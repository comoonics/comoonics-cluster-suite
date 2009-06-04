import unittest
import setup

setupCluster=setup.SetupCluster()        
setupCDSLRepository=setup.SetupCDSLRepository()  
setupCdsls=setup.SetupCDSLs(setupCDSLRepository.cdslRepository2)

class test_CdslSearch(unittest.TestCase):
    def testCdslSearch(self):
        """
        Creates clusterRepository, clusterInfo and cdslRepository and search for cdsls which 
        are not already included in inventoryfile.
        """
        cdslSearch(setupCDSLRepository,clusterInfo)
         
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    setupCDSLRepository.cdslRepository1.buildInfrastructure(setupCluster.clusterinfo)
    setupCdsls.setupCDSLInfrastructure(setup.tmppath, setupCDSLRepository.cdslRepository1)
    unittest.main()
    setupCdsls.cleanUpInfrastructure(setup.tmppath, setupCDSLRepository.cdslRepository1, setupCluster.clusterinfo)
    setupCDSLRepository.cleanUpInfrastructure(setup.tmppath)
    