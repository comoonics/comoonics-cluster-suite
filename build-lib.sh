# $Id: build-lib.sh,v 1.1 2007-02-09 12:31:24 marc Exp $

function setup {
  CHANGELOG=$(awk '
BEGIN { changelogfound=0; }
/^comoonics-cs-py/{ changelogfound=1; next };
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
      scripts=       [ '${SCRIPTS}' ]
     )
' > setup.py
  python setup.py -v bdist_rpm --release=${RELEASE} ${REQUIRES} ${NOAUTO_REQ} --changelog="${CHANGELOG}"
}
##########
# $Log: build-lib.sh,v $
# Revision 1.1  2007-02-09 12:31:24  marc
# initial revision
#
