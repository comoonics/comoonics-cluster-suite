#!/bin/bash

source ./build-lib.sh

RELEASE=1
REQUIRES="--requires=comoonics-assistant-py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-ec-admin-py"
VERSION="0.1"
DESCRIPTION="Comoonics enterprise copy administrator written in Python"
LONG_DESCRIPTION="
Comoonics enterprise copy administrator written in Python
"
AUTHOR="ATIX AG - Mark Hlawatschek"
AUTHOR_EMAIL="hlawatschek@atix.de"
URL="http://www.atix.de/comoonics/"
#PACKAGE_DIR='"comoonics.assistant" : "lib/comoonics/assistant"'
#PACKAGE_DATA='"comoonics.assistant": ["man/*.gz"]'
#PACKAGE_DATA='"comoonics.assistant": ["lib/comoonics/assistant/xml-dr/*.xml"]'
#PACKAGES='"comoonics.assistant"'
SCRIPTS='"bin/com-ec-administrator-tui"'
DATA_FILES='("/etc/comoonics/enterprisecopy/xml-ec-admin",[
             "xml/xml-ec-admin/localclone.disk2disk.infodef.xml",
             "xml/xml-ec-admin/localclone.disk2disk.template.xml",
             "xml/xml-ec-admin/single-filesystem.backup.infodef.xml",
             "xml/xml-ec-admin/single-filesystem.backup.template.xml",
             "xml/xml-ec-admin/single-filesystem.restore.infodef.xml",
             "xml/xml-ec-admin/single-filesystem.restore.template.xml",
            ])'

setup
