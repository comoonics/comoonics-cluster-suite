#!/bin/bash
# $Id: build_rpm-storage.sh,v 1.1 2007-02-09 12:31:24 marc Exp $

source ./build-lib.sh

RELEASE=1
REQUIRES="--requires=comoonics-cs-py,comoonics-ec-py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-storage-py"
VERSION="0.1"
DESCRIPTION="Comoonics Enterprisecopy Storage utilities and libraries written in Python"
LONG_DESCRIPTION="
Comoonics Enterprisecopy Storage utilities and libraries written in Python
"
AUTHOR="Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.storage" : "lib/comoonics/storage"'
PACKAGES='"comoonics.storage"'

setup

##############
# $Log: build_rpm-storage.sh,v $
# Revision 1.1  2007-02-09 12:31:24  marc
# initial revision
#
