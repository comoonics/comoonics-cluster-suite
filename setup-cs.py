#!/usr/bin/env python

# here is some internal information
# $Id: setup-cs.py,v 1.2 2006-09-28 08:47:28 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/Attic/setup-cs.py,v $

from distutils.core import setup

setup(name='comoonics-cs-py',
      version='0.1',
      description='Comoonics Clustersuite utilities and libraries written in Python',
      long_description=
"""
Comoonics Clustersuite utilities and libraries written in Python
""",
      author='Marc Grimme',
      author_email='grimme@atix.de',
      url='http://www.atix.de/comoonics/',
      package_dir =  { '' : 'lib'},
      packages=      [ 'comoonics' ],
      scripts=['bin/cl_checknodes']
     )

#########################
# $Log: setup-cs.py,v $
# Revision 1.2  2006-09-28 08:47:28  marc
# added cl_checknodes
#
# Revision 1.1  2006/07/26 10:04:04  marc
# initial revision
#
# Revision 1.1  2006/07/19 14:30:34  marc
# initial revision
#