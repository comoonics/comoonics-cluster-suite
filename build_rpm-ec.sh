#!/bin/bash

# $Id: $

source ./build-lib.sh

RELEASE=38
REQUIRES='libxslt-python,comoonics-ec-base-py, comoonics-storage-py'
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-ec-py"
VERSION="0.1"
DESCRIPTION="Comoonics Enterprisecopy utilities and libraries written in Python"
LONG_DESCRIPTION="
Comoonics Enterprisecopy utilities and libraries written in Python
"
AUTHOR="ATIX AG - Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.enterprisecopy" : "lib/comoonics/enterprisecopy"'
PACKAGES='"comoonics.enterprisecopy"'
SCRIPTS='"bin/com-ec"'

setup

##############
# $Log: $
#
