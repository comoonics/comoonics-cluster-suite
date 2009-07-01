'''
Created on Jun 30, 2009

@author: marc
'''
import unittest

class test_SearchFormat(unittest.TestCase):
    lines={ "afas marc asdfik": True, "asdkfjlj": False}

    def test_search(self):
        from comoonics.search.SearchFormat import SearchFormat, RESearchFormat
        _sfs=[ RESearchFormat(".*marc"), SearchFormat("*marc") ]
        print "lines: %s, searchformats: %s" %(self.lines, _sfs)
        for _line, _matches in self.lines.items():
            for _sf in _sfs:
                _match=_sf.search(_line)
                print "line: %s, search: %s" %(_line, _match)
                self.assertTrue(_matches and _match or not _matches and not _match)

    def test_deepcopy(self):
        from comoonics.search.SearchFormat import SearchFormat, RESearchFormat
        _sfs=[ RESearchFormat(".*marc"), SearchFormat("*marc") ]
        import copy
        for _sf in _sfs:
            self.assert_(copy.deepcopy(_sf))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
