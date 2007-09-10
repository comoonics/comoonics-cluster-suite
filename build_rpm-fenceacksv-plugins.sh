#!/bin/bash
# $Id: build_rpm-fenceacksv-plugins.sh,v 1.1 2007-09-10 15:15:41 marc Exp $

source ./build-lib.sh

RELEASE=1
REQUIRES="comoonics-cs-py >= 0.1-44,comoonics-ec-py >= 0.1-25,comoonics-bootimage-fenceacksv >= 0.3,comoonics-fenceacksv-py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-fenceacksv-plugins-py"
VERSION="0.1"
DESCRIPTION="Comoonics Fenceacksv plugins written in Python"
LONG_DESCRIPTION="
Comoonics Fenceacksv plugins written in Python
"
AUTHOR="Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.fenceacksv.plugins" : "lib/comoonics/fenceacksv/plugins"'
PACKAGES='"comoonics.fenceacksv.plugins"'
setup

##############
# $Log: build_rpm-fenceacksv-plugins.sh,v $
# Revision 1.1  2007-09-10 15:15:41  marc
# released new version of:
# - comoonics-cs-py: 0.1-44
# - comoonics-ec-py: 0.1-25
# - comoonics-fenceacksv-py: 0.1-1
# - comoonics-fenceacksv-plugins-py: 0.1-1
#
