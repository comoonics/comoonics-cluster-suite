'''
Created on Mar 3, 2010

@author: marc
'''
    
def test():
    from comoonics import ComLog
    import logging
    from comoonics.assistant.ComECAssistantController import ECAssistantController
    from comoonics.assistant.ComAssistantTui import AssistantTui 
    ComLog.setLevel(logging.DEBUG)
    ac=ECAssistantController("./localclone.xml", "./infodef.xml", "/opt/atix/comoonics-cs/xsl/localclone.xsl", scan=True)
    ac2=ECAssistantController("./createlivecd.xml", "./createlivecd.infodef.xml", scan=True)

    at = AssistantTui([ac2, ac])
    result = at.run()
#    at.cleanup()
#    ac.printDocument()
    
if __name__=="__main__":
    test()
