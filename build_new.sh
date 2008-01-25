#!/bin/bash
rm -f dist/*
LASTBUILDFILE=.lastbuild
for buildfile in $(find ./ -newer .lastbuild -type f -name "build_rpm-*.sh"); do
   echo $buildfile
   sh $buildfile
done 
touch $LASTBUILDFILE
