#!/usr/bin/env python

# dsdlib.py
# Set of functions for testing and playing DSD (DSDIFF and DSF) files
# (c) 2014 Jurgen Kramer
# License: GPLv2
#
# version 0.1 9-sep-14 Jurgen Kramer
# First initial version
# v0.2 13-Sept-14 Jurgen Kramer
# Now loops through all main chunks
# TODO: handle sub chunks
# v0.3 15-Sept-14 Jurgen Kramer
# Handle local property ('PROP') chunks, FVER version check
# v0.3 05-Oct-14 Jurgen Kramer
# Start conversion for usage as DSD library functions dsdlib.py
# v0.4 07-Oct-14 Jurgen Kramer
# Add support for DSF
# v0.5 08-Nov-14 Jurgen Kramer
# Pythonize a bit
# v0.6 12-Nov-14 Jurgen Kramer
# Rework rate check/display functions

#from struct import unpack, calcsize
import struct
import sys
from ctypes import *

dsdiff_data = {
	'basic' : '>4s',
	'frm8' : '>4s1Q4s',
	'fver' : '>1L',
	'prop' : '>4s',
	'rate' : '>1L',
	'chan' : '>1H',
	'chandes' : '>4s',
	'cmp' : '>4s1B',
	'cmpstr' : '>1s',
	'abbs' : '>1H1B1B1L',
	'spkr' : '>1H',
	'data' : '>4s1Q',
	'dsd_chunk' : '>4s1Q'
}

length = {}
unpacked = {}

for x in dsdiff_data:
	length[x] = struct.calcsize(dsdiff_data[x])
	unpacked[x] = struct.Struct(dsdiff_data[x]).unpack_from


dsf_data = {
	'hdr' : '<4sQ1Q1Q1',
	'fmt' : '<4sQ1L1L1L1L1L1L1Q1L1L1',
	'data' : '<4s1Q',
	'meta' : '<3s'
}

dsf_length = {}
dsf_unpacked = {}

for x in dsf_data:
	dsf_length[x] = struct.calcsize(dsf_data[x])
	dsf_unpacked[x] = struct.Struct(dsf_data[x]).unpack_from

# dsdfile, store useful info of a DSD file
#
# dsdinfo.type		- "dsdiff" or "dsf"
# dsdfile.valid		- file is valid DSD file: 0 = yes, 1 = no, 2 = not a DSD file
# dsdinfo.confedence	- 4 for a valid dsdiff file
# dsdinfo.version	-
# dsdinfo.channels	-
# dsdinfo.rate		- sample rate in Hz
# dsdinfo.fsize		- total filesize
# dsdinfo.datasize	-
# dsdinfo.datastart	-
# dsdfile.id3tag	-
# dsdfile.id3len	-
# dsdfile.lsbfirst	- 1 = LSB first, bit reverse needed
# dsdfile.curpos	-

class dsdfile(Structure):
	_fields_ = [
			('type', 6*c_char),
			('valid', c_byte),
			('confedence', c_ushort),
			('version', c_ulong),
			('compress', c_bool),
			('channels', c_byte),
			('rate', c_ulong),
			('fsize', c_longlong),
			('datasize', c_longlong),
			('datastart', c_longlong),
			('id3tag', c_longlong),
			('id3len', c_longlong),
			('lsbfirst', c_ushort,),
			('curpos', c_longlong)
		]

#-- Functions
def wrongfile(marker):
	print "Not a DSDIFF file! Error at '%s' marker" % marker
	sys.exit(1)

# getfiletype
def getfiletype(filename, dsdfile):

	# Mark file as non DSD file by default
	dsdfile.valid = 2
	dsdfile.type = 'none'

	results = []
	with open(filename, "rb") as f:

		data = f.read(length['basic'])
		s = unpacked['basic'](data)
		results.append(s)
		chunk_id = results[0][0]			# Should be 'FRM8' or 'DSD '

	f.close()

	if chunk_id == 'FRM8':
		# Mark file as potential DSDIFF
		dsdfile.valid = 0
		dsdfile.type = 'dsdiff'
		return dsdfile

	if chunk_id == 'DSD ':
		# Mark file as potential DSF
		dsdfile.valid = 0
		dsdfile.type = 'dsf'
		return dsdfile

	# Not a DSD file
	return dsdfile

# getmaxdsd
# Returns max supported DSD rate. DSD64 = 1, DSD128 = 2, etc
#
def getmaxdsd():
	# Max DSD512
	return 4

