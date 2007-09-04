# $Id: build-lib.sh,v 1.6 2007-09-04 13:28:52 mark Exp $

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
     )
' > setup.py
  python setup.py -v bdist_rpm --release=${RELEASE} ${REQUIRES} ${NOAUTO_REQ} --changelog="${CHANGELOG}" --doc-files=${DOCFILES}
}
##########
# $Log: build-lib.sh,v $
# Revision 1.6  2007-09-04 13:28:52  mark
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
