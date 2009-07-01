#!/usr/bin/python
"""
"""

from comoonics import ComLog

class RESearchFormat(object):
    """
    SearchFormat where format is a regular expression
    """
    logger=ComLog.getLogger("comoonics.search.SearchFormat")
    def __init__(self, _searchfor="", _format=""):
        super(RESearchFormat, self).__init__()
        self._format=_format
        if _searchfor:
            self.searchfor=self.createRESearchFor(_searchfor)
        self.match=None
    def __deepcopy__(self, memo=None):
        _obj=self.__class__()
        _obj.__init__()
        _obj.searchfor=self.searchfor
        _obj._format=self._format
        return _obj
    def format(self, _format=None):
        #SearchFormat.logger.debug("format(%s)" %_format)
        if not _format:
            _format=self._format
        return _format
    def createRESearchFor(self, _searchfor, _flags=0):
        import re
        if isinstance(_searchfor, basestring):
            _searchfor=self.format(_searchfor)
            SearchFormat.logger.debug("createRESearchFor: searchfor<%s>: %s" %(self.__class__.__name__, _searchfor))
            _searchfor=re.compile(_searchfor, _flags)
            return _searchfor
        else:
            return _searchfor
    def search(self, _line, _searchfor=None, _flags=0):
        self.clear()
        if not _searchfor:
            _searchfor=self.searchfor
        #SearchFormat.logger.debug("search: searchfor: %s, line: %s" %(_searchfor, _line))
        _searchfor=self.createRESearchFor(_searchfor, _flags)
        self.match=_searchfor.search(_line)
        return self.match
    def found(self, _line, _searchfor=None, _flags=0):
        #self.logger.debug("_line %s" %line)
        if self.search(_line, _searchfor, _flags):
            return True
        else:
            return False
    def getMatch(self):
        return self.match
    def clear(self):
        self.match=None

    def __str__(self):
        return "<%s(format: %s, searchfor: %s)>" %(self.__class__.__name__, self._format, self.searchfor.pattern)

class SearchFormat(RESearchFormat):
    """
    Searchformat where format is a string * will match everything and ? one character
    """
    def format(self, _format=None):
        _format=super(SearchFormat, self).format(_format)
        _format=_format.replace("*", ".*")
        _format=_format.replace("?", ".")
        return _format
