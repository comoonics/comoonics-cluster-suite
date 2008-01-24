#!/bin/bash
for buildfile in build_rpm-*.sh; do
   sh $buildfile
done 
