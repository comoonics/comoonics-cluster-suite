"""
Class for logging to a generic database

"""
# here is some internal information
# $Id: XMLConfigParser.py,v 1.1 2011-02-15 14:58:21 marc Exp $
#
from ConfigParser import NoSectionError, DuplicateSectionError
from ConfigParser import ConfigParser as oldConfigParser
from comoonics.ComExceptions import ComException
from comoonics.ComProperties import Properties
from comoonics import ComLog
from comoonics import XmlTools

from xml.dom import Node

class NoLoggingConfigFound(ComException):
    pass

class IncompatibleConfigFileType(ComException):
    def __str__(self):
        return "The file %s seems to be not compatible to XMLConfigParser." %self.value

mylogger=ComLog.getLogger("comoonics.XMLConfigParser")
#mylogger.setLevel(logging.DEBUG)

class ConfigParser(oldConfigParser):
    LOGGING_TAGNAME="logging"
    LOGGERS_TAGNAME="loggers"
    LOGGER_TAGNAME="logger"
    FORMATTERS_TAGNAME="formatters"
    FORMATTER_TAGNAME="formatter"
    HANDLERS_TAGNAME="handlers"
    HANDLER_TAGNAME="handler"
    ARGS_TAGNAME="args"
    ARG_TAGNAME="arg"
    #PROPERTIES_TAGNAME="properties"
    #PROPERTY_TAGNAME="property"

    ADD_TAGS={ "formatter": ("format",)}

    # should we validate the xml or not
    validate=True
    # delimiter of lists
    delimiter=","

    _logging_element=None
    _subsection_prefixes=dict()
    def __init__(self, defaults=None):
        oldConfigParser.__init__(self, defaults)
        self.doc=None

    def read(self, filename):
        """ This method reads the file and initializes all internal structures for handling as ConfigParser. """
        if isinstance(filename, basestring):
            self.doc=XmlTools.parseXMLFile(filename, self.validate)
            try:
                if self.doc.documentElement.tagName == self.LOGGING_TAGNAME:
                    _baseelement=self.doc.documentElement
                else:
                    _baseelement=self.doc.documentElement.getElementsByTagName(self.LOGGING_TAGNAME)[0]
            except:
                mylogger.exception("No Logging configuration found in file %s" %(filename))
                raise NoLoggingConfigFound, "No Logging configuration found in file %s" %(filename)
        elif isinstance(filename, Node):
            _baseelement=filename
        else:
            raise IncompatibleConfigFileType(type(filename))
        self._read(_baseelement, filename)

    def toDelimiterString(self, _list):
        return self.delimiter.join(_list)

    def getNamesOfElements(self, section):
        return self._logging_element.getElementsByTagName(section)

    def getSubsectionPrefix(self, section):
        return self._subsection_prefixes[section]

    def formatSubsectionPair(self, section, name):
        return "%s_%s" %(self.getSubsectionPrefix(section), name)

    def formatArgs(self, args):
        _str=""
        for arg in args:
            _str+=arg+self.delimiter
        return "("+_str+")"

    def _interpolate(self, section, option, rawval, variables):
        if isinstance(rawval, basestring):
            oldConfigParser._interpolate(self, section, option, rawval, variables)
        return rawval

    def _read(self, _baseelement, filename):
        self._parseSections(self.LOGGERS_TAGNAME, _baseelement, (self.LOGGER_TAGNAME,))
        self._parseSections(self.HANDLERS_TAGNAME, _baseelement, (self.HANDLER_TAGNAME,))
        self._parseSections(self.FORMATTERS_TAGNAME, _baseelement, (self.FORMATTER_TAGNAME,))
        for _section in self._sections.keys():
            if hasattr(self, "apply_"+self._sections[_section]['__element__'].nodeName):
                func=getattr(self, "apply_"+self._sections[_section]['__element__'].nodeName)
                _cursect=self._sections[_section]
                func(_cursect)

    def _parseSections(self, sections, baseelement, validsubsections):
        sectionselement=baseelement.getElementsByTagName(sections)
        if len(sectionselement)<1:
            NoSectionError(sections)
        elif len(sectionselement)>1:
            DuplicateSectionError(sections)
        sectionselement=sectionselement[0]
        self._sections[sections]=self._parseSection(sections, sectionselement, validsubsections, None, True)
        _keys=list()
        for key in self._sections.keys():
            for validsubsection in validsubsections:
                if key.startswith(validsubsection+"_"):
                    _keys.append(self._sections[key]['__name__'])
        self._sections[sections]['keys']=self.delimiter.join(_keys)

    def _parseSection(self, section, sectionelement, validsubsections, parent=None, rootElement=False):
        _name=section
        if sectionelement.hasAttribute("name"):
            _name=sectionelement.getAttribute('name')
        _cursect={'__name__': _name,
                  '__element__': sectionelement}
        if parent:
            if not rootElement:
                _cursect['__parent__']=parent
                _cursect['parent']=parent['__name__']
            else:
                rootElement=False
        _add_tags=None
        if self.ADD_TAGS.has_key(sectionelement.nodeName):
            _add_tags=self.ADD_TAGS[sectionelement.nodeName]
        _section=None
        if validsubsections:
            _args=None
            for subsection in validsubsections:
                for _child in sectionelement.childNodes:
                    if _child.nodeType == Node.ELEMENT_NODE and _child.nodeName == subsection:
                        mylogger.debug("_parseSection(%s, %s): subsection, %s, %s" %(section, validsubsections, subsection, _child))
                        _section=self._parseSection(subsection, _child, validsubsections, _cursect, rootElement)
                        self._subsection_prefixes[section]=subsection
                        self._sections[self.formatSubsectionPair(section, _section['__name__'])]=_section
                    if _add_tags and _child.nodeName in _add_tags:
                        if hasattr(self, "_parse_"+_child.nodeName):
                            func=getattr(self, "_parse_"+_child.nodeName)
                            func(_cursect, _child)
        for _child in sectionelement.childNodes:
            if _child.nodeType == Node.ELEMENT_NODE and _child.nodeName == self.ARGS_TAGNAME:
                _cursect[self.ARGS_TAGNAME]=self.formatArgs(self._parseArgs(_child))
            elif _child.nodeType == Node.ELEMENT_NODE and _child.nodeName == Properties.TAGNAME:
                _properties=Properties(_child)
                mylogger.debug("_parseSection(%s): properties: %s" %(section, _properties))
                for (_name, _property) in _properties.items():
                    _cursect[_name]=_property.getValue()
        for i in range(sectionelement.attributes.length):
            _child=sectionelement.attributes.item(i)
            _cursect[_child.name]=_child.value
            mylogger.debug("_parseSection(%s, %s): %s->attribute: %s: %s" %(section, validsubsections, _cursect['__name__'], _child.name, _child.value))
        return _cursect

    def apply_logger(self, cursect):
        if str(cursect['__name__'])=='root':
            if cursect.has_key("parent"):
                del cursect['parent']
            if cursect.has_key("__parent__"):
                del cursect['__parent__']
            qualname="(root)"
        else:
            cursect['channel']=cursect['__name__']
            qualname=self._generateQualname(cursect, cursect['__element__'])[:-1]
            mylogger.debug("apply_logger qualname: %s" %(qualname))
        cursect['qualname']=qualname

    def _generateQualname(self, cursect, sectionelement, qualname=""):
        if cursect.has_key('__parent__'):
            _parent=cursect['__parent__']
            qualname+=self._generateQualname(_parent, _parent['__element__'], qualname)
            qualname+=cursect['__name__']+"."
        return qualname

    def _parse_format(self, cursect, child):
        _format=XmlTools.getTextFromElement(child)
        cursect["format"]=_format

    def _parse_dateformat(self, cursect, child):
        _format=XmlTools.getTextFromElement(child)
        cursect["dateformat"]=_format

    def _parseArgs(self, args_element):
        arg_elements=args_element.getElementsByTagName(self.ARG_TAGNAME)
        args=list()
        if len(arg_elements)>0:
            for arg_element in arg_elements:
                arg=""
                for _child in arg_element.childNodes:
                    if _child.nodeType == Node.TEXT_NODE:
                        arg+=_child.nodeValue
                args.append(arg)
        return args

########################
# $Log: XMLConfigParser.py,v $
# Revision 1.1  2011-02-15 14:58:21  marc
# initial revision
#
# Revision 1.3  2010/11/21 21:48:19  marc
# - fixed bug 391
#   - moved to upstream XmlTools implementation
#
# Revision 1.2  2007/06/13 10:09:27  marc
# - removed debugging
#
# Revision 1.1  2007/06/13 09:12:05  marc
# initial revision
#
