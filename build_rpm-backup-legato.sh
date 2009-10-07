#!/bin/bash
# $Id: build_rpm-backup-legato.sh,v 1.8 2009-10-07 12:12:38 marc Exp $

source ./build-lib2.sh

NAME=comoonics-backup-legato-py

build_rpms $NAME $*

##############
# $Log: build_rpm-backup-legato.sh,v $
# Revision 1.8  2009-10-07 12:12:38  marc
# new versions
#
# Revision 1.7  2009/09/28 15:29:06  marc
# updated to new build process
#
# Revision 1.6  2007/12/07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
#
# Revision 1.5  2007/08/07 11:22:01  marc
# - Fix Bug BZ #77 that the restore command is likely to timeout. This is ignored now.
#
# Revision 1.4  2007/08/06 13:06:04  marc
# new version
#
# Revision 1.3  2007/07/10 11:38:25  marc
# new version 3
#
# Revision 1.2  2007/06/13 09:02:08  marc
# - now backuping full path to support incremental backups (0.1-2)
#
# Revision 1.1  2007/04/04 13:42:42  marc
# initial revision
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
