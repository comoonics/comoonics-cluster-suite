#!/bin/bash
# $Id: build_rpm-backup.sh,v 1.5 2009-10-07 12:12:38 marc Exp $


source ./build-lib2.sh

NAME=comoonics-backup-py

build_rpms $NAME $*

##############
# $Log: build_rpm-backup.sh,v $
# Revision 1.5  2009-10-07 12:12:38  marc
# new versions
#
# Revision 1.4  2009/09/28 15:29:06  marc
# updated to new build process
#
# Revision 1.3  2007/12/07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
#
# Revision 1.2  2007/06/13 09:00:55  marc
# - now backuping full path to support incremental backups (0.1-2)
#
# Revision 1.1  2007/04/04 13:42:42  marc
# initial revision
#
