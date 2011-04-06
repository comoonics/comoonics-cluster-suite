#!/bin/bash

PRODUCTVERSION=${1}
CHANNELNAME=${2}
PRODUCTNAME=${3:-comoonics}
CHANNELBASEDIR=${4:-/atix/dist-mirrors/}
DISTRIBUTIONS=${5:-"rhel4 rhel5 rhel6 sles10 sles11 fedora"}
SERVERMAPPINGS="internal:http://archiv-server.gallien.atix/dist-mirrors/comoonics :http://download.atix.de/yum/comoonics"
usage() {
	cat << EOF
$0 version channelname [productname] [channelbasedir] [distributions] [servermapping]*
version       : version of the product
channelname   : name of the channel
productname   : name of the product. Default: $PRODUCTNAME
channelbasedir: where the channel will be created. Default $CHANNELBASEDIR
distributions : for which distribution should the channel be created. Default: $DISTRIBUTIONS
servermapping : for which servers a repo file should be created (Syntax: servername:serverbaseuri). Default: $SERVERMAPPINGS  
EOF
}

makedir() {
  if [ -n "$1" ] && [ ! -d $1 ]; then
    echo "Creating $1 .."
    mkdir -p $1
  fi
}

makerepo() {
  local productname=$1
  local productversion=$2
  local channelname=$3
  local repouri=$4
  local distribution=$5
  
  cat <<EOF
[${productname}-${productversion}-${channelname}-noarch]
name=Packages for the ${productname} version ${productversion} channel ${channelname} and architecture noarch
baseurl=${repouri}/${productversion}/${channelname}/${distribution}/RPMS/noarch
enabled=1
gpgcheck=1
gpgkey=${repouri}/${productname}-RPM-GPG.key

[${productname}-${productversion}-${channelname}]
name=Packages for the ${productname} version ${productversion} channel ${channelname} and architecture \$basearch
baseurl=${repouri}/${productversion}/${channelname}/${distribution}/RPMS/\$basearch
enabled=1
gpgcheck=1
gpgkey=${repouri}/${productname}-RPM-GPG.key

EOF
}
if [ $# -lt 2 ]; then
  usage
  exit
fi
if [ $# -le 5 ]; then
  shift $#
else
  shift 5
fi
if [ $# -ne 0 ]; then
  SERVERMAPPINGS=$@
fi

if [ ! -d $CHANNELBASEDIR ]; then
  echo "Channelbasedir $CHANNELBASEDIR does not exist. Cannot continue!" >&2
  exit 2
fi

RPMDIRS=${RPMDIRS:-"RPMS/i386 RPMS/x86_64 RPMS/noarch SRPMS"}
ARCHITECTURES=${ARCHITECTURES:-"x86_64 i386 noarch"}

makedir ${CHANNELBASEDIR}/${PRODUCTNAME}
makedir ${CHANNELBASEDIR}/${PRODUCTNAME}/${PRODUCTVERSION}
makedir ${CHANNELBASEDIR}/${PRODUCTNAME}/${PRODUCTVERSION}/${CHANNELNAME}

for distribution in $DISTRIBUTIONS; do
  makedir ${CHANNELBASEDIR}/${PRODUCTNAME}/${PRODUCTVERSION}/${CHANNELNAME}/$distribution
  for rpmdir in $RPMDIRS; do
  	makedir ${CHANNELBASEDIR}/${PRODUCTNAME}/${PRODUCTVERSION}/${CHANNELNAME}/$distribution/$rpmdir
  done
  for servermap in $SERVERMAPPINGS; do
  	repouri=$(echo "$servermap" | cut -f2- -d:)
  	reponame=$(echo "$servermap" | cut -f1 -d:)
  	[ -z "$repouri" ] && repouri=$reponame && reponame=
  	if [ -z "$reponame" ]; then
      repofilename=${PRODUCTNAME}.repo
  	else
      repofilename=${PRODUCTNAME}-${reponame}.repo
  	fi
  	if [ ! -f ${CHANNELBASEDIR}/${PRODUCTNAME}/${PRODUCTVERSION}/${CHANNELNAME}/$distribution/$repofilename ]; then
       makerepo $PRODUCTNAME $PRODUCTVERSION $CHANNELNAME $repouri $distribution $architecture >> ${CHANNELBASEDIR}/${PRODUCTNAME}/${PRODUCTVERSION}/${CHANNELNAME}/$distribution/$repofilename
  	fi
  done
done
