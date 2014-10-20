python-dsd-tools
================

Set of Python scripts for testing and playing DSD files. Mainly created to get
some hands on experience with Python.

**dsf-info.py**
Standalone script to test and show info for DSD DSF files

*Usage:*

`./dsf-info.py <path to DSF file>`

**dsdiff-info.py**

Standalone script to test DSD DSDIFF files and show relevant info.

*Usage:*

`./dsdiff-info.py <path to DSDIFF file>`

**playdsd.py**

Script to play DSD (DSF and DSDIFF) files using native DSD playback.
Uses dsdlib.py and requires updated pyalsaaudio, ALSA lib and kernel support.

*Usage:*

`./playdsd.py -l`

Show available sound cards and prints native DSD playback ability

`./playdsd.py -c <audiocard> -l <DSD file to play>`


**dsdlib.py**

Set of commonly used functions


The *pyalsaaudio-patches* directory contains patches to add DSD sample format
support to pyalsaaudio-0.7.
A SPEC file for Fedora is provided.

