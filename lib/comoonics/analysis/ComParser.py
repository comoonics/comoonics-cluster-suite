#!/usr/bin/python
"""analysis.ComGlockParser

analysis objects for the glock writers

"""

# here is some internal information
# $Id $
#

import logging
import sys
import os
import shlex

__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/analysis/ComParser.py,v $

class Parser(shlex.shlex):
    logger=logging.getLogger("comoonics.analysis.ComParser")
    def __init__(self, instream=None, infile=None, posix=False):
        shlex.shlex.__init__(self, instream, infile, posix)

    def items(self):
        """
        Returns all parsed items
        """
        pass
        

######################
# $Log: ComParser.py,v $
# Revision 1.1  2009-09-28 15:27:11  marc
# *** empty log message ***
#