# dsd_valid_rate
# Check if given rate is a valid DSD rate
#
def dsd_valid_rate(rate):

	maxdsdrate = getmaxdsd()
	dsdrate = []

	if rate % 44100 == 0:

		dsdrates = set(get_dsd_rates(maxdsdrate, 44100))
		if rate in dsdrates:
			return True
		else:
			return False

	if rate % 48000 == 0:

		dsdrates = set(get_dsd_rates(maxdsdrate, 48000))
		if rate in dsdrates:
			return True
		else:
			return False

	return False

# valid_base_rate
# Check if the given rate is has a valid DSD base rate (44k1/48k)
#
def valid_base_rate(rate):

	if rate % 44100 == 0 or rate % 48000 == 0:
		return True
	return False

# get_dsd_rates
# Get all rates based on given base (44k1/48k) rate
def get_dsd_rates(maxdsdrate, base):

	dsd_base_rate = base*64
	max_dsd = getmaxdsd()
	rates = []

	if base != 44100 and base != 48000:
		return rates

	for x in range(0, max_dsd):
		rates.append(dsd_base_rate)
		dsd_base_rate *= 2
	return rates

# rate_to_string
# Convert rate to "DSD64", "DSD128" etc moniker
def rate_to_string(rate):

	if not valid_base_rate(rate):
		return "DSD?? invalid DSD rate"

	rate_strings = {}
	base = 44100
	maxdsdrate = getmaxdsd()

	if rate % 48000 == 0:
		base = 48000
	rates = get_dsd_rates(maxdsdrate,base)

	y = 0
	for x in rates:
		dsdstr = "DSD" + str(rates[y]/base)
		if base == 48000:
			dsdstr += ", fs=48kHz"
		rate_strings[rates[y]] = dsdstr
		y += 1

	if rate in rate_strings:
		return rate_strings[rate]
	else:
		return "DSD??"

# DSDIFF Handle local chunks of property chunk
def handle_prop_local_chunks(size, handle, dsdfile):
	ret = 0
	curpos = handle.tell()
	maxpos = curpos + size
	#print "Property local chunks, total size is %d , cur pos = %d" % (size, curpos)
	props = []
	propdata = handle.read(length['prop'])
	s = unpacked['prop'](propdata)
	props.append(s)
	chunk_id = props[0][0]					# Should be 'SND '
	if chunk_id == 'SND ':

		while curpos < maxpos:
			# Read next chunk ID + chunk size
			propdata = handle.read(length['data'])
			s = unpacked['data'](propdata)
			props.append(s)

			chunk_id = props[1][0]
			chunk_size = props[1][1]

			# Sample Rate Chunk
			if chunk_id == 'FS  ':
				#print "Sample Rate Chunk"
				props = []
				propdata = handle.read(length['rate'])
				s = unpacked['rate'](propdata)
				props.append(s)
				rate = props[0][0]
				#print "Sample rate: %d Hz" % rate
				if not dsd_valid_rate(rate):
					return -1
				dsdfile.rate = rate
				ret += 1
				curpos = handle.tell()
				continue

			# Channels Chunk
			if chunk_id == 'CHNL':
				#print "Channels Chunk"
				props = []
				propdata = handle.read(length['chan'])
				s = unpacked['chan'](propdata)
				props.append(s)
				channels = props[0][0]
				#print "File has %d channels" % channels
				dsdfile.channels = channels
				for i in range(0, channels):
					props = []
					propdata = handle.read(length['chandes'])
					s = unpacked['chandes'](propdata)
					props.append(s)
					chandes = props[0][0]
					#print "Channel: %s" % chandes
				ret += 1
				curpos = handle.tell()
				continue
					
			# Compression Type Chunk
			if chunk_id == 'CMPR':
				#print "Compression Type Chunk"
				props = []
				propdata = handle.read(length['cmp'])
				s = unpacked['cmp'](propdata)
				props.append(s)
				cmptype = props[0][0]
				cmplen = props[0][1]
				#print "Compression type: '%s'" % cmptype
				if cmptype == 'DSD ':
					dsdfile.compress = 0
				else:
					dsdfile.compress = 1

				#print "Compression string length: %d" % cmplen
				for i in range(0, cmplen+1):
					propdata = handle.read(length['cmpstr'])
					s = unpacked['cmpstr'](propdata)
					#print "%s" % s,
					
				ret += 1
				curpos = handle.tell()
				#print "POS is %d" % curpos
				continue

			if chunk_id == 'ABSS':				# Optional
				#print "Absolute Start Time Chunk"
				#print "Size %d" % chunk_size
				props = []
				propdata = handle.read(length['abbs'])
				s = unpacked['abbs'](propdata)
				props.append(s)
				hrs = props[0][0]
				mins = props[0][1]
				secs = props[0][2]
				samples = props[0][3]
				#print "Offset: %d hrs, %d mins, %d secs and %d samples " %(hrs, mins, secs, samples)

				curpos = handle.tell()
				continue

			if chunk_id == 'LSCO':				# Optional
				#print "Loudspeaker Configuration Chunk"
				if chunk_size != 2:
					#print "Illegal chunk size %d" % chunk_size
					ret = -1
					return ret

				props = []
				propdata = handle.read(length['spkr'])
				s = unpacked['spkr'](propdata)
				props.append(s)
				spkrcfg = props[0][0]
				#print "Speaker config is: %d" % spkrcfg
				curpos = handle.tell()
				continue

		#print "Done with while loop, ret = %d" % ret
		# Save current position in the DSD file
		dsdfile.curpos = curpos
		return ret

	else:
		#print "Illegal/wrong chunk id '%s' " % chunk_id
		ret = -1
		return ret

