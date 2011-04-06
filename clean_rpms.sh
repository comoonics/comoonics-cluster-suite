#!/bin/bash
RPMBUILDDIR=${1:-$(rpmbuild --showrc | grep ": _topdir" | awk '{print $3}')}
RPMFILTER=${2:-comoonics-bootimage*}

usage() {
  cat <<EOF
$0 rpmbuilddir rpmfilter
rpmbuilddir: where to clean the rpms from. default: $RPMBUILDDIR
rpmfilter:   what rpms should be included. default: $RPMFILTER
EOF
}

if [ "$1" = "-h" ] || [ "$1" = "-?" ]; then
	usage
	exit 1
fi
if [ -d "$RPMBUILDDIR" ]; then
  echo "Cleaning $RPMBUILDDIR"
  find $RPMBUILDDIR -iname "$RPMFILTER" -type f \( -name "*.rpm" -or -name "*.spec" -or -name "*.tar.*" \) -delete
fi
