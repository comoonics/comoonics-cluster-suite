#!/bin/bash

source ./build-lib.sh

RELEASE=1
REQUIRES="--requires=comoonics-cs-py,PyXML,comoonics-pythonosfix-py,comoonics-cluster-py,comoonics-ec-py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-assistant-py"
VERSION="0.1"
DESCRIPTION="Comoonics assistant library written in Python"
LONG_DESCRIPTION="
Comoonics assistant library written in Python
"
AUTHOR="ATIX AG - Andrea Offermann"
AUTHOR_EMAIL="offermann@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.assistant" : "lib/comoonics/assistant"'
PACKAGE_DATA='"comoonics.assistant": ["man/*.gz"]'
PACKAGES='"comoonics.assistant"'
#SCRIPTS=''
#DATA_FILES=''

setup
