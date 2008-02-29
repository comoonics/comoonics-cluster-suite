#!/bin/bash

source ./build-lib.sh

RELEASE=1
REQUIRES="--requires=comoonics-assistant.py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-dr-py"
VERSION="0.1"
DESCRIPTION="Comoonics desaster recovery assistant written in Python"
LONG_DESCRIPTION="
Comoonics desaster recovery assistant written in Python
"
AUTHOR="ATIX AG - Mark Hlawatschek"
AUTHOR_EMAIL="hlawatschek@atix.de"
URL="http://www.atix.de/comoonics/"
#PACKAGE_DIR='"comoonics.assistant" : "lib/comoonics/assistant"'
#PACKAGE_DATA='"comoonics.assistant": ["man/*.gz"]'
#PACKAGE_DATA='"comoonics.assistant": ["lib/comoonics/assistant/xml-dr/*.xml"]'
#PACKAGES='"comoonics.assistant"'
SCRIPTS='"bin/comoonics-create-restoreimage","bin/comoonics-restore-system"'
DATA_FILES='("/etc/comoonics/enterprisecopy/xml-dr",[
             "xml/xml-dr/drbackup.xml",
			 "xml/xml-dr/createlivecd.xml",
			 "xml/xml-dr/drbackup.infodef.xml",
			 "xml/xml-dr/createlivecd.infodef.xml",
			 "xml/xml-dr/drrestore.template.xml",
			 "xml/xml-dr/drrestore.infodef.xml"
            ])'

setup
