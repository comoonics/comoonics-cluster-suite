""" Comoonics Message Requirement

Just to output a message as requirement

"""


# here is some internal information
# $Id: ComMessage.py,v 1.2 2010-03-08 12:30:48 marc Exp $
#

import sys
from ComRequirement import Requirement
from ComModification import Modification
from comoonics import ComLog
from comoonics import XmlTools

__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComMessage.py,v $

class MessageModification(Modification):
    """
    A class for outputing a message to stdout one of both ways is allowed:
    <modification type="message" message="hello world"/>

    <modification type="message">
        <text>Hello World
        my dear lad</text>
    </modification>
    """

    __logStrLevel__ = "comoonics.enterprisecopy.ComMessage.MessageModification"
    log=ComLog.getLogger(__logStrLevel__)

    def __init__(self, element, doc):
        """
        Creates a new requirement instance
        """
        Modification.__init__(self, element, doc)
        self._message=Message(self)

    def doModification(self):
        self._message._do()

class MessageRequirement(Requirement):
    """
    A class for outputing a message to stdout one of both ways is allowed:
    <modification type="copy">
        <requirement type="message" message="hello world"/>
        <file name="etc/cluster.conf" sourcefile="/etc/copysets/lilr10023/cluster.conf"/>
    </modification>

    <modification type="copy">
        <requirement type="message" message="hello world">
        <text>Hello World</text>
        </requirement>
        <file name="etc/cluster.conf" sourcefile="/etc/copysets/lilr10023/cluster.conf"/>
    </modification>
    """

    __logStrLevel__ = "comoonics.enterprisecopy.ComMessage.MessageRequirement"
    log=ComLog.getLogger(__logStrLevel__)

    def __init__(self, element, doc):
        """
        Creates a new requirement instance
        """
        Requirement.__init__(self, element, doc)
        self._message=Message(self)

    def doPre(self):
        if self.isPre():
            self._message._do()

    def doPost(self):
        if self.isPost():
            self._message._do()

    def do(self):
        pass
        #self._message._do()

class Message(object):
    def __init__(self, _parent, out=sys.stdout):
        self.parent=_parent
        self.out=out
    def _do(self):
        _message=""
        if self.parent.hasAttribute("message"):
            _message=self.parent.getAttribute("message")
            _message+="\n"
        else:
            _textelements=self.parent.getElement().getElementsByTagName("text")
            for _textelement in _textelements:
                _message+=XmlTools.getTextFromElement(_textelement)
                _message+="\n"
        self.out.write(_message)

###################
# $Log: ComMessage.py,v $
# Revision 1.2  2010-03-08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.1  2007/09/07 14:37:56  marc
# initial revision
#