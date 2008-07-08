#!/usr/bin/python
"""
Collection of dict tools
"""

__version__= "$Revision $"

from comoonics import ComLog

from xml.dom.ext.reader.Sax2 import implementation

logger=ComLog.getLogger("comoonics.DictTools")

def searchDict(hash,searchedElement):
    """
    Searches for a given key in a nested dictionary
    @param hash: Dictionary to seach in
    @type hash: L{dict}
    @param searchedElement: key to search for
    @type searchedElement: L{string}
    @return: Returns if the given string is found as key in given hash
    @rtype: L{Boolean}
    """
    for (key, value) in hash.items():
        if key == searchedElement:
            return True
        else:
            #dicts are used to represent the different layers in the (later) xml
            if type(value) == dict:
                if searchDict(value,searchedElement) == True: return True
            #list are used to define more than one element with same name
            elif type(value) == list:
                for element in value:
                    if searchDict(element,searchedElement) == True: return True
    return False

def applyDefaults(hash,defaults):
    """
    Applies default values to a given hash. Hash and default values 
    has to be available as a dict with the same structure.
    @param hash: hash to apply defaults to
    @type hash: L{dict}
    @param defaults: defaults to apply
    @type defaults: L{dict}
    @return: hash with applied default values
    @rtype: L{dict} 
    """
    for (key,value) in defaults.items():
        # if hash does not contain any value for a key defined in default, use 
        # key/value pair from defaults
        if not hash.has_key(key):
            hash[key] = value
        # if a nested structure is found, continue recursively
        elif type(defaults[key]) == dict and type(hash[key]) == dict:
            hash[key] = applyDefaults(hash[key],defaults[key])
        # a special nested structure, used to handle elements whose names appear 
        # several times on the same level
        # split list and for each continue recursively
        elif type(defaults[key]) == list and type(hash[key]) == list:
            for i in range(len(hash[key])):
                hash[key][i] = applyDefaults(hash[key][i],defaults[key][0])
        # if hash already contains a value which is defined in defaults, pass default 
        # value and keep hash value
        elif type(defaults[key]) == type(hash[key]):
            pass
        # if type(defaults[key]) == type(hash[key]) which was queried above is false, 
        # the structure of hash and defaults differ - this is not allowed!
        else:
            raise AttributeError("Keys from hash and defaults don't fit! key: %s, %s!=%s. Information: Structure of given hash " %(key, type(defaults[key]), type(hash[key])) + str(hash) + " and defaults " + str(defaults) + " differs, could not proceed")
            
    return hash

def createDomFromHash(hash,doc=None,element=None,defaults=None):
    """
    Creates or manipulates a DOM from given hash.
    @param hash: Hash to create DOM
    @type hash: L{dict}
    @param doc: if given, expand given DOM instead of creating a new one
    @type doc: L{DOM}
    @param element: element in doc to work on
    @param defaults: default values to apply to hash 
    @type defaults: L{dict}
    @return: XML-Dom-Element created from hash
    @return: returns a new or extended DOM which (partly) represents the given hash
    @rtype: L{DOM}
    """
    
    #apply defaults
    if defaults != None:
        hash = applyDefaults(hash, defaults)
    
    #create dom or use given dom
    if doc==None:            
        doc = implementation.createDocument(None,hash.keys()[0],None)
        newelement = doc.documentElement                
    else:
        newelement = doc.createElement(hash.keys()[0])                    
        element.appendChild(newelement)
    
    #extend given dom or fill new dom
    _tmp = hash[hash.keys()[0]]
    for i in _tmp.keys():
        if (type(_tmp[i]) != dict) and (type(_tmp[i]) != list):
            newelement.setAttribute(str(i),str(_tmp[i]))
        elif type(_tmp[i]) == list:
            for element in _tmp[i]:
                createDomFromHash({i:element},doc,newelement)
        else:
            _tmp2 = {i: _tmp[i]}
            createDomFromHash(_tmp2,doc,newelement)
    
    return doc