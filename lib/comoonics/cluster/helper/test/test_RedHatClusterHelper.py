"""
this module tests the functionality of RedHatClusterHelper
"""
import unittest

from comoonics.cluster.helper import RedHatClusterHelper

class test_RedHatClusterHelper(unittest.TestCase):
    OUTPUT_TEST_FILE="clustat.xml"
    TEST_QUERIES={ "/clustat/@version": "4.1.1",
                   "/clustat/cluster/@generation": "900",
                   "/clustat/quorum/@quorate": "1",
                   "/clustat/nodes/node[1]/@name": "gfs-node1",
                   "/clustat/groups/group[1]/@name": "service:vmware_ip",
                   "/clustat/nodes/node[1]/@state": "1" }
    def setUp(self):
        from comoonics import ComSystem
        ComSystem.setExecMode(ComSystem.SIMULATE)
        from comoonics import ComLog
        import logging
        import inspect
        import os.path
        ComLog.setLevel(logging.DEBUG)
        self.helper=RedHatClusterHelper()
        path=os.path.dirname(inspect.getfile(self.__class__))
        f=open(os.path.join(path, self.OUTPUT_TEST_FILE))
        import StringIO
        buf=StringIO.StringIO()
        for line in f:
            buf.write(line)
        self.TEST_OUTPUT=buf.getvalue()
    # tests the cluster helper status command method
    def testClusterStatusCmd(self):
        self.assertEqual("/usr/sbin/clustat -x -f", self.helper.getClusterStatusCmd(True))
        self.assertEqual("/usr/sbin/clustat", self.helper.getClusterStatusCmd(False))
        
    # tests querying a status element of a cluster helper
    def testQueryStatusElement(self):
        for _query, _result in self.TEST_QUERIES.items():
            self.assertEqual(self.helper.queryStatusElement(query=_query, output=self.TEST_OUTPUT), _result)

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(test_RedHatClusterHelper)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()

