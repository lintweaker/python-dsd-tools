#!/usr/bin/env python

# playdsd.py - Native DSD playback for DSD files
# Uses DSD_U32_BE sample format
# (c) 2014 Jurgen Kramer
# License: GPLv2
#
# v0.2 10-Sept-14 Jurgen Kramer
# Initial version
# v0.3 12-Sept-14 Jurgen Kramer
# First attempt at actually playing DSDIFF files
# v0.3 12-Sept-14 Jurgen Kramer
# Further fine tuning
# v0.4 13-Sept-14 Jurgen Kramer
# v0.5 5-Oct-14 JK
# Use dsdlib.py
# 0.6 10-Oct-14 JK
# Implemented DSF playback
# v0.7 12-Nov-14 JK
# Switch to new rate functions
# v0.7 28-Nov-14 JK
# Switch to DSD BE sample format
# v0.7thf 29-Aug-15 Dariusz Garbowski
# Fix ALSA device initialisation
# [typo] Fix comment: which sample format playdsd.py uses

import os.path
import re
import sys, getopt, struct
import signal

# Make sure alsaaudio module is available
try:
 import alsaaudio
except:
	print "Failed to import 'alsaudio'"
	sys.exit (1)

# Load dsdlib
try:
 import dsdlib
except:
	print "Failed to load 'dsdlib'"
	sys.exit (1)

#-- Functions
def signal_handler(signal, frame):
	print("CTRL-C pressed")
	sys.exit(0)

# Test for needed sample format support
def dsdformat():
	try:
		audiofmt = alsaaudio.PCM_FORMAT_DSD_U32_BE
		return 0
	except:
		return 1

#
def checkstream(streamfile):
	f = open(streamfile, 'r')
	if not f:
		f.close()
		return 2	# Problems reading stream0 file
	# Loop through lines of stream0 file
	for line in f:
		line = line.replace("\n", "")
		matchObj = re.search( r'DSD_U32_BE', line, re.M|re.I)
		if matchObj:
			#print "match!", matchObj.group()
			return 0
	return 3

# Test card for native DSD support using the DSD_U32_BE sample format, only available for USB sound cards
def checkdsd(card):
	cardpath = "/proc/asound/" + card
	streampath = cardpath + "/stream0"
	if os.path.exists(cardpath):
		#print "path ok for %s" % cardpath
		if os.path.isfile(streampath):
			# USB device, check for DSD_U32_BE support
			return checkstream(streampath)
		else:
			# Not a USB card"
			return 1
	else:
		#print "Path not ok for %s" % cardpath
		return 2
	return 0

# Walk through available sound cards and check DSD_U32_BE sample format support
# This only works for USB based soundcards
def checksndcards():
	cards = alsaaudio.cards()
	nrcards = len(cards)
	if nrcards == 0:
		return nrcards

	print "\nAvailable sound cards:\n"
	for i in range(0, nrcards):
		if len(cards[i]) < 6:
			print "'%s'\t\t:" % cards[i],
		else:
			print "'%s'\t:" % cards[i],
		dsd = checkdsd(cards[i])
		if dsd == 0:
			print "USB device with native DSD support"
		elif dsd == 1:
			print "Not a (UAC2) USB sound card"
		elif dsd == 2:
			print "No proc entry for '%s'" % cards[i]
		elif dsd == 3:
			print "USB device, no native DSD support"
		else:
			print "Unhandled value '%d' " % dsd
			exit (1)
	print ""

# dsdxmos
# Convert input DSDIFF DSD data to correct order for XMOS native DSD playback
def dsdxmos(size, indata, outdata):

	for i in range(0, size, 8):
		outdata[i+0x00] = indata[i+0x01]
		outdata[i+0x01] = indata[i+0x03]
		outdata[i+0x02] = indata[i+0x05]
		outdata[i+0x03] = indata[i+0x07]

		outdata[i+0x04] = indata[i+0x00]
		outdata[i+0x05] = indata[i+0x02]
		outdata[i+0x06] = indata[i+0x04]
		outdata[i+0x07] = indata[i+0x06]

	outdata = str(outdata)

	return outdata

