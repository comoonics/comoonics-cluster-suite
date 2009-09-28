#!/bin/bash

detectDistribution() {
  head -q -n1 /etc/*-release | sed -e s/release// -e 's/ //g' -e 's/(.*)//g' -e 's/\.[0-9]*$//' | tr [A-Z] [a-z] | sed -e 's/centos/redhat/' -e 's/redhat/redhat-el/' -e 's/suselinuxenterpriseserver/suse-linux-es/' | sort -u
}

[ -z "$SOURCEDIR" ] && SOURCEDIR=dist
[ -z "$RPMBUILDDIR" ] && RPMBUILDDIR=$(rpmbuild --showrc | grep ": _topdir" | awk '{print $3}')
[ -z "$REPOSITORYDIR" ] && REPOSITORYDIR=/atix/dist-mirrors/comoonics
[ -z "$DISTRIBUTION" ] && DISTRIBUTION=$(detectDistribution)
[ -z "$REPOSITORY" ] && REPOSITORY=preview
[ -z "$SRPMSDIR" ] && SRPMSDIR=SRPMS
[ -z "$ARCHITECTURE" ] && ARCHITECTURE=noarch

if [ $# -eq 0 ]; then
   files=$(ls -1 $SOURCEDIR/*.src.rpm)
else
   files=$*
fi

packages=""
for file in $files; do
	package=${file#dist/}
    package=${package%%.*.rpm}
    package=${package%.spec}
	
	packages="$packages "$(find $RPMBUILDDIR -path "*/${ARCHITECTURE}/${package}*.${ARCHITECTURE}.rpm")
done

echo "Copying files $packages => $REPOSITORYDIR/$DISTRIBUTION/$REPOSITORY/$ARCHITECTURE/RPMS"
cp -a $packages $REPOSITORYDIR/$DISTRIBUTION/$REPOSITORY/$ARCHITECTURE/RPMS

echo "Updating repository data in $REPOSITORYDIR/$DISTRIBUTION/$REPOSITORY/$ARCHITECTURE/RPMS"
createrepo $OPTS $REPOSITORYDIR/$DISTRIBUTION/$REPOSITORY/$ARCHITECTURE