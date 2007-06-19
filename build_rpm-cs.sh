#!/bin/bash

# $Id: $

source ./build-lib.sh

RELEASE=38
REQUIRES="--requires=PyXML,pyparted"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-cs-py"
VERSION="0.1"
DESCRIPTION="Comoonics Clustersuite utilities and libraries written in Python"
LONG_DESCRIPTION="
Comoonics Clustersuite utilities and libraries written in Python
"
AUTHOR="Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics" : "lib/comoonics"'
PACKAGES='"comoonics"'
SCRIPTS='"bin/com-dsh", "bin/cl_checknodes"'

setup

##############
# $Log: $
#
