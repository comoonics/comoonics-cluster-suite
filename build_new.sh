#!/bin/bash
rm -f dist/*
failedbuilds=""
LASTBUILDFILE=.lastbuild
for buildfile in $(find ./ -newer .lastbuild -type f -name "build_rpm-*.sh"); do
   rm -rf build/*
   echo $buildfile
   bash $buildfile
   if [ $? -ne 0 ]; then
   	 failedbuilds="$failedbuilds $buildfile"
   fi
done 
touch $LASTBUILDFILE
if [ -n "$failedbuilds" ]; then
	echo "Could not build the following packages: $failedbuilds" >&2
	exit 1
fi

rpm --resign dist/*.rpm
