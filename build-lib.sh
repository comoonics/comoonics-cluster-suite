# $Id: build-lib.sh,v 1.9 2008-05-20 15:57:30 marc Exp $

function setup {
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

  [ -e MANIFEST ] && rm MANIFEST

[ -e setup.py ] && rm -f setup.py

echo '#!/usr/bin/python
import sys
import re
import os
import gzip

sys.path.append("./lib")
from comoonics import ComSystem

if not os.path.exists("/usr/bin/db2x_docbook2man"):
	print "ERROR: /usr/bin/db2x_docbook2man not installed !"
	print "  TIP: use \"yum install docbook2X\" to install the software"
	sys.exit(1)


ComSystem.__EXEC_REALLY_DO="continue"
manpages = "'${NAME}'.xml"
olddir=os.path.abspath(os.path.curdir)
os.chdir("man/")
if os.path.exists(manpages):
	ComSystem.execLocalStatusOutput("db2x_docbook2man " + manpages)
	man = '${DATA_FILES}'[1]
	for i in man:
		inF = file("../"+i.replace(".gz","",1),"rb")
		s = inF.read()
		inF.close()

		outF = gzip.GzipFile("../"+i,"wb")
		outF.write(s)
		outF.close()

		os.remove("../"+i.replace(".gz","",1))

os.chdir(olddir)

' > doc2man.py
if ! python doc2man.py; then
	exit 1
fi


echo '#!/usr/bin/python
from distutils.core import setup

setup(name="'${NAME}'",
      version="'${VERSION}'",
      description="'${DESCRIPTION}'",
      long_description="""'${LONG_DESCRIPTION}'""",
      author="'${AUTHOR}'",
      author_email="'${AUTHOR_EMAIL}'",
      url="'${URL}'",
      package_dir =  { '${PACKAGE_DIR}'},
      packages=      [ '${PACKAGES}' ],
      scripts=       [ '${SCRIPTS}' ],
      data_files=    [ '${DATA_FILES}' ],
      licence="GPL",
     )
' > setup.py

echo ${REQUIRES} | grep "^--requires" 2>&1 > /dev/null
if [ $? -ne 0 ] && [ -n "$REQUIRES" ]; then
	REQUIRES="--requires $REQUIRES"
fi
python setup.py -v bdist_rpm --release=${RELEASE} ${REQUIRES} ${NOAUTO_REQ} --changelog="${CHANGELOG}" --doc-files=${DOCFILES}
}
##########
# $Log: build-lib.sh,v $
# Revision 1.9  2008-05-20 15:57:30  marc
# bugfix with --requires when empty
#
# Revision 1.8  2007/12/07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
#
# Revision 1.7  2007/09/10 15:15:57  marc
# better support for requires
#
# Revision 1.6  2007/09/04 13:28:52  mark
# added verification for db2x tools
#
# Revision 1.5  2007/08/22 12:40:13  andrea2
# *** empty log message ***
#
# Revision 1.3  2007/04/02 12:09:38  marc
# stable changelog generation
#
# Revision 1.2  2007/03/05 21:13:00  marc
# added DOCFILES
#
# Revision 1.1  2007/02/09 12:31:24  marc
# initial revision
#
