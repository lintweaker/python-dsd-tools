#!/usr/bin/env python

# dsf-info.py
# Test DSF DSD files (.dsf) and print out all info
# Standalone, does not use dsdlib.py
# (c) 2014 Jurgen Kramer
# License: GPLv2
#
# version 0.1 06-Oct-14 Jurgen Kramer
# Initial version
# version 0.2 24-Feb-24 JK
# Update for Python3

import struct
import sys


# DSF 'DSD ' chunk
struct_dsf_hdr = '<4s1Q1Q1Q'
struct_dsf_hdr_len = struct.calcsize(struct_dsf_hdr)
struct_unpack_dsf_hdr = struct.Struct(struct_dsf_hdr).unpack_from

# fmt chunk
struct_fmt_chunk = '<4s1Q1L1L1L1L1L1L1Q1L1L'
struct_fmt_chunk_len = struct.calcsize(struct_fmt_chunk)
struct_unpack_fmt_chunk = struct.Struct(struct_fmt_chunk).unpack_from

# data chunk
struct_data_chunk = '<4s1Q'
struct_data_chunk_len = struct.calcsize(struct_data_chunk)
struct_unpack_data_chunk = struct.Struct(struct_data_chunk).unpack_from

# metadata chunk
struct_meta_chunk = '<3s'
struct_meta_chunk_len = struct.calcsize(struct_meta_chunk)
struct_unpack_meta_chunk = struct.Struct(struct_meta_chunk).unpack_from

#-- Functions
def wrongfile(marker):
	print("Not a DSF file! Error at '%s' marker" % marker)
	sys.exit(1)

# Convert given rate to DSD64, DSD128 etc moniker
def dsdtype(rate):
	if rate % 44100 == 0:
		#print("File has fs = 44k1 base")
		if rate == 2822400:
			return "DSD64"
		if rate == 5644800:
			return "DSD128"
		if rate == 11289600:
			return "DSD256"
		if rate == 22579200:
			return "DSD512"
	if rate % 48000 == 0:
		#print("File has fs = 48k base")
		if rate == 3072000:
			return "DSD64, fs = 48kHz"
		if rate == 6144000:
			return "DSD128, fs = 48kHz"
		if rate == 12288000:
			return "DSD256, fs = 48kHz"
		if rate == 24576000:
			return "DSD512, fs = 48kHz"
	return "DSD??"

#-- Main

# Check command line arguments
if len(sys.argv) <= 1:
	print("Missing filename to test on")
	sys.exit(1)

filename = sys.argv[1]

print("\nResults for file\t\t: %s\n" % filename)

results = []

with open(filename, "rb") as f:

	# Read header of the file and check for the needed DSF ID
	data = f.read(struct_dsf_hdr_len)
	s = struct_unpack_dsf_hdr(data)
	results.append(s)
	chunk_id = results[0][0]		# Should be 'DSD '

	if chunk_id != b'DSD ':
		wrongfile('DSD ')

	print("DSF 'DSD ' chunk info:\n")

	chunk_size = results[0][1]		# Size should be 28
	if chunk_size != 28:
		print("Wrong chunk size: %d" % chunk_size)
		sys.exit(1)


	file_size = results[0][2]
	print("Total file size\t\t\t: %d" % file_size)

	id3_chunk_offset = results[0][3]
	if id3_chunk_offset == 0:
		print("ID3v2 chunk offset\t\t: No ID3v2 tag")
	else:
		print("ID3v2 chunk offset\t\t: %d" % id3_chunk_offset)

	# Read the fmt chunk
	results = []
	data = f.read(struct_fmt_chunk_len)
	s = struct_unpack_fmt_chunk(data)
	results.append(s)

	chunk_id = results[0][0]		# Should be 'fmt '
	if chunk_id != b'fmt ':
		wrongfile('fmt ')

	print("\nDSF 'fmt ' chunk info:\n")

	chunk_size = results[0][1]		# Size should be 52
	if chunk_size != 52:
		print("Wrong chunk size: %d" % chunk_size)
		sys.exit(1)

	dsf_version = results[0][2]		# Should be 1
	if dsf_version != 1:
		print("DSF version\t\t\t: %d [Unknown version]" % dsf_version)
		print("-- the results might not be correct --")
	else:
		print("DSF version\t\t\t: %d" % dsf_version)

	dsf_format_id = results[0][3]		# Should be 0
	if dsf_format_id != 0:
		print("Format ID\t\t\t: %d [Unsupported]" % dsf_format_id)
	else:
		print("Format ID\t\t\t: %d [DSD raw]" % dsf_format_id)

	dsf_chan_type = results[0][4]
	if dsf_chan_type == 0 or dsf_chan_type > 7:
		print("Channel type\t\t\t: %d [Unsupported]" % dsf_chan_type)
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

		print("Channel type\t\t\t: %d [%s]" % (dsf_chan_type, spkr_setup))

	dsf_chan_num = results[0][5]
	if dsf_chan_num == 0 or dsf_chan_num > 7:
		print("Number of channels\t\t: %d [Unsupported]" % dsf_chan_num)
	else:
		print("Number of channels\t\t: %d" % dsf_chan_num)

	dsf_rate = results[0][6]
	dsdstr = dsdtype(dsf_rate)
	print("Sampling frequency\t\t: %d Hz [%s]" % (dsf_rate, dsdstr))

	dsf_sample_bits = results[0][7]
	if dsf_sample_bits == 8:
		print("Bits per sample\t\t\t: %d [MSB first]" % dsf_sample_bits)
	else:
		print("Bits per sample\t\t\t: %d [LSB first, bit reverse needed]" % dsf_sample_bits)

	dsf_sample_count = results[0][8]
	print("1-bit sample count (per channel): %d" % dsf_sample_count)

	dsf_block_size = results[0][9]
	if dsf_block_size == 4096:
		print("Block size per channel\t\t: %d" % dsf_block_size)
	else:
		print("Block size per channel\t\t: %d [Unsupported]" % dsf_block_size)

	dsf_reserved = results[0][10]
	if dsf_reserved != 0:
		print("Reserved\t\t\t: %d [Should be 0]" % dsf_reserved)

	# Read chunk header of 'data' chunk
	results = []
	data = f.read(struct_data_chunk_len)
	s = struct_unpack_data_chunk(data)
	results.append(s)

	chunk_id = results[0][0]
	if chunk_id != b'data':
		wrongfile('data')

	print("\nDSF 'data' chunk info:\n")

	print("Sample data starts at\t\t: %d" % f.tell())
	chunk_size = results[0][1]
	chunk_size -= 12
	print("Chunk size (samples)\t\t: %d" % chunk_size)

	if chunk_size != dsf_chan_num * dsf_sample_count:
		print("Number of fill samples\t\t: %d [calculated]" % (chunk_size - (dsf_chan_num * dsf_sample_count / 8)))

	# Read metadata chunk
	if id3_chunk_offset != 0:
		f.seek(id3_chunk_offset)

	results = []
	data = f.read(struct_meta_chunk_len)
	s = struct_unpack_meta_chunk(data)
	results.append(s)

	print("\nDSF 'metadata' chunk info:\n")

	chunk_id = results[0][0]
	if chunk_id == b'ID3':
		print("ID3 tag\t\t\t\t: OK (%s)" % chunk_id)
	else:
		print("No valid ID3 tag at offset %d" % id3_chunk_offset)

	print("\nDone")
	f.close()

