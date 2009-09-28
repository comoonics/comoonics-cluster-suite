#!/bin/bash
# $Id: build_rpm-storage.sh,v 1.4 2009-09-28 15:30:18 marc Exp $

source ./build-lib.sh

RELEASE=3
REQUIRES="--requires=comoonics-ec-py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-storage-py"
VERSION="0.1"
DESCRIPTION="Comoonics Enterprisecopy Storage utilities and libraries written in Python"
LONG_DESCRIPTION="
Comoonics Enterprisecopy Storage utilities and libraries written in Python
"
AUTHOR="ATIX AG - Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.storage" : "lib/comoonics/storage"'
PACKAGES='"comoonics.storage"'

setup

##############
# $Log: build_rpm-storage.sh,v $
# Revision 1.4  2009-09-28 15:30:18  marc
# New version
#
# Revision 1.3  2007/12/07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
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
