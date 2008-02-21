""" 
Helper Classes for Comoonics Assistant
"""

from comoonics import ComSystem, ComLog

__logStrLevel__="comoonics.assistant.ComAssistantHelper"

def createAssistantHelper(classname, query):
    if classname:
        try: 
            print "Classname:%s" %classname
            return eval(classname)(query)
        except Exception:
            ComLog.getLogger(__logStrLevel__).warning("Assitanthelper %s coud not be initialized" %classname)


class AssistantHelper(object):
    """
    @todo: add some comments
    """
    
    def __init__(self, query):
        self.query=query
    
    def scan(self):
        """
        starts the helper scan process and returns an array of estimated results
        """ 
        return
    
class KernelAssistantHelper(AssistantHelper):
    """
    check for the current kernel version
    """
    
    def scan(self):
        if self.query=="version":
            return self.scan_release()
        if self.query=="processor":
            return self.scan_processor()
        
        return self.scan_release()
        
            
    def scan_processor(self):
       _ret = ComSystem.execLocalOutput("uname -p") 
       return _ret[0].strip("\n")
        
    
    def scan_release(self):
       _ret = ComSystem.execLocalOutput("uname -r") 
       return _ret[0].strip("\n")
   
   