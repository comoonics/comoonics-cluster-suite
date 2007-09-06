#!/bin/bash

source ./build-lib.sh

RELEASE=1
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-pythonosfix-py"
VERSION="0.1"
DESCRIPTION="Comoonics modul to fix bug in os.path.realpath in python-2.3.4-14.4"
LONG_DESCRIPTION="
Comoonics modul to fix bug in os.path.realpath in python-2.3.4-14.4
"
AUTHOR="Andrea Offermann"
AUTHOR_EMAIL="offermann@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.pythonosfix" : "lib/comoonics/pythonosfix"'
PACKAGES='"comoonics.pythonosfix"'

setup
