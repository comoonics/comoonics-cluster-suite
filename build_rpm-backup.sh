#!/bin/bash
# $Id: build_rpm-backup.sh,v 1.1 2007-04-04 13:42:42 marc Exp $

source ./build-lib.sh

RELEASE=1
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
# Revision 1.1  2007-04-04 13:42:42  marc
# initial revision
#
