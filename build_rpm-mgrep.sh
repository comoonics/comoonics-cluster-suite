#!/bin/bash

# $Id: build_rpm-mgrep.sh,v 1.3 2009-10-07 12:12:38 marc Exp $


source ./build-lib2.sh

NAME=mgrep

build_rpms $NAME $*

##############
# $Log: build_rpm-mgrep.sh,v $
# Revision 1.3  2009-10-07 12:12:38  marc
# new versions
#
# Revision 1.2  2007/12/07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
#
# Revision 1.1  2007/10/02 12:18:44  marc
# initial revision
#