# revbits
# Reverse bits if needed for DSF
def revbits(x):
	x = ((x & 0x55) << 1) | ((x & 0xaa) >> 1)
	x = ((x & 0x33) << 2) | ((x & 0xcc) >> 2)
	x = ((x & 0x0f) << 4) | ((x & 0xf0) >> 4)
	return x

# dsfxmos
# Convert input DSF DSD data to correct order for XMOS native DSD playback
def dsfxmos(size, indata, outdata, lsbfirst):

	if lsbfirst == 1:

		j = 0
		for i in range(0, size, 8):
			outdata[i+0x00] = revbits(indata[j+0x00])
			outdata[i+0x01] = revbits(indata[j+0x01])
			outdata[i+0x02] = revbits(indata[j+0x02])
			outdata[i+0x03] = revbits(indata[j+0x03])
			j += 4
		j = 0
		for i in range(0, size, 8):
			outdata[i+0x04] = revbits(indata[j+4096+0x00])
			outdata[i+0x05] = revbits(indata[j+4096+0x01])
			outdata[i+0x06] = revbits(indata[j+4096+0x02])
			outdata[i+0x07] = revbits(indata[j+4096+0x03])
			j += 4

	else:
		j = 0
		for i in range(0, size, 8):
			outdata[i+0x00] = indata[j+0x00]
			outdata[i+0x01] = indata[j+0x01]
			outdata[i+0x02] = indata[j+0x02]
			outdata[i+0x03] = indata[j+0x03]
			j += 4
		j = 0
		for i in range(0, size, 8):
			outdata[i+0x04] = indata[j+4096+0x00]
			outdata[i+0x05] = indata[j+4096+0x01]
			outdata[i+0x06] = indata[j+4096+0x02]
			outdata[i+0x07] = indata[j+4096+0x03]
			j += 4	

	outdata = str(outdata)

	return outdata

# playdsdsilence
# Play DSD silence data
# Input: dsdfile, nr of ms to play
def playdsdsilence(myfile, ms):
	#print "Requested %d ms of DSD silence playback" % ms
	silsize = ms * myfile.rate / 1000
	#print "Size for silence data = %d" % silsize
	sildata = bytearray(silsize)
	for i in range(0, silsize):
		sildata[i] = 0x69
	sildata = str(sildata)
	out.write(sildata)

def usage(errstring):
	if errstring != "":
		print errstring
	print "\nUsage:\n"
	print "\tPlay a DSD DSDIFF file:"
	print "\tplaydsd.py -c <audiocard> -f <file>"
	print "\n\tList usable audio cards:"
	print "\tplaydsd.py -l\n"

#-- Main
audiodev = ''
audiofile = ''
argv = sys.argv[1:]

# Check if the python-alsaaudio is updated with DSD sample format support
if dsdformat() != 0:
	print "Your python-alsaaudio installation does not support the needed DSD sample format"
	exit (1)

try:
	opts, args = getopt.getopt(argv,"hlc:f:",["card=","file=", "list"])
	#print "Opts = %s" % opts
	#print "Args = %s" % args
	if len(opts) == 0 and len(args) == 0:
		usage("No arguments given")
		sys.exit(2)

except getopt.GetoptError:
	usage("Wrong arguments given")
	sys.exit(2)
for opt, arg in opts:
	if opt == '-h':
		usage("")
		sys.exit(1)
	elif opt in ("-c", "--card"):
		audiodev = arg
	elif opt in ("-f", "--file"):
		audiofile = arg
		#print "Arg for file is %s" % arg
		if arg == "":
			print "Missing filename for -f option"
			sys.exit(1)
	elif opt in ("-l", "--list"):
		checksndcards()
		sys.exit(0)
		
if audiodev == "":
	usage("Missing audio device")
	sys.exit(1)
if audiofile == "":
	usage("Missing file name")
	sys.exit(1)

print "Chosen audio device is: '%s'" % audiodev
print "File to play: '%s'" % audiofile

