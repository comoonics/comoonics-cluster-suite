#!/bin/bash
# $Id: build_rpm-scsi.sh,v 1.2 2007-12-07 14:29:23 reiner Exp $

source ./build-lib.sh

RELEASE=1
REQUIRES="--requires=comoonics-cs-py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-scsi-py"
VERSION="0.1"
DESCRIPTION="Comoonics SCSI utilities and libraries written in Python"
LONG_DESCRIPTION="
Comoonics SCSI utilities and libraries written in Python
"
AUTHOR="ATIX AG - Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.scsi" : "lib/comoonics/scsi"'
PACKAGES='"comoonics.scsi"'
SCRIPTS='"bin/com-rescanscsi"'
setup

##############
# $Log: build_rpm-scsi.sh,v $
# Revision 1.2  2007-12-07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
#
# Revision 1.1  2007/04/04 13:20:09  marc
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
