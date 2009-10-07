#!/bin/bash
# $Id: build_rpm-scsi.sh,v 1.4 2009-10-07 12:12:38 marc Exp $


source ./build-lib2.sh

NAME=comoonics-scsi-py

build_rpms $NAME $*

##############
# $Log: build_rpm-scsi.sh,v $
# Revision 1.4  2009-10-07 12:12:38  marc
# new versions
#
# Revision 1.3  2009/09/28 15:29:57  marc
# updated to new build process
#
# Revision 1.2  2007/12/07 14:29:23  reiner
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
