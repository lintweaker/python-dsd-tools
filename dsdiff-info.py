#!/usr/bin/env python

# dsdiff-check-all-chunks.py
# Test DSDIFF DSD files (.dff) loop through all chunks
# prints out all DSDIFF chunk data structure info
# Standalone version, does not use dsdlib.py
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
# v0.4 05-Oct-14 Jurgen Kramer
# Accept 0x1040000 as a valid version for DSDIFF (minimum version should be 0x1050000)
# v0.5 11-Mar-16 Jurgen Kramer
# Add check if file could hang MPD at the end of the file (sample data size not dividable by 4 bug)
# Adjust print statements to new style
# Additional compression info

from __future__ import print_function

import struct
import sys

# Form DSD Chunk
struct_frm8_fmt = '>4s1Q4s'
struct_frm8_len = struct.calcsize(struct_frm8_fmt)
struct_unpack_frm8 = struct.Struct(struct_frm8_fmt).unpack_from

# Format Version Chunk
struct_fver_fmt = '>1L'
struct_fver_len = struct.calcsize(struct_fver_fmt)
struct_unpack_fver = struct.Struct(struct_fver_fmt).unpack_from

# Property Chunk
struct_prop_fmt = '>4s'
struct_prop_len = struct.calcsize(struct_prop_fmt)
struct_unpack_prop = struct.Struct(struct_prop_fmt).unpack_from

# Sample Rate Chunk
struct_rate_fmt = '>1L'
struct_rate_len = struct.calcsize(struct_rate_fmt)
struct_unpack_rate = struct.Struct(struct_rate_fmt).unpack_from

# Channels Chunk
struct_chan_fmt = '>1H'
struct_chan_len = struct.calcsize(struct_chan_fmt)
struct_unpack_chan = struct.Struct(struct_chan_fmt).unpack_from

# Channel descriptions
struct_chandes_fmt = '>4s'
struct_chandes_len = struct.calcsize(struct_chandes_fmt)
struct_unpack_chandes = struct.Struct(struct_chandes_fmt).unpack_from

# Compression Type Chunk
struct_cmp_fmt = '>4s1B'
struct_cmp_len = struct.calcsize(struct_cmp_fmt)
struct_unpack_cmp = struct.Struct(struct_cmp_fmt).unpack_from

# Compression name
struct_cmpstr_fmt = '>1s'
struct_cmpstr_len = struct.calcsize(struct_cmpstr_fmt)
struct_unpack_cmpstr = struct.Struct(struct_cmpstr_fmt).unpack_from

# Absolute Start Time Chunk
struct_abbs_fmt = '>1H1B1B1L'
struct_abbs_len = struct.calcsize(struct_abbs_fmt)
struct_unpack_abbs = struct.Struct(struct_abbs_fmt).unpack_from

# Loudspeaker Configuration Chunk
struct_spkr_fmt = '>1H'
struct_spkr_len = struct.calcsize(struct_spkr_fmt)
struct_unpack_spkr = struct.Struct(struct_spkr_fmt).unpack_from

# DSD Sound Data Chunk
struct_dsd_fmt = '>4s1Q'
struct_dsd_len = struct.calcsize(struct_dsd_fmt)
struct_unpack_dsd = struct.Struct(struct_dsd_fmt).unpack_from

# Basis chunk, ID + chunk_size only
struct_dsd_chunk = '>4s1Q'
struct_dsd_chunk_len = struct.calcsize(struct_dsd_chunk)
struct_unpack_dsd_chunk = struct.Struct(struct_dsd_chunk).unpack_from


#-- Functions
def wrongfile(marker):
	print( "Not a DSDIFF file! Error at '%s' marker" % marker )
	sys.exit(1)