# Check if the chosen card supports native DSD playback
res = checkdsd(audiodev)
if res == 1:
	print "\n'%s' is not a (UAC2) USB device" % audiodev
	checksndcards()
	exit (1)
elif res == 2:
	print "\nAudio card '%s' does not exist." % audiodev
	checksndcards()
	exit (1)
elif res == 3:
	print "\nSorry, '%s' is a USB sound card without native DSD support" % audiodev
	checksndcards()
	exit (1)
elif res != 0:
	print "Res is %d" % res
	exit (1)

# Install signal handler
signal.signal(signal.SIGINT, signal_handler)

# Check if given file exists and is readable

# Check if file to play is a proper DSDIFF or DSF file.
# If so, get its properties
myfile = dsdlib.dsdfile()
ret = dsdlib.checkdsdfile(audiofile, myfile)

#print "Got: myfile.valid = %d, myfile.type = %s" % (myfile.valid, myfile.type)

if myfile.valid == 2:
	print "Not a DSD file"
	sys.exit(1)

dsdtype = myfile.type
valid = myfile.valid
rate = myfile.rate
channels = myfile.channels

if valid == 0 and (dsdtype != 'dsdiff' and dsdtype != 'dsf'):
	print "Unsupported or invalid DSD file"
	sys.exit(1)

if valid == 0 and (dsdtype == 'dsdiff' or dsdtype == 'dsf'):
	print "Invalid %s file" % dsdtype.upper()
	sys.exit(1)

if dsdtype == "dsdiff" and myfile.compress == 1:
	print "This DSDIFF file uses compressed DSD data samples, playback is not supported"
	sys.exit(1)

if channels != 2:
	print "Sorry, only 2 channel (stereo) files are supported"
	sys.exit(1)

print "DSD file type: %s" % dsdtype.upper()
print "channels = %d" % channels
print "rate = %d Hz [%s]" % (rate, dsdlib.rate_to_string(rate))
print "Total file size: %d" % myfile.fsize
print "DSD data start at: %d" % myfile.datastart
print "DSD data size: %d" % myfile.datasize

# Open file
f = open(audiofile, 'rb')
# Seek to start of DSD data
f.seek(myfile.datastart)

# Setup ALSA
try:
	out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, card="front:CARD='%s',DEV=0" % audiodev)
except Exception as e:
	print "\nError: Cannot play, %s\n" % e
	sys.exit(1)

out.setchannels(2)
out.setrate(myfile.rate/8/4)
out.setformat(alsaaudio.PCM_FORMAT_DSD_U32_BE)
out.setperiodsize(11025)

# Start with a few ms of DSD silence data
playdsdsilence(myfile, 10)

if myfile.type == "dsdiff":
	# DSDIFF playback	

	# Play!
	print "Playing '%s' using card '%s'" % (audiofile, audiodev)
	rdsize=320

	data = f.read(rdsize)
	newdata = bytearray(rdsize)

	# Convert first block of DSD data
	newdata = dsdxmos(rdsize, data, newdata)
	datasize = myfile.datasize - rdsize
	remain = datasize

	while data:
		out.write(newdata)

		remain -= rdsize	
		if remain < rdsize:
			print "Nearing the end, todo: %d" % remain
			rdsize = remain

		data = f.read(rdsize)
		newdata = bytearray(rdsize)

		newdata = dsdxmos(rdsize, data, newdata)

# DSF playback
else:
	rdsize = 8192
	data = f.read(rdsize)
	data = bytearray(data)
	newdata = bytearray(data)

	# Convert first block of DSD data
	newdata = dsfxmos(rdsize, data, newdata, myfile.lsbfirst)
	datasize = myfile.datasize - rdsize
	remain = datasize

	while data:
		out.write(newdata)
		remain -= rdsize

		if remain < rdsize:
			print "DSF: nearing the end, todo: %d" % remain
			rdsize = remain
		data = f.read(rdsize)
		data = bytearray(data)
		newdata = bytearray(rdsize)

		newdata = dsfxmos(rdsize, data, newdata, myfile.lsbfirst)


# Play a few ms of DSD silence at the end
playdsdsilence(myfile, 10)

f.close()
sys.exit(0)
