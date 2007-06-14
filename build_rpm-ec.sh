#!/bin/bash

# $Id: $

source ./build-lib.sh

RELEASE=20
REQUIRES="--requires=PyXML,libxslt-python,comoonics-cs-py,comoonics-cs"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-ec-py"
VERSION="0.1"
DESCRIPTION="Comoonics Enterprisecopy utilities and libraries written in Python"
LONG_DESCRIPTION="
Comoonics Enterprisecopy utilities and libraries written in Python
"
AUTHOR="Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.enterprisecopy" : "lib/comoonics/enterprisecopy"'
PACKAGES='"comoonics.enterprisecopy"'
SCRIPTS='"bin/com-ec"'

setup

##############
# $Log: $
#
