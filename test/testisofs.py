import sys
import traceback
import copy

sys.path.append("../lib")


from comoonics.enterprisecopy import ComModificationset

from comoonics import ComLog, ComSystem

import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath

ComSystem.__EXEC_REALLY_DO="ask"

# create Reader object
reader = Sax2.Reader()

xml="""
<modificationset type="isofs" name="/tmp/myiso.iso">
        <path name="/tmp/isofs"/>
        <path name="/tmp/extras"/>
        <properties>
            <property name="bootcd" value="livecd"/>
            <property name="cdlabel" value="COMOONICS_LIVECD"/>
        </properties>
</modificationset>
"""
xml2="<test/>"

doc = reader.fromString(xml)

PrettyPrint(doc)
ms=ComModificationset.getModificationset(doc.documentElement, doc)

ms.doPre()
ms.doModifications()
ms.doPost()
