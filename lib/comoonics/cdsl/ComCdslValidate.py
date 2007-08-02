"""Comoonics cdsl validation module


Checks if all cdsl defined in given inventoryfile really exists in filesystem.
Wrotes overview about failed cdsls to logfile and prints result of validation 
(sucessfull/not sucessfull) to screen.
"""


__version__ = "$Revision: 1.1 $"

from ComCdslRepository import *
import os.path

def cdslValidate(filename="/var/lib/cdsl/cdsl_inventory.xml",logfile="/var/adm/cdsl_check_list"):
    """
    Validates cdsls in given inventoryfile against filesystem and writes informations 
    about not existing/damaged cdsls to logfile. Returns if validation was sucessfull 
    or not
    @param filename: path to cdsl-inventoryfile
    @type filename: string
    @param logfile: path to logfile to write into
    @type logfile: string
    @return: returns if validation was sucessfull (True) or not (False)
    @rtype: Boolean
    """
    cdslRepository = CdslRepository(filename,None,False)
    failed_cdsls = []
    failure = True
    
    if not cdslRepository.cdsls:
        print "No CDSL in inventoryfile found"
        return False
        
    for cdsl in cdslRepository.cdsls:
        if cdsl.exists():
            failure = False
        else:
            failed_cdsls.append([cdsl.src,cdsl.type])
    
    if failure == True:
        print "Fail CDSL inventory check. See details in " + os.path.abspath(logfile)
        if os.path.exists(logfile):
            os.remove(logfile)
        elif not os.path.exists(os.path.dirname(logfile)):
            os.makedirs(os.path.dirname(logfile))
        logfailed = file(logfile,"w")
        for cdsl in failed_cdsls:
            logfailed.write("Expected CDSL " + cdsl[0] + " of type " + cdsl[1] + "\nAn administrator or application has removed/damaged this cdsl\n\n")
        logfailed.close()
        return False
    else:
        print "Sucessful CDSL inventory check"
        return True

def main():
    """
    Validate test/cdsl4.xml as a test.
    """
    #ComLog.setLevel(logging.INFO)
    cdslValidate("test/cdsl4.xml","test/logfile")

if __name__ == '__main__':
    main()