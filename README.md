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

#### building from source RPM
If needed, first setup your system for RPM building, see [Fedora, building a custom kernel] (https://fedoraproject.org/wiki/Building_a_custom_kernel)

Install the source RPM:

`rpm -ivh SRPMS/python-alsaaudio-0.7-8.fc20.src.rpm`

`cd ~/rpmbuild/SPECS`

`rpmbuild -bb --target=$(uname -m) python-alsaaudio.spec`

Install the newly created RPM:

``yum localinstall ~/rpmbuild/RPMS/`uname -m`/python-alsaaudio-0.7-8.fc20.`uname -m`.rpm``
