#!/bin/bash
# $Id: build_rpm-backup-legato.sh,v 1.1 2007-04-04 13:42:42 marc Exp $

source ./build-lib.sh

RELEASE=1
REQUIRES="--requires=comoonics-cs-py,comoonics-backup-py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-backup-legato-py"
VERSION="0.1"
DESCRIPTION="Comoonics Legato Backup utilities and libraries written in Python"
LONG_DESCRIPTION="
Comoonics Legato Backup utilities and libraries written in Python
"
AUTHOR="Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.backup.EMCLegato" : "lib/comoonics/backup/EMCLegato"'
PACKAGES='"comoonics.backup.EMCLegato"'
setup

##############
# $Log: build_rpm-backup-legato.sh,v $
# Revision 1.1  2007-04-04 13:42:42  marc
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
