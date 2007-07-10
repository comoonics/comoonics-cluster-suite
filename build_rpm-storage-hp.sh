#!/bin/bash
# $Id: build_rpm-storage-hp.sh,v 1.7 2007-07-10 11:38:07 marc Exp $

source ./build-lib.sh

RELEASE=7
REQUIRES="--requires=comoonics-cs-py,comoonics-ec-py,comoonics-storage-py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-storage-hp-py"
VERSION="0.1"
DESCRIPTION="Comoonics Enterprisecopy HP Storage utilities and libraries written in Python"
LONG_DESCRIPTION="
Comoonics Enterprisecopy HP Storage utilities and libraries written in Python
"
AUTHOR="Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.storage.hp" : "lib/comoonics/storage/hp"'
PACKAGES='"comoonics.storage.hp"'

setup

##############
# $Log: build_rpm-storage-hp.sh,v $
# Revision 1.7  2007-07-10 11:38:07  marc
# new version 7
#
# Revision 1.6  2007/06/26 07:52:07  marc
# new version of comoonics-storage-hp-py 0.1-6
#
# Revision 1.5  2007/06/19 13:34:42  marc
# new versions
#
# Revision 1.4  2007/06/15 19:10:28  marc
# new version
#
# Revision 1.3  2007/06/13 09:09:12  marc
# - if management appliance gets locked while working we'll overwrite it
# - added reconnect on timeout
#
# Revision 1.2  2007/04/04 13:20:09  marc
# new revisions for:
# comoonics-cs-py-0.1-30
# comoonics-ec-py-0.1-15
# comoonics-scsi-py-0.1-1
# comoonics-storage-hp-py-0.1-2
# comoonics-storage-py-0.1-2
#
# Revision 1.1  2007/02/09 12:31:24  marc
# initial revision
#
