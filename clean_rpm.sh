#!/bin/bash
RPMBUILDDIR=$1
[ -z "$RPMBUILDDIR" ] && RPMBUILDDIR=$(rpmbuild --showrc | grep ": _topdir" | awk '{print $3}')
if [ -d "$RPMBUILDDIR" ]; then
  echo "Cleaning $RPMBUILDDIR"
  find $RPMBUILDDIR -type f \( -name "*.rpm" -or -name "*.spec" -or -name "*.tar.*" \) -delete
fi
