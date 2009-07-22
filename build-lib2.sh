INSTALLDIR=install

function build_rpms {
	NAME=$1
	shift
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
	
	if [ $# -eq 0 ]; then
		PYTHONPATH=./ python setup.py $NAME -v bdist_rpm --spec-only --changelog="${CHANGELOG}"
		PYTHONPATH=./ python setup.py $NAME -v bdist_rpm --changelog="${CHANGELOG}"
	else
		PYTHONPATH=./ python setup.py $NAME -v bdist_rpm $@ --changelog="${CHANGELOG}"
	fi
	
	for file in $(find $INSTALLDIR -maxdepth 1 -type f); do
  		rm -f $(basename $file)
	done

	for file in $(find $INSTALLDIR/$NAME -maxdepth 1 -type f); do
  		rm -f $(basename $file)
	done
}