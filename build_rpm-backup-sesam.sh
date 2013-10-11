#!/bin/bash
# $Id: build_rpm-backup-legato.sh,v 1.8 2009-10-07 12:12:38 marc Exp $

source ./build-lib2.sh

NAME=comoonics-backup-sesam-py

build_rpms $NAME "$@"
