"""
@todo Add some comments
"""

class AssistantInfo(object):
    def __init__(self, container, attr_name, attr_type, comment=None, validator=None, helper=None):
        self.data=container
        self.attr_type=attr_type
        self.attr_name=attr_name
        self.validator=validator
        self.helper=helper
        self.comment=comment
 
    def getName(self):
        return self.attr_name
 
    def getValue(self):
        pass
    
    def getType(self):
        return self.attr_type
    
    def setValue(self, val):
        pass

    def getValidator(self):
        return self.validator    
    
    def getHelper(self):
        return self.helper
    
    def getComment(self, lang=None):
        return self.comment


class AttrAssistantInfo(AssistantInfo):
    def __init__(self, attr, attr_name, attr_type, comment=None, validator=None, helper=None, doc=None):
        AssistantInfo.__init__(self, attr, attr_name, attr_type, comment, validator, helper)   
       
    def getValue(self):
        return self.data.nodeValue
 
    def setValue(self, val):
        self.data.nodeValue=val
    
    