#!/bin/bash

source ./build-lib.sh

RELEASE=3
REQUIRES="--requires=comoonics-cluster-py,comoonics-ec-py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-assistant-py"
VERSION="0.1"
DESCRIPTION="Comoonics assistant library written in Python"
LONG_DESCRIPTION="
Comoonics assistant library written in Python
"
AUTHOR="ATIX AG - Mark Hlawatschek"
AUTHOR_EMAIL="hlawatschek@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.assistant" : "lib/comoonics/assistant"'
PACKAGE_DATA='"comoonics.assistant": ["man/*.gz"]'
PACKAGES='"comoonics.assistant"'
#SCRIPTS=''
#DATA_FILES=''

setup
