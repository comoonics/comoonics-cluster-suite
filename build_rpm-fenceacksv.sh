#!/bin/bash
# $Id: build_rpm-fenceacksv.sh,v 1.2 2007-12-07 14:29:23 reiner Exp $

source ./build-lib.sh

RELEASE=1
REQUIRES="comoonics-cs-py >= 0.1-44"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-fenceacksv-py"
VERSION="0.1"
DESCRIPTION="Comoonics Fenceacksv utilities and libraries written in Python"
LONG_DESCRIPTION="
Comoonics Fenceacksv utilities and libraries written in Python
"
AUTHOR="ATIX AG - Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.fenceacksv" : "lib/comoonics/fenceacksv"'
PACKAGES='"comoonics.fenceacksv"'
setup

##############
# $Log: build_rpm-fenceacksv.sh,v $
# Revision 1.2  2007-12-07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
#
# Revision 1.1  2007/09/10 15:15:41  marc
# released new version of:
# - comoonics-cs-py: 0.1-44
# - comoonics-ec-py: 0.1-25
# - comoonics-fenceacksv-py: 0.1-1
# - comoonics-fenceacksv-plugins-py: 0.1-1
#
