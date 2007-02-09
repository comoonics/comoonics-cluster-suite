#!/bin/bash
# $Id: build_rpm-storage-hp.sh,v 1.1 2007-02-09 12:31:24 marc Exp $

source ./build-lib.sh

RELEASE=1
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
# Revision 1.1  2007-02-09 12:31:24  marc
# initial revision
#
