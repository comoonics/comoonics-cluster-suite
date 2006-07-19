#!/usr/bin/env python

# here is some internal information
# $Id: setup.py,v 1.1 2006-07-19 14:30:34 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/Attic/setup.py,v $

from distutils.core import setup

setup(name='comoonics_cs_py',
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
      packages=      [ 'comoonics', 'comoonics.enterprisecopy' ],
      scripts=['bin/com-ec']
     )

#########################
# $Log: setup.py,v $
# Revision 1.1  2006-07-19 14:30:34  marc
# initial revision
#