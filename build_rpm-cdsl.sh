#!/bin/bash

source ./build-lib.sh

RELEASE=1
REQUIRES="--requires=comoonics-cs-py,PyXML"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-cdsl-py"
VERSION="0.1"
DESCRIPTION="Comoonics cdsl utilities and library written in Python"
LONG_DESCRIPTION="
Comoonics cdsl utilities and library written in Python
"
AUTHOR="Andrea Offermann"
AUTHOR_EMAIL="offermann@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.cdsl" : "lib/comoonics/cdsl"'
PACKAGES='"comoonics.cdsl"'
SCRIPTS='"bin/com-mkcdsl", "bin/com-mkcdslinfrastructure", "bin/com-cdslinvchk", "bin/com-searchcdsls"'

setup
