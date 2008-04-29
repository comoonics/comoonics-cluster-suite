#!/bin/bash

source ./build-lib.sh

RELEASE=9
REQUIRES="--requires=comoonics-cs-py,PyXML"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-cluster-py"
VERSION="0.1"
DESCRIPTION="Comoonics cluster configuration utilities written in Python"
LONG_DESCRIPTION="
Comoonics cluster configuration utilities written in Python
"
AUTHOR="ATIX AG - Andrea Offermann"
AUTHOR_EMAIL="offermann@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.cluster" : "lib/comoonics/cluster"'
PACKAGE_DATA='"comoonics.cdsl": ["man/*.gz"]'
PACKAGES='"comoonics.cluster"'
SCRIPTS='"bin/com-queryclusterconf"'
DATA_FILES='("share/man/man1",[
             "man/com-queryclusterconf.1.gz"
            ])'

setup
