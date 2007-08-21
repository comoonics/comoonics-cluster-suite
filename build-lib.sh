# $Id: build-lib.sh,v 1.4 2007-08-21 13:19:02 andrea2 Exp $

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
# Revision 1.4  2007-08-21 13:19:02  andrea2
# added support for extra files
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
