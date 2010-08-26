#!/bin/bash
# $Id: build_rpm-fenceacksv-plugins.sh,v 1.6 2010-08-26 08:07:14 marc Exp $


source ./build-lib2.sh

NAME=comoonics-fenceacksv-plugins-py

build_rpms $NAME $*

##############
# $Log: build_rpm-fenceacksv-plugins.sh,v $
# Revision 1.6  2010-08-26 08:07:14  marc
# new versions
#
# Revision 1.5  2009/10/07 12:12:38  marc
# new versions
#
# Revision 1.4  2009/09/28 15:29:30  marc
# updated to new build process
#
# Revision 1.3  2008/09/10 13:11:06  marc
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
