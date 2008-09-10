#!/bin/bash
# $Id: build_rpm-fenceacksv-plugins.sh,v 1.3 2008-09-10 13:11:06 marc Exp $

source ./build-lib.sh

RELEASE=2
REQUIRES="comoonics-cs-py >= 0.1-44,comoonics-ec-py >= 0.1-25,comoonics-bootimage-fenceacksv >= 0.3,comoonics-fenceacksv-py,comoonics-bootimage-listfiles-fenceacksv-plugins"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-fenceacksv-plugins-py"
VERSION="0.1"
DESCRIPTION="Comoonics Fenceacksv plugins written in Python"
LONG_DESCRIPTION="
Comoonics Fenceacksv plugins written in Python
"
AUTHOR="ATIX AG - Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.fenceacksv.plugins" : "lib/comoonics/fenceacksv/plugins"'
PACKAGES='"comoonics.fenceacksv.plugins"'
setup

##############
# $Log: build_rpm-fenceacksv-plugins.sh,v $
# Revision 1.3  2008-09-10 13:11:06  marc
# Fix Bug#262, plugins do not work in fenceacksv because of missing deps. Added the dep to rpmspec.
#
# Revision 1.2  2007/12/07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
#
# Revision 1.1  2007/09/10 15:15:41  marc
# released new version of:
# - comoonics-cs-py: 0.1-44
# - comoonics-ec-py: 0.1-25
# - comoonics-fenceacksv-py: 0.1-1
# - comoonics-fenceacksv-plugins-py: 0.1-1
#
