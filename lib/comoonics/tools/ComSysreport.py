"""ComSysreport

Class to represent the sysreport of Red Hat in a more general way

"""

# here is some internal information
# $Id: ComSysreport.py,v 1.1 2007-09-07 14:44:41 marc Exp $
#

from comoonics import ComLog
from comoonics.enterprisecopy.ComEnterpriseCopy import EnterpriseCopy

SYSREPORT_TEMPLATEBASE="/usr/share/sysreport/templates"
DEFAULT_TEMPLATE_FILE="default.xsl"

class Sysreport(object):
    """
    the Baseclass for doing sysreports takes a Systeminformation as parameter to determine which systemreport
    components are needed.
    """
    head_set="sysreport-head"
    save_set="save-sysreport"
    XPATH_DESTINATION="//path/@name"
    XPATH_TARFILE="//destination/data/archive/@name"
    logger=ComLog.getLogger("comoonics.ComSysreport.Sysreport")
    def __init__(self, _sysinfo, _destination, _tarfile=None, sysreport_templatesbase=SYSREPORT_TEMPLATEBASE):
        """
        __init__(_sysinfo, _destination)
        @_sysinfo: the systeminformation of this system
        @_destination: where to write to
        """
        super(Sysreport, self).__init__()
        self.sets=None
        self._sysinfo=_sysinfo
        self.sysreport_templatesbase=sysreport_templatesbase
        self.destination=_destination
        self.tarfile=_tarfile
        self.xml_validate=1
        self.templatefiles=self.getTemplateFiles()
        self.enterprisecopy=self.getEnterprisecopy()

    def getTemplateFiles(self):
        import os.path
        import dircache
        _features=list(self._sysinfo.getFeatures())
        _file=DEFAULT_TEMPLATE_FILE
        _files=dict()
        _ret_files=dict()
        __dirfiles=dircache.listdir(self.sysreport_templatesbase)
        __dirfiles.sort()
        for _file in __dirfiles:
            #_file=re.sub("^\d+_", "", _file)
            self.logger.debug("file: %s" %_file)
            _file_features=os.path.splitext(_file)[0].split("-")
            if not _files.has_key(len(_file_features)):
                _files[len(_file_features)]=[ _file_features ]
            else:
                _files[len(_file_features)].append(_file_features)
        _keys=_files.keys()
        _keys.sort()
        _keys.reverse()
        self.logger.debug("getTemplateFiles: _files: %s" %_files)
        for _i in _keys:
            _file_features=_files[_i]
            for _file_feature_list in _file_features:
                _found=0
                for _file_feature in _file_feature_list:
                    if _file_feature in _features:
                        _found+=1
                self.logger.debug("getTemplateFiles: _file_feature_list: %s/%s, found: %u" %(_file_feature_list, _features, _found))
                if _found==len(_file_feature_list):
                    # self.logger.debug("getTemplateFiles(): index(%s): %u" %(_file_feature_list, self._getFeatureIndex(_file_feature_list)))
                    _ret_files[self._getFeatureIndex(_file_feature_list)] = "%s.xml" %"-".join(_file_feature_list)
                    for _feature in _file_feature_list:
                        if _feature in _features:
                            _features.remove(_feature)

        self.logger.debug("getTemplateFiles: Found files: %s" %_ret_files)

        _ks=_ret_files.keys()
        _ks.sort()
        _ks.reverse()
        _ret=list()
        for _k in _ks:
            _ret.append(_ret_files[_k])

        return _ret

    def _getFeatureIndex(self, _file_feature_list):
        i=0
        _features=self._sysinfo.getFeatures()
        # self.logger.debug("_getFeatureIndex(): features: %s" %_features)
        for _feature in _file_feature_list:
            if _feature in _features:
                if _features.index(_feature) > i:
                    i=_features.index(_feature)
        return i

    def getEnterprisecopy(self):
        from comoonics import XmlTools
        import xml.dom
        import odict
        import os.path
        ret_doc=None
        ret_element=None
        _sets=odict.Odict()
        for _templatefile in self.templatefiles:
            _file=open(os.path.join(self.sysreport_templatesbase, _templatefile),"r")
            doc=XmlTools.parseXMLFP(_file)
            # Initially create ret_doc. Cannot do it before cause we need the doc
            if not ret_doc:
                ret_doc=XmlTools.getDOMImplementation().createDocument(None, doc.documentElement.tagName, None)
                ret_element=ret_doc.documentElement
            for _child in doc.documentElement.childNodes:
                if _child.nodeType==xml.dom.Node.ELEMENT_NODE:
                    if _child.hasAttribute("name"):
                        _sets[_child.getAttribute("name")]=XmlTools.clone_node(_child, ret_doc)
                elif _child.nodeType == xml.dom.Node.ATTRIBUTE_NODE:
                    ret_element.appendChild(XmlTools.clone_node(_child, ret_doc))
        # remove the save-sysreport and add it to the end
        _save_set= _sets[self.save_set]
        del _sets[self.save_set]
        _sets[self.save_set]=_save_set

        for _set in _sets.values():
            Sysreport.logger.debug("getEnterprisecopy() adding child: %s" %_set.getAttribute("name"))
            ret_element.appendChild(_set)
        del _sets[self.save_set]
        del _sets[self.head_set]
        self.sets=_sets
        return EnterpriseCopy(ret_element, ret_doc)

    def getOverwriteMap(self):
        _map=dict()
        _map[self.XPATH_DESTINATION]=self.destination
        if self.tarfile:
            _map[self.XPATH_TARFILE]=self.tarfile
        return _map

    def overwriteDestination(self):
        from comoonics import XmlTools
        self.enterprisecopy=EnterpriseCopy(XmlTools.overwrite_attributes_with_xpaths(self.enterprisecopy.getElement(), self.getOverwriteMap()), self.enterprisecopy.getDocument())
        for setname in self.sets:
            for myset in self.enterprisecopy.allsets:
                if myset.hasAttribute("name") and myset.getAttribute("name"):
                    self.sets[setname]=myset
        return self.enterprisecopy.getElement()

    def getSetNames(self):
        return self.sets.keys()

    def getSets(self):
        return self.sets.values()

    def doSets(self, setnames=None, _head_set=True, _save_set=True):
        self.overwriteDestination()
        if not setnames:
            setnames=self.getSetNames()
        if _head_set:
            self.enterprisecopy.doAllsets(self.head_set)
        self.enterprisecopy.doAllsets(setnames)
        if _save_set:
            self.enterprisecopy.doAllsets(self.save_set)

# $Log: ComSysreport.py,v $
# Revision 1.1  2007-09-07 14:44:41  marc
# initial revision
#
