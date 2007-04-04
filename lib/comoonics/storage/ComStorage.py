#!/usr/bin/python
"""
Python implementation of the Base Storage Interface to connect a modification or copyset to a storage implementation
"""

# here is some internal information
# $Id: ComStorage.py,v 1.3 2007-04-04 12:35:05 marc Exp $
#

__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/ComStorage.py,v $

from comoonics.ComExceptions import ComException
from comoonics import ComLog

class NotImplementedYet(ComException): pass
class ErrorDuringExecution(ComException):
    def __init__(self, message, nested_exception=None):
        self.message=message
        self.nested_exception=nested_exception
    def __str__(self):
        buf=self.message
        if self.nested_exception:
            buf+="\nNested Error: %s" %(self.nested_exception)
        return buf
class ModuleNotFoundException(ComException):
    def __init__(self, path):
        ComException.__init__(self, "Could not find module %s." %(path))
class IncompatibleObjectException(ComException):
    def __init__(self, cls1, cls2):
        ComException.__init__(self, "%s is no instance of %s. Incompatible Object" %(cls1.__name__, cls2.__name__))

class Storage(object):
    """
    Baseclass for storagesystem implementations. All supported methods should be implemented. If not an exception is
    raised.
    """
    __logStrLevel__="Storage"

    def getStorageObject(implementation, the_element):
        """ returns the storage object by the implementation attribute and the given element."""
        module=__import__(implementation)
        for i in implementation.split(".")[1:]:
            module = getattr(module, i)
        if module:
            cls=None
            for key in module.__dict__.keys():
                import inspect
                if inspect.isclass(getattr(module, key)) and inspect.getclasstree([getattr(module, key)], True)[0][0] == Storage:
                    cls=getattr(module, key)
                    break
            if cls:
                try:
                    inst=object.__new__(cls)
                    log.debug("class is %s" %(cls))
                    inst.__init__(element=the_element)
                    connname=inst.getConnectionName()
                    if not StorageConnections.has_key(connname):
                        log.debug("Creating new storage connection %s %s" %(connname, StorageConnections.keys()))
                        StorageConnections[connname]=inst
                        return inst
                    else:
                        log.debug("Returning already established storage connection %s" %(connname))
                        return StorageConnections[connname]
                except:
                    import traceback
                    traceback.print_exc()
                    raise IncompatibleObjectException(cls, Storage)
            else:
                raise IncompatibleObjectException(getattr(module, key), Storage)
        else:
            raise ModuleNotFoundException(implementation)
    getStorageObject=staticmethod(getStorageObject)

    def __init__(self, **kwds):
        """ Default constructor does nothing here. Except saving the parameters in attributes."""
        self.system=self.username=self.password=""
        if kwds.has_key("system"):
            self.system=kwds["system"]
        if kwds.has_key("username"):
            self.username=kwds["username"]
        if kwds.has_key("password"):
            self.password=kwds["password"]
        if kwds.has_key("element"):
            self.fromElement(kwds["element"])

    def fromElement(self, element):
        """
        initializes Storage connection from element.
        First properties are read and then attributes in the element. Results to attributes precedence.
        """
        from comoonics.ComProperties import Properties
        props=element.getElementsByTagName(Properties.TAGNAME)
        #log.debug("fromElement: %s, %u" %(element, len(props)))
        if len(props)>=1:
            self.properties=Properties(props[0])
            for propertyname in self.properties.keys():
                log.debug("fromElement: Setting attribute %s, %s" %(propertyname, self.properties[propertyname].getAttribute("value")))
                setattr(self, propertyname, self.properties[propertyname].getAttribute("value"))
        for attribute in element.attributes:
            self.__dict__[attribute.name]=attribute.value
#            log.debug("fromElement: attribute(%s)=%s" %(attribute.name, getattr(self, attribute.name)))

    def getConnectionName(self):
        """ for singleton implementation if you want to have only one connection per storage system you can use
        this string as unique reference.
        Returns the self.system
        """
        return self.system

    def isConnected(self):
        """ Returns True if this instance is already connected to the storagesystem or otherwise False.
        Default is False."""
        return False

    def connect(self):
        """ Connects to the storage system """
        raise NotImplementedYet()

    def map_luns(self, dest, source=None):
        """ Lunmaps the given disk. Hosts and luns are integrated insite the disk. """
        raise NotImplementedYet()

    def unmap_luns(self, dest, source=None):
        """ Lunmaps the given disk (dest). Hosts and luns are integrated insite the disk. """
        raise NotImplementedYet()

    def add(self, dest, source=None):
        """ Adds the given disk (dest). Parameters are packed as properties insite the disk. """
        raise NotImplementedYet()
    def add_snapshot(self, dest, source=None):
        """ Snapshots the given sourcedisk to destdisk. Options are packed as properties insite of destdisk."""
        raise NotImplementedYet()

    def add_clone(self, dest, source=None):
        """ Clones the given sourcedisk to destdisk. Options are packed as properties insite of destdisk. """
        raise NotImplementedYet()

    def delete(self, dest, source=None):
        """ Deletes the given disk (dest). If you only want to support the deleting of snapshots use delete_snaphot. """
        raise NotImplementedYet()

    def delete_snapshot(self, dest, source=None):
        """ Deletes the given disk (dest) only if its a snapshot. """
        raise NotImplementedYet()

    def delete_clone(self, dest, source=None):
        """ Deletes the given disk(dest) only if its a clone. """
        raise NotImplementedYet()

    def close(self):
        """ Cleans up and closes all open connections to the storagesystem """

log=ComLog.getLogger(Storage.__logStrLevel__)
log.debug("IMPORTING: "+__name__)
StorageConnections=dict()

def main():
    pass

if __name__ == '__main__':
    main()

########################
# $Log: ComStorage.py,v $
# Revision 1.3  2007-04-04 12:35:05  marc
# MMG Backup Legato Integration :
# - just logging
#
# Revision 1.2  2007/03/26 08:10:22  marc
# - better logging
# - added support for XML-properties
#
# Revision 1.1  2007/02/09 11:36:16  marc
# initial revision
#