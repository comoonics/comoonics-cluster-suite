#!/bin/bash
rm -f dist/*
failedbuilds=""
for buildfile in build_rpm-*.sh; do
   rm -rf build/*
   echo "Building $buildfile.."
   bash $buildfile
   if [ $? -ne 0 ]; then
   	 failedbuilds="$failedbuilds $buildfile"
#   	 echo "Failed to build $buildfile"
#   	 exit 1
   fi
done 

if [ -n "$failedbuilds" ]; then
	echo "Could not build the following packages: $failedbuilds" >&2
	exit 1
fi
touch .lastbuild
rpm --resign dist/*.src.rpm
rpm -ivh dist/*.src.rpm