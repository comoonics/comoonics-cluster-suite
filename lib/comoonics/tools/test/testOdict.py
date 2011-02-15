'''
Created on 15.02.2011

@author: marc
'''
import unittest


class Test(unittest.TestCase):


    def testOdict(self):
        from comoonics.tools.odict import Odict
        _in={ "a": "A", "b": "B", "d": "D", "c":"C" }
        _out=Odict()
#        print "testing dict"
#        print "adding to odict sorted: %s" %_in
        _keys=_in.keys()
        _keys.sort()
        for _key in _keys:
            _value=_in[_key]
#            print "Adding %s: %s" %(_key, _value)
            _out[_key]=_value
#        print "output ordered dict: %s" %_out
        self.assertEquals(_keys, _out.keys(), "Sorted input %s is not equal to sorted output %s" %(_keys, _out.keys()))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()