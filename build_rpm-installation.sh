#!/bin/bash

source ./build-lib.sh

RELEASE=1
#REQUIRES=""
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-installation-py"
VERSION="0.1"
DESCRIPTION="Comoonics installation library written in Python"
LONG_DESCRIPTION="
Comoonics installation library written in Python. Used for installation helpers like anaconda or YaST.
"
AUTHOR="ATIX AG - Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.installation" : "lib/comoonics/installation"'
PACKAGE_DATA='"comoonics.installation": ["man/*.gz"]'
PACKAGES='"comoonics.installation"'
#SCRIPTS=''
#DATA_FILES=''

setup
