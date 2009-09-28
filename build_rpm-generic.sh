#!/bin/bash
source build-lib2.sh

NAME=$(basename $1)
shift

build_rpms $NAME $*