# check_dsdiff
# Check if the given file is a proper DSDIFF file
def check_dsdiff(filename, dsdfile):

	results = []
	confedence = 0
	neededconf = 4
	id3tag = 0

	with open(filename, "rb") as f:

		# Read header of the file and check for the needed DSDIFF ID's
		data = f.read(length['frm8'])
		s = unpacked['frm8'](data)
		results.append(s)
		chunk_id = results[0][0]				# Should be 'FRM8'
		dsd_file_size = results[0][1]
		dsd_id = results[0][2]					# Should be 'DSD '

		if chunk_id != 'FRM8':
			# Mark file as invalid
			dsdfile.valid = 0
			return dsdfile
			#wrongfile('FRM8')

		if dsd_id != 'DSD ':
			# Mark file as invalid
			dsdfile.valid = 0
			return dsdfile
			#wrongfile('DSD ')

		confedence += 1
		dsdfile.fsize = dsd_file_size

		# Loop through all the remaining chunks
		while True:
			results = []
			data = f.read(length['dsd_chunk'])
			if not data: break
			s = unpacked['dsd_chunk'](data)
			results.append(s)
			chunk_id = results[0][0]
			chunk_size = results[0][1]

			if chunk_id == 'FVER':
				results = []
				data = f.read(length['fver'])
				s = unpacked['fver'](data)
				results.append(s)
				version = results[0][0]
				if version != 0x1050000 and version != 0x1040000:
					#print "Illegal/unsupported version 0x%06x" % version
					dsdfile.valid = 0
					break
				confedence += 1

				pos = f.tell()
				seekpos = pos
				continue

			if chunk_id == 'DSD ' or chunk_id == 'DST ':
				dsdfile.datastart = f.tell()
				dsdfile.datasize = chunk_size
				confedence += 1

			if chunk_id == 'PROP':
				ret = handle_prop_local_chunks(chunk_size, f,dsdfile)

				if ret == -1:
					# Mark file as invalid
					dsdfile.valid = 0
					break
				if ret != 3:
					#print "Missing required local chunks in property chunk"
					# Mark file as invalid
					dsdfile.valid = 0
					break

				confedence += 1
				#pos = f.tell()
				seekpos = dsdfile.curpos
				
			else:
				# Seek to next chunk
				pos = f.tell()
				seekpos = pos + chunk_size
				# Check if this was the last chunk
				if seekpos > dsd_file_size:
					break
			
			f.seek(seekpos)
			#print "\nFile pos now at\t\t: %d" % f.tell()

		f.close()
		dsdfile.confedence = confedence

		if confedence < neededconf:
			# Mark file as invalid
			dsdfile.valid = 0
		else:
			# Mark file as valid
			dsdfile.valid = 1
			#if id3tag == 0:
			#	print "This is a properly formatted DSDIFF file"
			#else:
			#	print "This is a properly formatted DSDIFF file with unofficial ID3 tag"

			# TODO: store id3tag length
		
		return dsdfile

