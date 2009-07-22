#!/bin/bash
INSTALLDIR=install
NAME=comoonics-base-py
CHANGELOG=$(awk '
BEGIN { changelogfound=0; }
/^'${NAME}'/{ changelogfound=1; next };
/^comoonics/ { changelogfound=0; next };
{
  if (changelogfound == 1) {
     print
  }
}
' < docs/CHANGELOG)

for file in $(find $INSTALLDIR -maxdepth 1 -type f); do
  cp $file $(basename $file)
done

for file in $(find $INSTALLDIR/$NAME -maxdepth 1 -type f); do
  cp $file $(basename $file)
done
PYTHONPATH=./ python setup.py $NAME -v bdist_rpm $@ --changelog="${CHANGELOG}"
# --dist-dir=../../dist --bdist-base=../../build
#popd