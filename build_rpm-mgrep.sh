#!/bin/bash

# $Id: build_rpm-mgrep.sh,v 1.2 2007-12-07 14:29:23 reiner Exp $

source ./build-lib.sh

RELEASE=1
REQUIRES="--requires=comoonics-search-py"
NOAUTO_REQ="--no-autoreq"
NAME="mgrep"
VERSION="0.1"
DESCRIPTION="MGrep tool that gives ability to search logfiles and files in parallel"
LONG_DESCRIPTION="
MGrep tool that gives ability to search logfiles and files in parallel
"
AUTHOR="ATIX AG - Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
SCRIPTS='"bin/mgrep"'
DATA_FILES='("share/man/man1",[
             "man/mgrep.1.gz"
            ])'


setup

##############
# $Log: build_rpm-mgrep.sh,v $
# Revision 1.2  2007-12-07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
#
# Revision 1.1  2007/10/02 12:18:44  marc
# initial revision
#
