"""
The controller class for the comoonics assistant  manager
"""

import dircache
import os
import shutil

from comoonics.ComExceptions import ComException

class TypeNotMatchError(ComException):
    pass

class ConfigError(ComException):
    pass

class ConfigurationManager(object):
    
    def __init__ (self, path="/etc/comoonics/enterprisecopy/xml-dr"):
        self.path=os.path.normpath(path)
        self.store=ConfigurationStore()

    def setConfigPath(self, path):
        self.path=path
        
    def getConfigPath(self):
        return self.path
    
    def getConfigStore(self):
        return self.store
        
    def getCompleteConfigSetNames(self):
        sets={}
        for tstore in self.store.getConfigTypeStores():
            _all_dirs=tstore.getConfigInfodefset().getDirections()
            for set in tstore.getConfigsets():
                if set.hasDirections(_all_dirs):
                    sets[set.getName()] = tstore.getType()
        return sets
    
    def getCompleteConfigTemplateSetNames(self):
        sets=[]
        for tstore in self.store.getConfigTypeStores():
            _all_dirs=tstore.getConfigInfodefset().getDirections()
            if not tstore.hasConfigTemplateset(_all_dirs): continue
            if not tstore.hasConfigInfodefset(_all_dirs): continue
            sets.append(tstore.getType())
        return sets
    
   
    def createConfigSet(self, name, type):
        #TODO add check for existence.
        # check if a complete template set is available
        if not self.store.hasConfigTypeStore(type):
            raise ConfigError("type %s not valid" %type)
        tstore = self.store.getConfigTypeStoreByName(type)
        _all_dirs=tstore.getConfigInfodefset().getDirections()
        if not tstore.hasConfigTemplateset(_all_dirs):
            raise ConfigError("Templateset for type %s is not complete" %type)
        tset=tstore.getConfigTemplateset()
        for dir in _all_dirs:
            dpath=os.path.normpath("%s/%s.%s.config.%s.xml" %(self.getConfigPath(), type, dir, name))
            shutil.copyfile(tset.getConfiguration(dir).getConfigFile(), dpath)
            self.store.addConfig(Configuration(type, dir, "config", name, dpath))
            
    def deleteConfigSet(self, name, type):
        if not self.store.hasConfigTypeStore(type):
            raise ConfigError("type %s not valid" %type)
        tstore = self.store.getConfigTypeStoreByName(type)
        set = tstore.getConfigset(name)
        for config in set.getConfigurations():
           os.rename(config.getConfigFile(), "%s.bak" % config.getConfigFile())
        self.store.removeConfigSet(type, name)
        
    def renameConfigSet(self, name, type, newname):
        if not self.store.hasConfigTypeStore(type):
            raise ConfigError("type %s not valid" %type)
        tstore = self.store.getConfigTypeStoreByName(type)
        set = tstore.getConfigset(name)
        for config in set.getConfigurations():
            _oldpath=config.getConfigFile()
            _newpath="%s/%s.%s.config.%s.xml" %(self.getConfigPath(),config.getType(), config.getDirection(), newname)
            os.rename(_oldpath, _newpath)
            config.setName(newname)
            config.setConfigFile(_newpath)
        set.setName(newname)
        tstore.removeConfigset(name)
        tstore.addConfigset(newname, set)
        
        
    def scanConfigs(self, path = None):
        if not path:
            path = self.path
        path = os.path.normpath(path)
        dirents=dircache.listdir(path)
        #configfile :: <type>.backup|restore.config|template|infodef.<name>.xml
        for ent in dirents:
            enparts=ent.split(".")
            # must have at least 4 fields
            if len(enparts) < 5: continue
            # must end with .xml
            if enparts[len(enparts)-1] != "xml": continue
            # we  need .config files here
            if enparts[2] != "config": continue
            self.store.addConfig(Configuration(enparts[0], enparts[1], enparts[2], enparts[3], "%s/%s" %(path, ent)))

    def scanConfigTemplates(self, path = None):
        if not path:
            path = self.path
        path = os.path.normpath(path)
        dirents=dircache.listdir(path)
        #configfile :: <type>.backup|restore.config|template|infodef.xml
        for ent in dirents:
            enparts=ent.split(".")
            # must have at least 4 fields
            if len(enparts) < 4: continue
            # must end with .xml
            if enparts[len(enparts)-1] != "xml": continue
            # we  need .config files here
            if enparts[2] != "template": continue
            self.store.addConfigTemplate(Configuration(enparts[0], enparts[1], enparts[2], enparts[0], "%s/%s" %(path, ent)))
            
    def scanConfigInfodefs(self, path = None):
        if not path:
            path = self.path
        path = os.path.normpath(path)
        dirents=dircache.listdir(path)
        #configfile :: <type>.backup|restore.config|template|infodef.xml
        for ent in dirents:
            enparts=ent.split(".")
            # must have at least 4 fields
            if len(enparts) < 4: continue
            # must end with .xml
            if enparts[len(enparts)-1] != "xml": continue
            # we  need .config files here
            if enparts[2] != "infodef": continue
            self.store.addConfigInfodef(Configuration(enparts[0], enparts[1], enparts[2], enparts[0], "%s/%s" %(path, ent)))
            


    def printConfigSets(self):
        for store in self.store.getConfigTypeStores():
            print store
    
