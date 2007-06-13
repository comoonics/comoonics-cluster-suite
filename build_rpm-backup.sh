#!/bin/bash
# $Id: build_rpm-backup.sh,v 1.2 2007-06-13 09:00:55 marc Exp $

source ./build-lib.sh

RELEASE=2
REQUIRES="--requires=comoonics-cs-py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-backup-py"
VERSION="0.1"
DESCRIPTION="Comoonics Backup utilities and libraries written in Python"
LONG_DESCRIPTION="
Comoonics Backup utilities and libraries written in Python
"
AUTHOR="Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.backup" : "lib/comoonics/backup"'
PACKAGES='"comoonics.backup"'
setup

##############
# $Log: build_rpm-backup.sh,v $
# Revision 1.2  2007-06-13 09:00:55  marc
# - now backuping full path to support incremental backups (0.1-2)
#
# Revision 1.1  2007/04/04 13:42:42  marc
# initial revision
#
