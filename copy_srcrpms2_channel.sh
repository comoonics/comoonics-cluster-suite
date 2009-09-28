#!/bin/bash

[ -z "$SOURCEDIR" ] && SOURCEDIR=dist
[ -z "$RPMBUILDDIR" ] && RPMBUILDDIR=$(rpmbuild --showrc | grep ": _topdir" | awk '{print $3}')
[ -z "$REPOSITORYDIR" ] && REPOSITORYDIR=/atix/dist-mirrors/comoonics
[ -z "$REPOSITORY" ] && REPOSITORY=preview
[ -z "$SRPMSDIR" ] && SRPMSDIR=SRPMS

if [ $# -eq 0 ]; then
   files=$(ls -1 $SOURCEDIR/*.src.rpm)
else
   files=$*
fi

packages=""
for file in $files; do
	package=${file#dist/}
    package=${package%.src.rpm}
    package=${package%.spec}
	
	packages="$packages "$(find $SOURCEDIR -name "${package}*.src.rpm")
done

echo "Copying files $packages => $REPOSITORYDIR/$REPOSITORY/$SRPMSDIR"
cp -a $packages $REPOSITORYDIR/$REPOSITORY/$SRPMSDIR

echo "Updating repository data in $REPOSITORYDIR/$REPOSITORY/$SRPMSDIR"
createrepo $OPTS $REPOSITORYDIR/$REPOSITORY/$SRPMSDIR