class ConfigurationStore(object):
    def __init__(self):
        self.store={}
    
    def getConfigTypeNames(self):
        return self.store.keys()
    
    def getConfigTypeStores(self):
        return self.store.values()
    
    def getConfigTypeStoreByName(self, name):
        return self.store.get(name)
    
    def hasConfigTypeStore(self, name):
        return self.store.has_key(name)
    
    def addConfig(self, config):
        __type = config.getType()
        if not self.store.has_key(__type):
            self.store[__type]=ConfigurationTypeStore(__type)
        tstore=self.store.get(__type)
        __name = config.getName()
        if not tstore.hasConfigset(__name):
            tstore.addConfigset(__name, ConfigurationSet(__name))
        tstore.getConfigset(__name).addConfiguration(config)
        
    def removeConfigSet(self, type, name):
        tstore=self.store.get(type)
        tstore.removeConfigset(name)
        

    def addConfigTemplate(self, config):
        __type = config.getType()
        if not self.store.has_key(__type):
            self.store[__type]=ConfigurationTypeStore(__type)
        tstore=self.store.get(__type)
        __name = config.getName()
        tstore.getConfigTemplateset().addConfiguration(config)

    def addConfigInfodef(self, config):
        __type = config.getType()
        if not self.store.has_key(__type):
            self.store[__type]=ConfigurationTypeStore(__type)
        tstore=self.store.get(__type)
        __name = config.getName()
        tstore.getConfigInfodefset().addConfiguration(config)

            
class ConfigurationTypeStore(object):
    def __init__(self, type):
        self.type=type
        self.store={}
        self.infodefset=ConfigurationSet(type)
        self.templateset=ConfigurationSet(type)
        
    def getType(self):
        return self.type
    
    def addConfigset(self, name, configset):
        self.store[name]=configset
        
    def removeConfigset(self, name):
        self.store.pop(name)
        
    def hasConfigset(self, name, directions=[]):
        if not self.store.has_key(name): return False
        return self.getConfigset(name).hasDirections(directions)
            
    def hasConfigTemplateset(self, directions = None):
        return self.templateset.hasDirections(directions)
   
    def hasConfigInfodefset(self, directions = None):
        return self.infodefset.hasDirections(directions)
   
    def getConfigsetNames(self):
        return self.store.keys()
    
    def getConfigsets(self):
        return self.store.values()
   
    def getConfigset(self, name):
        return self.store.get(name)

    def getConfigTemplateset(self):
        return self.templateset

    def getConfigInfodefset(self):
        return self.infodefset
    
    
    def __str__(self):
        __str=[self.type]
        __str.append("templateset:\t"+ self.templateset.__str__())
        __str.append("infodefset:\t" +self.infodefset.__str__())
        for set in self.store.values():
             __str.append(set.__str__())
        return "\n".join(__str)
    
class ConfigurationSet(object):
    def __init__(self, name):
        self.set={}
        self.type=None
        self.name=name
        
    def addConfiguration(self, config):   
        self.setType(config.getType())
        self.set[config.getDirection()] = config
    
    def removeConfiguration(self, direction):
        self.set.pop(direction)
    
    def getConfiguration(self, direction):
        return self.set.get(direction)
    
    def getConfigurations(self):
        return self.set.values()
    
    def getDirections(self, ordered=False):
        _dirs=self.set.keys()
        if ordered:
            _dirs.sort()
        return _dirs
                
    def getName(self):
        return self.name
    
    def getType(self):
        return self.type
      
    def hasDirection(self, direction):
        return self.set.has_key(direction)
    
    def hasDirections(self, directions):
        for dir in directions:
            if not self.hasDirection(dir): return False
        return True
    
    def setName(self, name):
        self.name=name
    
    def setType(self, type):
        if self.type:
            if self.type != type:
                raise TypeNotMatchError("type of %s %s and %s do not match" %(self.getName(), self.getType(), type))
        self.type=type
       
    def __str__(self):
        __str=["ConfigSet:\tname: %s\ttype:%s" %(self.name, self.type)]
        for config in self.getConfigurations():
            __str.append("\tconfig: %s" % str(config))
        return "\n".join(__str)
        

                
class Configuration(object):
    def __init__(self, ectype, direction, filetype, name, path=None):
        self.ectype = ectype
        self.direction = direction
        self.filetype=filetype
        self.name = name
        self.path = path
    
    def setConfigFile(self, path):
        self.path=path
        
    def setName(self, name):
        self.name=name
        
    def getConfigFile(self):
        return self.path
    
    def getType(self):
        return self.ectype
    
    def getDirection(self):
        return self.direction
 
    def getFiletype(self):
        return self.filetype
    
    def getName(self):
        return self.name
    
    def __str__(self):
        return ("ectype: %s\tdirection: %s\tfiletype: %s\tname: %s\tpath: %s"
                %(self.ectype, self.direction, self.filetype, self.name, self.path))
    
def main():
    print "Testing ConfigurationManager"
    manager=ConfigurationManager("/tmp/cmtest")
    manager.scanConfigs()
    manager.scanConfigTemplates()
    manager.scanConfigInfodefs()
    print "Initial ConfigStore:"
    manager.printConfigSets()
    manager.createConfigSet("newname", "type1")
    print "Created new ConfigSet:"
    manager.printConfigSets()
    manager.deleteConfigSet("newname", "type1")
    print "Deleted ConfigSet:"
    manager.printConfigSets()
    print "complete sets:"
    print manager.getCompleteConfigSetNames()
    
if __name__=="__main__":
    main()
  