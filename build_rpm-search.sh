#!/bin/bash

# $Id: build_rpm-search.sh,v 1.2 2007-12-07 14:29:23 reiner Exp $

source ./build-lib.sh

RELEASE=1
REQUIRES="comoonics-cs-py >= 0.1-46"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-search-py"
VERSION="0.1"
DESCRIPTION="Searchlibraries used by mgrep"
LONG_DESCRIPTION="
Searchlibraries used by mgrep
"
AUTHOR="ATIX AG - Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.search" : "lib/comoonics/search", "comoonics.search.datetime": "lib/comoonics/search/datetime"'
PACKAGES='"comoonics.search", "comoonics.search.datetime"'

setup

##############
# $Log: build_rpm-search.sh,v $
# Revision 1.2  2007-12-07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
#
# Revision 1.1  2007/10/02 12:18:44  marc
# initial revision
#
