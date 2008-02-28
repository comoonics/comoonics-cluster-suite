"""
@todo Add some comments
"""

#TODO: add support for multiple value containers

class AssistantInfo(object):
    def __init__(self, container, attr_name, attr_type, comment=None, validator=None, helper=None):
        self.data=[ container ]
        self.attr_type=attr_type
        self.attr_name=attr_name
        self.validator=validator
        self.helper=helper
        self.comment=comment
        self.suggestions=[]
        self.manual=""
        self.default=self.getValue()
        
    def __str__(self):
        return "\n".join(( "current %s" %self.getValue(), \
                 "default %s" %self.default, \
                 "suggestions %s" %" ".join(self.suggestions), \
                 "manual %s" %self.manual)) 

    def addContainer(self, container):
        self.data.append(container)

 
    def setName(self, name):
        self.attr_name=name
    
    def getName(self):
        return self.attr_name
 
    def setValue(self, val):
        pass

    def getValue(self):
        pass

    def setDefault(self, default):
        self.default=default
        
    def getDefault(self):
        return self.default
    
    def setSuggestions(self, suggestions):
        self.suggestions=suggestions
    
    def getSuggestions(self):
        return self.suggestions
    
    def addSuggestion(self, suggestion):
        self.suggestions.append(suggestion)
    
    def setManual(self, manual):
        self.manual=manual
        
    def getManual(self):
        return self.manual

    def getType(self):
        return self.attr_type

    def setValidator(self, validator):
        self.validator=validator
    
    def getValidator(self):
        return self.validator    

    def setHelper(self, helper):
        self.helper=helper

    def getHelper(self):
        return self.helper
    
    def hasHelper(self):
        if self.helper:
            return True
        return False
    
    def setComment(self, comment, lang=None):
        self.comment=comment

    def getComment(self, lang=None):
        if not self.comment:
            return "No addittional information available"
        return self.comment

    def scan(self):
        if self.hasHelper():
            self.setSuggestions(self.getHelper().scan())
            
    
    def validate(self):
        pass

            

class AttrAssistantInfo(AssistantInfo):
    def __init__(self, attr, attr_name, attr_type, comment=None, validator=None, helper=None, doc=None):
        AssistantInfo.__init__(self, attr, attr_name, attr_type, comment, validator, helper)   
       
    def getValue(self):
        return self.data[0].nodeValue
 
    def setValue(self, val):
        for _elem in self.data:
            _elem.nodeValue=val
    
    