# Handle local chunks of property chunk
def handle_prop_local_chunks(size):
	ret = 0
	curpos = f.tell()
	maxpos = curpos + size
	#print "Property local chunks, total size is %d , cur pos = %d" % (size, curpos)
	props = []
	propdata = f.read(struct_prop_len)
	s = struct_unpack_prop(propdata)
	props.append(s)
	chunk_id = props[0][0]					# Should be 'SND '
	if chunk_id == 'SND ':

		while curpos < maxpos:
			# Read next chunk ID + chunk size
			propdata = f.read(struct_dsd_len)
			s = struct_unpack_dsd_chunk(propdata)
			props.append(s)

			chunk_id = props[1][0]
			chunk_size = props[1][1]

			# Sample Rate Chunk
			if chunk_id == 'FS  ':
				print( "Sample Rate Chunk" )
				props = []
				propdata = f.read(struct_rate_len)
				s = struct_unpack_rate(propdata)
				props.append(s)
				rate = props[0][0]
				print( "Sample rate: %d Hz" % rate )
				ret += 1
				curpos = f.tell()
				continue

			# Channels Chunk
			if chunk_id == 'CHNL':
				print( "Channels Chunk" )
				props = []
				propdata = f.read(struct_chan_len)
				s = struct_unpack_chan(propdata)
				props.append(s)
				channels = props[0][0]
				print( "File has %d channels" % channels )
				for i in range(0, channels):
					props = []
					propdata = f.read(struct_chandes_len)
					s = struct_unpack_chandes(propdata)
					props.append(s)
					chandes = props[0][0]
					print( "Channel: %s" % chandes )
				ret += 1
				curpos = f.tell()
				continue
					
			# Compression Type Chunk
			if chunk_id == 'CMPR':
				print( "Compression Type Chunk" )
				props = []
				propdata = f.read(struct_cmp_len)
				s = struct_unpack_cmp(propdata)
				props.append(s)
				cmptype = props[0][0]
				cmplen = props[0][1]
				compressed = "Not compressed"
				if cmptype != 'DSD ':
					compressed = " Compressed"
				print( "Compression type: '%s' (%s)" % ( cmptype, compressed ) )
				print( "Compression string length: %d" % cmplen )
				for i in range(0, cmplen+1):
					propdata = f.read(struct_cmpstr_len)
					s = struct_unpack_cmpstr(propdata)
					#print "%s" % s,
					
				ret += 1
				curpos = f.tell()
				#print "POS is %d" % curpos
				continue

			if chunk_id == 'ABSS':				# Optional
				print( "Absolute Start Time Chunk" )
				print( "Size %d" % chunk_size )
				props = []
				propdata = f.read(struct_abbs_len)
				s = struct_unpack_abbs(propdata)
				props.append(s)
				hrs = props[0][0]
				mins = props[0][1]
				secs = props[0][2]
				samples = props[0][3]
				print( "Offset: %d hrs, %d mins, %d secs and %d samples " %(hrs, mins, secs, samples) )

				curpos = f.tell()
				continue

			if chunk_id == 'LSCO':				# Optional
				print( "Loudspeaker Configuration Chunk" )
				if chunk_size != 2:
					print( "Illegal chunk size %d" % chunk_size )
					ret = -1
					return ret

				props = []
				propdata = f.read(struct_spkr_len)
				s = struct_unpack_spkr(propdata)
				props.append(s)
				spkrcfg = props[0][0]
				print( "Speaker config is: %d" % spkrcfg )
				curpos = f.tell()
				continue

		return ret

	else:
		ret = -1
		return ret
	

#-- Main

#filename = "/home/kramer/edited-dsd.dff"
#print "ARGS: %d" % len(sys.argv)

# Check command line arguments
if len(sys.argv) <= 1:
	print( "Missing filename to test on" )
	sys.exit(1)

filename = sys.argv[1]

print( "\nResults for file\t: %s\n" % filename )

results = []
confedence = 0
neededconf = 4
id3tag = 0
could_trigger_mpd_hang = False


with open(filename, "rb") as f:

	# Read header of the file and check for the needed DSDIFF ID's
	data = f.read(struct_frm8_len)
	s = struct_unpack_frm8(data)
	results.append(s)
	chunk_id = results[0][0]				# Should be 'FRM8'
	dsd_file_size = results[0][1]
	dsd_id = results[0][2]					# Should be 'DSD '

	if chunk_id != 'FRM8':
		wrongfile('FRM8')

	if dsd_id != 'DSD ':
		wrongfile('DSD ')

	confedence += 1

	print( "Found start chunk\t: '%s'" % chunk_id )
	print( "Total file size\t\t: %d" % dsd_file_size )

	print( "\nFile pos now at\t\t: %d" % f.tell() )

	# Loop through all the remaining chunks
	while True:
		results = []
		data = f.read(struct_dsd_chunk_len)
		if not data: break
		s = struct_unpack_dsd_chunk(data)
		results.append(s)
		chunk_id = results[0][0]
		chunk_size = results[0][1]

		print( "Found chunk with id\t: '%s'" % chunk_id )
		print( "Chunk size\t\t: %d" % chunk_size )

		if chunk_id == 'FVER':
			results = []
			data = f.read(struct_fver_len)
			s = struct_unpack_fver(data)
			results.append(s)
			version = results[0][0]
			#print "FVER: version 0x%06x " % version
			if version != 0x1050000 and version != 0x1040000:
				print( "Illegal/unsupported version 0x%06x" % version )
				break
			confedence += 1

			pos = f.tell()
			seekpos = pos
			#print "POS is: %d" % pos
			continue

		if chunk_id == 'DSD ' or chunk_id == 'DST ':
			print( "DSD sample data starts at: %d" % f.tell() )
			confedence += 1
			# Test if this file can trigger MPD hang bug
			if chunk_id == 'DSD ' and chunk_size % 4 != 0:
				could_trigger_mpd_hang = True

		if chunk_id == 'PROP':
			ret = handle_prop_local_chunks(chunk_size)
			if ret == -1:
				print( "Problems with property chunk" )
				break
			if ret != 3:
				print( "Missing required local chunks in property chunk" )
				break

			confedence += 1
			pos = f.tell()
			seekpos = pos
		else:
			# Seek to next chunk
			pos = f.tell()
			seekpos = pos + chunk_size
			# Check if this was the last chunk
			if seekpos > dsd_file_size:
				break
		f.seek(seekpos)
		print( "\nFile pos now at\t\t: %d" % f.tell() )


	f.close()
	print( "\nConclusion\t\t: ", end='' )
	if confedence < neededconf:
		print( ">>This is not a properly DSDIFF formatted file<<" )
		print( "\t\t\t\tConfedence = %d, needs to be %d" % (confedence, neededconf) )
	else:
		if id3tag == 0:
			print( "This is a properly formatted DSDIFF file" )
		else:
			print( "This is a properly formatted DSDIFF file with unofficial ID3 tag" )
		if could_trigger_mpd_hang:
			print( "Warning\t\t\t: !!This file could hang MPD at the end of the song!!" )

	print ( "" )
	sys.exit(0)

