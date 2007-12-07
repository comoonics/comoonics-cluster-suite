#!/bin/bash

source ./build-lib.sh

RELEASE=3
REQUIRES="--requires=comoonics-cs-py,PyXML,comoonics-pythonosfix-py,comoonics-cluster-py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-cdsl-py"
VERSION="0.2"
DESCRIPTION="Comoonics cdsl utilities and library written in Python"
LONG_DESCRIPTION="
Comoonics cdsl utilities and library written in Python
"
AUTHOR="ATIX AG - Andrea Offermann"
AUTHOR_EMAIL="offermann@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.cdsl" : "lib/comoonics/cdsl"'
PACKAGE_DATA='"comoonics.cdsl": ["man/*.gz"]'
PACKAGES='"comoonics.cdsl"'
SCRIPTS='"bin/com-mkcdsl", "bin/com-mkcdslinfrastructure", "bin/com-cdslinvchk", "bin/com-searchcdsls", "bin/com-rmcdsl"'
DATA_FILES='("share/man/man1",[
             "man/com-mkcdslinfrastructure.1.gz",
             "man/com-mkcdsl.1.gz",
             "man/com-searchcdsls.1.gz",
             "man/com-cdslinvchk.1.gz",
             "man/com-rmcdsl.1.gz"
            ])'

setup