# check_dsf
# Check if the given file is a proper DSD DSF formatted file
def check_dsf(filename, dsdfile):

	results = []
	dsdfile.valid = 0
	confedence = 0
	dsdfile.lsbfirst = 0
	dsdfile.id3tag = 0

	with open(filename, "rb") as f:

		# Read header of the file and check for the needed DSF ID
		data = f.read(dsf_length['hdr'])
		s = dsf_unpacked['hdr'](data)
		results.append(s)
		chunk_id = results[0][0]		# Should be 'DSD '

		if chunk_id != 'DSD ':
			return dsdfile

		chunk_size = results[0][1]		# Size should be 28
		if chunk_size != 28:
			#print "Wrong chunk size: %d" % chunk_size
			return dsdfile

		confedence += 1

		file_size = results[0][2]
		dsdfile.fsize = file_size
		#print "Total file size\t\t\t: %d" % file_size

		id3_chunk_offset = results[0][3]
		if id3_chunk_offset != 0:
			dsdfile.id3tag = id3_chunk_offset

		# Read the fmt chunk
		results = []
		data = f.read(dsf_length['fmt'])
		s = dsf_unpacked['fmt'](data)
		results.append(s)

		chunk_id = results[0][0]		# Should be 'fmt '
		if chunk_id != 'fmt ':
			return dsdfile

		chunk_size = results[0][1]		# Size should be 52
		if chunk_size != 52:
			return dsdfile

		confedence += 1

		dsf_version = results[0][2]		# Should be 1
		if dsf_version != 1:
			return dsdfile

		dsf_format_id = results[0][3]		# Should be 0
		if dsf_format_id != 0:
			return dsdfile

		confedence += 1

		dsf_chan_type = results[0][4]
		if dsf_chan_type == 0 or dsf_chan_type > 7:
			return dsdfile
		else:
			if dsf_chan_type == 1:
				spkr_setup = "Mono"
			if dsf_chan_type == 2:
				spkr_setup = "Stereo"
			if dsf_chan_type == 3:
				spkr_setup = "3 channels"
			if dsf_chan_type == 4:
				spkr_setup = "Quad"
			if dsf_chan_type == 5:
				spkr_setup = "4 channels"
			if dsf_chan_type == 6:
				sprk_setup = "5 channels"
			if dsf_chan_type == 7:
				spkr_setup == "5.1 channels"

		dsf_chan_num = results[0][5]
		if dsf_chan_num == 0 or dsf_chan_num > 7:
			return dsdfile

		dsdfile.channels = dsf_chan_num

		dsf_rate = results[0][6]
		if not dsd_valid_rate(dsf_rate):
			return dsdfile
		dsdfile.rate = dsf_rate

		dsf_sample_bits = results[0][7]
		if dsf_sample_bits == 1:
			dsdfile.lsbfirst = 1

		dsf_sample_count = results[0][8]

		dsf_block_size = results[0][9]
		if dsf_block_size != 4096:
			return dsdfile

#		dsf_reserved = results[0][10]
#		if dsf_reserved != 0:
#			print "Reserved\t\t\t: %d [Should be 0]" % dsf_reserved

		confedence += 1

		# Read chunk header of 'data' chunk
		results = []
		data = f.read(dsf_length['data'])
		s = dsf_unpacked['data'](data)
		results.append(s)

		chunk_id = results[0][0]
		if chunk_id != 'data':
			return dsdfile

		dsdfile.datastart =  f.tell()

		chunk_size = results[0][1]
		chunk_size -= 12
		#print "Chunk size (samples)\t\t: %d" % chunk_size

		playable_size = dsf_chan_num * dsf_sample_count / 8

		if chunk_size > playable_size:
			dsdfile.datasize = playable_size
		else:
			dsdfile.datasize = chunk_size

		# Read metadata chunk
		if id3_chunk_offset != 0:
			f.seek(id3_chunk_offset)

		results = []
		data = f.read(dsf_length['meta'])
		s = dsf_unpacked['meta'](data)
		results.append(s)

		chunk_id = results[0][0]
		if chunk_id != 'ID3':
			dsdfile.id3tag = 0

		# TODO: store id3tag length

		confedence += 1

	f.close()

	# Mark DSF file as valid
	dsdfile.valid = 1
	dsdfile.confedence = confedence

	return dsdfile

# checkdsdfile()
# Input: filename to test on
# Return: structure
def checkdsdfile(filename, dsdfile):

	# Test readability of given filename

	# Read first basic header to determine if it is potentially a DSD file
	getfiletype(filename, dsdfile)
	if dsdfile.type == 'none':
		#print ">>>> Not a DSD file"
		return dsdfile
	if dsdfile.type == 'dsf':
		check_dsf(filename, dsdfile)
	else:
		# File is potentially a DSDIFF file
		check_dsdiff(filename, dsdfile)
	
	return dsdfile


