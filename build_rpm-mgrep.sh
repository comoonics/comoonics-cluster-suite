#!/bin/bash

# $Id: build_rpm-mgrep.sh,v 1.1 2007-10-02 12:18:44 marc Exp $

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
AUTHOR="Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
SCRIPTS='"bin/mgrep"'
DATA_FILES='("share/man/man1",[
             "man/mgrep.1.gz"
            ])'


setup

##############
# $Log: build_rpm-mgrep.sh,v $
# Revision 1.1  2007-10-02 12:18:44  marc
# initial revision
#
