"""Comoonics clusterinfo object module


This module provides functionality to query instances
of clusterrepositories

"""


# here is some internal information
# $Id: RedHatClusterHelper.py,v 1.2 2009-07-22 08:37:09 marc Exp $
#
# @(#)$File$
#
# Copyright (c) 2001 ATIX GmbH, 2007 ATIX AG.
# Einsteinstrasse 10, 85716 Unterschleissheim, Germany
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/helper/RedHatClusterHelper.py,v $

from comoonics import ComLog
from xml import xpath
from xml.dom.ext.reader import Sax2
from xml.dom.ext import PrettyPrint

class RedHatClusterHelper(object):
    defaultclusterstatus_cmd= "/usr/sbin/clustat"
    defaultclusterstatus_opts=["-x", "-f"]

    log = ComLog.getLogger("comoonics.cluster.helper.RedHatClusterHelper")

    def __init__(self):
        self.clusterstatus_cmd=RedHatClusterHelper.defaultclusterstatus_cmd
        self.clusterstatus_opts=RedHatClusterHelper.defaultclusterstatus_opts
    def __getfromkwds(self, __kwd, __kwds, __default):
        if not __default:
            __default=getattr(self, __kwd, None)
        return __kwds.get(__kwd, __default)
    def __setfromkwds(self, __kwd, __kwds, __default):
        if not __default:
            __default=getattr(self, __kwd)
        
        return setattr(self, __kwd, __kwds.get(__kwd, __default))
    def getClusterStatusCmd(self, full=False, delimitor=" "):
        cmd=self.clusterstatus_cmd
        if full:
            cmd+=delimitor+delimitor.join(self.clusterstatus_opts)
        return cmd

    def setSimOutput(self):
        import os.path
        import StringIO
        import inspect
        path=os.path.dirname(inspect.getfile(self.__class__))
        f=open(os.path.join(path, "test", "clustat.xml"))
        buf=StringIO.StringIO()
        for line in f:
            buf.write(line)
        self.output=buf.getvalue()
        
    def queryStatusElement(self, **kwds):
        self.__setfromkwds("clusterstatus_cmd", kwds, self.clusterstatus_cmd)
        self.__setfromkwds("clusterstatus_opts", kwds, self.clusterstatus_opts)
        asValue=self.__getfromkwds("asvalue", kwds, True)
        delimitor=self.__getfromkwds("delimitor", kwds, " ")
        query=self.__getfromkwds("query", kwds, None)
        __output=self.__getfromkwds("output", kwds, None)
        self.log.debug("queryStatusElement: query=%s" %query)
        from comoonics import ComSystem
        import StringIO
        try:
            # create Reader object
            reader = Sax2.Reader()
            _dom=reader.fromString(ComSystem.execLocalOutput(self.getClusterStatusCmd(True, delimitor), True, __output))
            if not query:
                return _dom.documentElement
            else:
                _tmp1 = xpath.Evaluate(query, _dom.documentElement)
                _tmp2 = None
                if asValue:
                    _tmp2=list()
                    for i in range(len(_tmp1)):
                        _tmp2.append(_tmp1[i].value)
                    return delimitor.join(_tmp2)
                else:
                    _tmp2 = StringIO.StringIO()
                    PrettyPrint(_tmp1[0], stream=_tmp2)
                    return _tmp2.getvalue()
        except ComSystem.ExecLocalException, error:
            self.log.warning("Could not query the running cluster. No active values will be available. Error %s" %error)

    