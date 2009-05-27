from comoonics.cluster.ComQueryMap import QueryMap

import unittest

class test_ClusterQueryMap(unittest.TestCase):    
    _results={ "osr": { "nodeid": "/cluster/clusternode[hwid=1234]/@nodeid",
                        "ip": "/cluster/clusternode[nodeid=1234]/eth/@ip" },
               "redhatcluster": { "nodeid": "/cluster/clusternode[nodeid=1234]/com_info/eth[mac=1234]",
                                  "ip": "/cluster/clusternode[nodeid=1234]/com_info/eth/@ip" }}
        
    """
    Unittests for Clustertools
    """   
    def setUp(self):
        """
        set up data used in the tests.
        setUp is called before each test function execution.
        """
        import sys
        import os.path
        testpath=os.path.dirname(sys.argv[0])
        for _module in sys.modules.keys():
            if _module.endswith("test_ClusterQueryMap"):
                testpath=os.path.dirname(sys.modules[_module].__file__)
        self.querymap=QueryMap()
        #print "testpath: %s" %testpath
        self.querymap.read(os.path.join(testpath,"test_ClusterQueryMap.txt"))
    def testOsr(self):
        self._test("osr")
    def testRedhatCluster(self):
        self._test("redhatcluster")
    def _test(self, section):
        self.querymap.mainsection=section
        params=["1234",]
        for param in self._results[section]:
            _result1=self._results[section][param]
            _result2=self.querymap.get(None, param) % self.querymap.array2params(params)
            print "%s == %s" %(_result1, _result2)
            self.assertEqual(_result1, _result2)

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(test_ClusterQueryMap)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
