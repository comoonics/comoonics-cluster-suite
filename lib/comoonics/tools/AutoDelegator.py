#!/usr/bin/python
"""
An Autodelegator class copied the from O'Reilly Python Cookbook
"""

from comoonics import ComLog

logger=ComLog.getLogger("comoonics.tools.AutoDelegator")

class AutoDelegator(object):
    delegates=list()
    do_not_delegate=list()
    _cash=dict()
    autocash=True
    def __getattr__(self, key, _super=False, with_delegator=True):
        #logger.debug("__getattr__(%s, %s)" %(key, _super))
        if _super:
            _attr=super(AutoDelegator, self).__getattr__(self, key)
        if key not in self.do_not_delegate:
            try:
                if not with_delegator:
                    return self.__getattr__(key, True)
            except AttributeError:
                pass
            for d in self.delegates:
                if self.autocash:
                    try:
                        return self._cash[key]
                    except KeyError:
                        pass
                try:
                    _attr=getattr(d, key)
                    if self.autocash:
                        self._cash[key]=_attr
                    return _attr
                except AttributeError:
                    pass
        raise AttributeError, key

class _Pricing(AutoDelegator):
    def __init__(self, location, event):
        self.delegates=[location, event]
    def setlocation(self, location):
        self.delegates[0]=self.localtion
    def getprice(self):
        return self.delegates[0].getprice()*self.delegates[1].getdiscount()

class _Location(object):
    def __init__(self, price, quantity):
        self.price=price
        self.quantity=quantity
    def getprice(self):
        return self.price
    def getquantity(self):
        return self.quantity
class _Event(object):
    def __init__(self, discount):
        self.discount=discount
    def getdiscount(self):
        return self.discount

def __main__():
    _pricing=_Pricing(_Location(5, 10), _Event(0.9))
    print "_pricing.getprice(): %f" %_pricing.getprice()
    print "_pricing.getquantity(): %u" %_pricing.getquantity()
    print "_pricing.getdiscount(): %f" %_pricing.getdiscount()

if __name__=="__main__":
    __main__()