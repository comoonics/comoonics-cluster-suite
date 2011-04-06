#!/bin/bash

CHANNELDIR=${CHANNELDIR:-/atix/dist-mirrors/comoonics}
DISTRIBUTIONS=${DISTRIBUTIONS:-"rhel4 rhel5 sles10 sles11 fedora"}
DISTRIBUTIONSNEG=${DISTRIBUTIONSNEG:-"rhel4 rhel5 sles10 sles11 fedora"}
if [ -z "$1" ]; then
  CHANNELS=${CHANNELS:-"preview prod-4.6"}
else
  CHANNELS=$@
fi

for distribution in ${DISTRIBUTIONS}; do
	# First build distributions to exclude from DISTRIBUTION ready to be given to find
    findparams="-false"
    set -f
	for tempdist in ${DISTRIBUTIONSNEG}; do
		if [ "$tempdist" != "$distribution" ]; then
			findparams='-name *'$tempdist'* -or '$findparams
		fi
	done
	for channel in ${CHANNELS}; do
		if [ -d "$CHANNELDIR/$distribution/$channel" ]; then
			echo -n "Tidying up channel $channel.."
			find $CHANNELDIR/$distribution/$channel $findparams -delete
			echo "[OK]"
		fi
	done 
	set +f
done