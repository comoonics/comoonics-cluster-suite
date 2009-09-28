#!/usr/bin/python
"""analysis.graphviz.ComGraphvizWriters

writers to write graphviz graphs of analysis datastructures if need be

"""

# here is some internal information
# $Id $
#

import logging
import sys
from comoonics.analysis.ComGLockWriters import DefaultGLockWriter, addLockdumpWriter
from comoonics.analysis.ComObjects import Holder, Waiter
import types

__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/analysis/graphviz/ComGraphvizWriters.py,v $

class GraphvizGLockWriter(DefaultGLockWriter):
    GRAPHVIZLIB_PATH="/usr/lib/graphviz/python"
    NAME="graphviz"
    logger=logging.getLogger("comoonics.ComGFS.GraphvizWriter")
    WAITER_NAMES=["Waiter3"]
    LOCK_NODE_ATTRS={ "shape": "circle" }
    PID_NODE_ATTRS={ "shape": "doublecircle"}
    CONNECTION_ATTRS={ "Holder":  { "label" : Holder.getConnectionName},
                       "Waiter3": { "label" : Waiter.getConnectionName, "arrowhead": "invdot" } }
    
    def __init__(self, _out=sys.stdout):
        self.format="svg"
        self.layout="dot"
        sys.path.append(self.GRAPHVIZLIB_PATH)
        import gv
        super(GraphvizGLockWriter, self).__init__(_out)
        self.graph=gv.graph("glockdump")

    # graphvizmethods
    def setNodeAttrs(self, _node, _attrs):
        import gv
        for _name, _value in _attrs.items():
            if type(_value)==types.MethodType:
                gv.setv(_node, _name, _value())
            else:
                gv.setv(_node, _name, _value)
            
    def setEdgeAttrs(self, _edge, _attr_dict, _type):
        import gv
        for _name, _value in _attr_dict[_type].items():
            if type(_value)==types.MethodType:
                gv.setv(_edge, _name, _value())
            else:
                gv.setv(_edge, _name, _value)

    def createLockNode(self, _lock):
        import gv
        _node=gv.node(self.graph, _lock.getName())
        self.setNodeAttrs(_node, self.LOCK_NODE_ATTRS)
        return _node

    def createPidNode(self, _subtree):
        import gv
        _node=gv.node(self.graph, _subtree.owner)
        self.setNodeAttrs(_node, self.PID_NODE_ATTRS)
        return _node

    def connectLockPid(self, _type, _lock, _pid):
        import gv
        _edge=gv.edge(_lock, _pid)
        self.setEdgeAttrs(_edge, self.CONNECTION_ATTRS, _type)
        return _edge

    def hasHolder(self, _glock):
        if hasattr(_glock, "_children"):
            for _child in _glock.children():
                if isinstance(_child, Holder) and hasattr(_child, "owner") and int(getattr(_child, "owner")) >=0:
                    return True
        return False

    def write(self, _glock, _tabs=0, _head=True, _tail=True, _actKey=None):
        if self.hasHolder(_glock):
            _glock.decipher()
            _locknode=self.createLockNode(_glock)
            for _child in _glock.children():
                for _attr in self.PID_NODE_ATTRS.keys():
                    if type(self.PID_NODE_ATTRS[_attr])==types.MethodType:
                        self.PID_NODE_ATTRS[_attr]=getattr(_child, self.PID_NODE_ATTRS[_attr].im_func.__name__)
                if isinstance(_child, Holder):
                    for _attr in self.CONNECTION_ATTRS["Holder"].keys():
                        if type(self.CONNECTION_ATTRS["Holder"][_attr])==types.MethodType:
                            if isinstance(self.CONNECTION_ATTRS["Holder"][_attr].im_class, Holder.__class__):
                                self.CONNECTION_ATTRS["Holder"][_attr]=getattr(_child, self.CONNECTION_ATTRS["Holder"][_attr].im_func.__name__)
                            else:
                                self.CONNECTION_ATTRS["Holder"][_attr]=getattr(_glock, self.CONNECTION_ATTRS["Holder"][_attr])
                    _holdernode=self.createPidNode(_child)
                    self.connectLockPid("Holder", _locknode, _holdernode)
                elif isinstance(_child, Waiter):
                    _waitername="%s%u" %(Waiter.__name__,_child.level)
                    for _attr in self.CONNECTION_ATTRS[_waitername]:
                        if type(self.CONNECTION_ATTRS[_waitername][_attr])==types.MethodType:
                            if isinstance(self.CONNECTION_ATTRS[_waitername][_attr].im_class, Waiter.__class__):
                                self.CONNECTION_ATTRS[_waitername][_attr]=getattr(_child, self.CONNECTION_ATTRS[_waitername][_attr].im_func.__name__)
                            else:
                                self.CONNECTION_ATTRS[_waitername][_attr]=getattr(_glock, self.CONNECTION_ATTRS[_waitername][_attr])
                    
                    _waiternode=self.createPidNode(_child)
                    self.connectLockPid(_waitername, _locknode, _waiternode)
    
    def writeEnd(self):
        import gv
        gv.layout(self.graph, self.layout)
        if isinstance(self.out, basestring):
            gv.render(self.graph, self.format, self.out)
        else:
            gv.render(self.graph, self.format)
        
    def isSupported(self):
        try:
            sys.path.append(self.GRAPHVIZLIB_PATH)
            import gv
            return True
        except:
            return False

addLockdumpWriter(GraphvizGLockWriter())
