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
        self._format=_format
        self.searchfor=self.createRESearchFor(_searchfor)
        self.match=None
    def format(self, _format=None):
        #SearchFormat.logger.debug("format(%s)" %_format)
        if not _format:
            _format=self._format
        return _format
    def createRESearchFor(self, _searchfor, _flags=0):
        import sre
        if isinstance(_searchfor, basestring):
            _searchfor=self.format(_searchfor)
            SearchFormat.logger.debug("createRESearchFor: searchfor<%s>: %s" %(self.__class__.__name__, _searchfor))
            _searchfor=sre.compile(_searchfor, _flags)
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
        return "<%s(format: %s, searchfor: %s)>" %(self.__class__.__name__, self._format, self.searchfor)

class SearchFormat(RESearchFormat):
    """
    Searchformat where format is a string * will match everything and ? one character
    """
    def format(self, _format=None):
        _format=super(SearchFormat, self).format(_format)
        _format=_format.replace("*", ".*")
        _format=_format.replace("?", ".")
        return _format

def main():
    _lines=("afas marc asdfik", "asdkfjlj")
    _sfs=[ RESearchFormat(".*marc"), SearchFormat("*marc") ]
    print "lines: %s, searchformats: %s" %(_lines, _sfs)
    for _line in _lines:
        for _sf in _sfs:
            print "line: %s, search: %s" %(_line, _sf.search(_line))

if __name__=="__main__":
    main()