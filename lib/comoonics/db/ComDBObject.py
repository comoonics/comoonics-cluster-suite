"""
Class for object to database persistence to a generic database

"""
# here is some internal information
# $Id: ComDBObject.py,v 1.1 2008-02-28 14:19:23 marc Exp $
#
from ComDBConnection import DBConnection
from comoonics import ComLog
from comoonics.ComExceptions import ComException

import MySQLdb.converters
import ConfigParser

_dbobject_properties=ConfigParser.ConfigParser()

class NoDataFoundForObjectException(ComException): pass

def loadDBObjectsRegistry(filename):
    _dbobject_properties.read(filename)
def setDBObjectsRegistry(parser):
    global _dbobject_properties
    _dbobject_properties=parser
def registerDBObjectProperties(_classname, _properties):
    if isinstance(_classname, type):
        _classname=_classname.__name__
    _dbobject_properties.add_section(_classname)
    for key, value in _properties.items():
        _dbobject_properties.set(_classname, key, value)
def getDBObjectProperties(_classname):
    if isinstance(_classname, type):
        _classname=_classname.__name__
    _props=dict()
    for key, value in _dbobject_properties.items(_classname):
        if isinstance(value, basestring) and _dbobject_properties.has_section(value):
            value=dict(getDBObjectProperties(value))
        _props[key]=value
    return _props.items()
def hasDBObjectProperties(_classname):
    if isinstance(_classname, type):
        _classname=_classname.__name__
    return _dbobject_properties.has_section(_classname)

class DBObject(DBConnection):
    COLUMNNAMES=["id"]
    OPT_COLUMNNAMES=[]

    def __init__(self, **kwds):
        """
        Creates an instance of the jobs. The _schema attribute defines the schema of the table. It is a map with key as attribute as defined
        above and value as columnname or None. If the columnname is None it will not be used. This only holds for options.
        If @schema is None columnames are as sepecified above.
        """
        _properties=dict()
        if hasDBObjectProperties(self.__class__):
            _properties.update(getDBObjectProperties(self.__class__))
        _properties.update(kwds)
        super(DBObject, self).__init__(**_properties)
        if not _properties.has_key("schema"):
            self.schema=dict()
            for _colname in self.COLUMNNAMES:
                self.schema[_colname]=_colname
        self.schemarev=dict()
        for _key, _value in self.schema.items():
            self.schemarev[_value]=_key
        self.logger=ComLog.getLogger(self.__class__.__name__)
        self._fromdb=False
        self._todb=False

    def __getattr__(self, value):
        _fromdb=None
        if self.__dict__.has_key("_fromdb"):
            _fromdb=super(DBObject, self).__getattribute__("_fromdb")
        
        if _fromdb==False and not self.__dict__.has_key(value):
            self._fromDB()
            return super(DBObject, self).__getattribute__(value)
        else:
            return super(DBObject, self).__getattribute__(value)
        
    def __setattr__(self, name, value):
        if name in self.COLUMNNAMES:
            self._todb=True
        super(DBObject, self).__setattr__(name, value)
        
    def _getRecordSet(self):
        _query=self.selectQuery(select=self.__dict__["schema"].values(), From=self.__dict__["tablename"], where={self.__dict__["schema"]["id"]: self.__dict__["id"]})
        return _query
        
    def _fromDB(self):
        _rs=self._getRecordSet()
        if _rs.num_rows()>0:
            _obj=_rs.fetch_row(1, 1)
            for _key, _value in _obj[0].items():
                setattr(self, self.__dict__["schemarev"][_key], _value)
        else:
            raise NoDataFoundForObjectException("No data found for object. ID: %s" %str(self.id))
        self._fromdb=True

    def _getPersistentAttributes(self):
        _pairs=list()
        for _col in self.COLUMNNAMES:
            if self.schema.has_key(_col) and self.schema[_col]:
                _pairs.append('%s="%s"' %(self.schema[_col], MySQLdb.converters.Thing2Str(getattr(self, _col), "")))
        return ", ".join(_pairs)

    def commit(self):
        if self._todb:
            self._todb=False
            query="UPDATE %s SET %s WHERE %s=%s" %(self.tablename, self._getPersistentAttributes(), self.schema["id"], self.id)
            self.execQuery(query)
    
    def delete(self):
        query="DELETE FROM %s WHERE %s=%s" %(self.tablename, self.schema["id"], self.id)
        self.execQuery(query)

########################
# $Log: ComDBObject.py,v $
# Revision 1.1  2008-02-28 14:19:23  marc
# initial revision
#
