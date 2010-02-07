""" comoonics.cdsl.migration Packge
helper package to migration versions from old to new.
"""
# $Id: __init__.py,v 1.1 2010-02-07 20:01:26 marc Exp $
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


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cdsl/migration/__init__.py,v $
from comoonics.ComExceptions import ComException

class ConfigfileFormatException(ComException): pass

from MigrationTools import MigrationTool, DefaultMigrationTool

def getMigrationTool(fromversion, toversion):
    return DefaultMigrationTool()

def migrate(fromversion, toversion, **keys):
    tool=getMigrationTool(fromversion, toversion)
    return tool.migrate(fromversion, toversion, **keys)