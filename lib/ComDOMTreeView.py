#!/usr/bin/env python
'''
Tree View/Generic Tree Model

This test is designed to demonstrate creating a new type of tree model
in python for use with the new tree widget in gtk 2.0.
'''

import gtk
import gobject
from xml.dom.minidom import parseString
from xml.dom.ext.reader import Sax2
import xml.dom
import sys
import os
from xml.dom.NodeFilter import NodeFilter

def acceptElements(model, iter):
    if not model.get_value(iter, DOMModel.COLUMN_NODE):
        return False
    node=model.get_value(iter, DOMModel.COLUMN_NODE).get_data(DOMTreeModel.NODE_KEY)
    if node.nodeType == node.ELEMENT_NODE:
        return True
    else:
        return False
        
def acceptAttributes(model, iter):
    if not model.get_value(iter, DOMModel.COLUMN_NODE):
        return False
    node=model.get_value(iter, DOMModel.COLUMN_NODE).get_data(DOMTreeModel.NODE_KEY)
    if node.nodeType == node.ATTRIBUTE_NODE:
        return True
    else:
        return False

class DOMModel:
    NODE_KEY="node"
    (
      COLUMN_NAME,
      COLUMN_VALUE,
      COLUMN_EDITABLE,
      COLUMN_NODE
     ) = range(4)


class DOMTreeModel(gtk.TreeStore, DOMModel):
    def __init__(self, node):
        gtk.TreeStore.__init__(self, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_BOOLEAN, gobject.TYPE_OBJECT)
        self.createStoreModelFromNode(node)

    def createStoreModelFromNode(self, node, parent=None):
        iter=self.append(parent)
        gobj=gobject.GObject()
        gobj.set_data(DOMTreeModel.NODE_KEY, node)
        self.set_value(iter, DOMModel.COLUMN_NAME, node.nodeName)
        self.set_value(iter, DOMModel.COLUMN_VALUE, node.nodeValue)
        self.set_value(iter, DOMModel.COLUMN_EDITABLE, False)
        self.set_value(iter, DOMModel.COLUMN_NODE, gobj)
        for child in node.childNodes:
            self.createStoreModelFromNode(child, iter)

class DOMListModel(gtk.ListStore, DOMModel):
    def __init__(self, node):
        gtk.ListStore.__init__(self, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_BOOLEAN, gobject.TYPE_OBJECT)
        self.createStoreModelFromNode(node)

    def createStoreModelFromNode(self, node):
        iter=self.append()
        print "Node: %s, %s" % (node.nodeName, node.nodeValue)
        gobj=gobject.GObject()
        gobj.set_data(DOMTreeModel.NODE_KEY, node)
        self.set_value(iter, DOMModel.COLUMN_NAME, node.nodeName)
        self.set_value(iter, DOMModel.COLUMN_VALUE, node.nodeValue)
        self.set_value(iter, DOMModel.COLUMN_EDITABLE, True)
        self.set_value(iter, DOMModel.COLUMN_NODE, gobj)
        if node.attributes:
            for child in node.attributes:
                self.createStoreModelFromNode(child)
         
class DOMNodeView(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)
        renderer = gtk.CellRendererText()
        renderer.set_property("xalign", 0.0)
        column = gtk.TreeViewColumn("Name", renderer, text=DOMModel.COLUMN_NAME)
        #column = gtk_tree_view_get_column(GTK_TREE_VIEW(treeview), col_offset - 1);
        column.set_clickable(True)
        # self.get_selection().set_mode(gtk.SELECTION_SINGLE)

        self.append_column(column)

       #column = gtk_tree_view_get_column(GTK_TREE_VIEW(treeview), col_offset - 1);
        column = gtk.TreeViewColumn("Value", renderer, text=DOMModel.COLUMN_VALUE, editable=DOMModel.COLUMN_EDITABLE)
        #column = gtk_tree_view_get_column(GTK_TREE_VIEW(treeview), col_offset - 1);
        column.set_clickable(True)
        # self.get_selection().set_mode(gtk.SELECTION_SINGLE)

        self.append_column(column)

class DOMTreeViewTest(gtk.Window):
    def __init__(self, node, dtd, parent=None):
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: gtk.main_quit())
        self.set_title(self.__class__.__name__)
        self.set_default_size(650, 400)
        self.set_border_width(8)
        self.dtd=dtd

        label = gtk.Label("DOMTreeViewer")

        # create model
        # create treeview
        basemodell=DOMTreeModel(node)
        basemodelr=DOMListModel(node)
        modelfilterl=basemodell.filter_new()
        modelfilterl.set_visible_func(acceptElements)
        modelfilterr=basemodelr.filter_new()
        modelfilterr.set_visible_func(acceptAttributes)
        treeview = DOMNodeView()
        treeview.set_model(modelfilterl)
        treeview.set_rules_hint(True)
        listview = DOMNodeView()
        listview.set_model(modelfilterr)
        listview.set_rules_hint(True)

        # expand all rows after the treeview widget has been realized
        treeview.connect('realize', lambda tv: tv.expand_all())
        treeview.get_selection().connect("changed", self.selection_changed, basemodelr, modelfilterr)
        treeview.connect_object("button-press-event", self.button_press, treeview)
        
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(treeview)

        framel = gtk.Frame()
        framel.set_shadow_type(gtk.SHADOW_IN)
        framel.set_size_request(200, 200)
        framel.add(sw)
        
        framer = gtk.Frame()
        framer.set_shadow_type(gtk.SHADOW_IN)
        framer.set_size_request(200, 200)
        framer.add(listview)
        
        hpaned = gtk.HPaned()
        hpaned.add1(framel)
        hpaned.add2(framer)
        vbox = gtk.VBox(False, 8)
        vbox.pack_start(label, False, False)
        vbox.add(hpaned)
        self.add(vbox)
        self.show_all()
        
    def selection_changed(self, selection, dest, filter):
        (model, iter) = selection.get_selected()
        print "Selection changed %s, %s, %s %s" % (model, iter, dest, filter)
        dest.clear()
        dest.createStoreModelFromNode(model.get_value(iter, DOMModel.COLUMN_NODE).get_data(DOMModel.NODE_KEY))
        if filter:
            filter.refilter()
    
    def button_press(self, widget, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            try:
                path, column, cell_x, cell_y = widget.get_path_at_pos(event.x, event.y)
                iter = widget.get_model().get_iter(path)
                selection = widget.get_selection()
                selection.select_path(path)
            except TypeError, e:
                return False
            __menu = gtk.Menu()
            __model, __i = widget.get_selection().get_selected()
            __item=AddAttributeMenuItem(widget.get_selection(), self.dtd)
            __item.registerListener(self)
            __menu.append(__item)
            __menu.append(DeleteAttributeMenuItem(widget.get_selection()))
            __item=AddElementMenuItem(widget.get_selection(), self.dtd)
            __menu.append(__item)
            __item.registerListener(self)
            __menu.append(DeleteElementMenuItem(widget.get_selection()))
            __menu.popup(None, None, None, event.button, event.time)
            
    def add_element(self, item, model, name):
        print "Menu Add Element... " + name + " pressed"

    def delete_element(self, item, model, name):
        print "Menu Add Element... " + name + " pressed"
 
    def add_attribute(self, item, model, name):
        print "Menu Add Attribute... " + name + " pressed"
    
    def delete_attribute(self, item, model, name):
        print "Menu Add Element... " + name + " pressed"
    
    """ 
    private methods
    """

class AddElementMenuItem(gtk.MenuItem):
    def __init__(self, selection, dtd, label="add Element..."):
        gtk.MenuItem.__init__(self, label)       
        self.items=list()
        self.set_submenu(self.createMenu(selection, dtd))
        self.show()  
        
    
    def registerListener(self, listener):
        for i in range(len(self.items)):
            self.items[i][0].connect("activate", listener.add_element, \
                                     self.items[i][1], self.items[i][2])

    def createMenu(self, selection, dtd):
        __menu = gtk.Menu()
        __model, __i = selection.get_selected()
        __node = __model.get(__i, DOMModel.COLUMN_NODE)[0]
        __attr = ContentModelHelper(dtd).getValidElementNames(__node.get_data(DOMTreeModel.NODE_KEY))
        for i in range(len(__attr)):
            __item = gtk.MenuItem(__attr[i])
            __menu.append(__item)
            self.items.append([__item, __model, __attr[i]])
            __item.show()
        __menu.show()
        return __menu
    

class DeleteElementMenuItem(gtk.MenuItem):
    def __init__(self, selection, label="delete"):
        gtk.MenuItem.__init__(self, label)
        self.show()
        
        
class AddAttributeMenuItem(gtk.MenuItem):
    def __init__(self, selection, dtd, label="add Attribute..."):
        gtk.MenuItem.__init__(self, label)
        self.items=list()
        self.set_submenu(self.createMenu(selection, dtd))
        self.show()  
        
    def registerListener(self, listener):
        for i in range(len(self.items)):
            self.items[i][0].connect("activate", listener.add_attribute, \
                                     self.items[i][1], self.items[i][2])    
        
    def createMenu(self, selection, dtd):
        __menu = gtk.Menu()
        __model, __i = selection.get_selected()
        __node = __model.get(__i, DOMModel.COLUMN_NODE)[0].get_data(DOMTreeModel.NODE_KEY)
        __attr = dtd.get_elem(__node.tagName).get_attr_list()
        for i in range(len(__attr)):
            if not __node.hasAttribute(__attr[i]):
                __item = gtk.MenuItem(__attr[i])
                __menu.append(__item)
                self.items.append([__item, __model, __attr[i]])
                __item.show()
        __menu.show()
        return __menu
       
    
class DeleteAttributeMenuItem(gtk.MenuItem):
    def __init__(self, selection, label="delete Attribute..."):
        gtk.MenuItem.__init__(self, label)
        self.set_submenu(self.createMenu(selection))
        self.show()           
            
    def createMenu(self, selection):
        __menu = gtk.Menu()
        __model, __i = selection.get_selected()
        __node = __model.get(__i, DOMModel.COLUMN_NODE)[0]
        __elem= __node.get_data(DOMTreeModel.NODE_KEY)
        __attr = __elem.attributes
        for i in range(len(__attr)):
            __item = gtk.MenuItem(__attr[i].name)
            __menu.append(__item)
            __item.show()
        __menu.show()
        return __menu
            
            
class ContentModelHelper:
    def __init__(self, dtd):
        self.dtd=dtd
    
    def getValidElementNames(self, element):
        __elem=self.dtd.get_elem(element.tagName)
        __sstate=__elem.get_start_state()
        __elementlist=list()
        __nodes=element.childNodes
        self.fillList(__elementlist, __elem, __sstate)
        return __elementlist
    
    def fillList(self, elements, element, state): 
        __el = element.get_valid_elements(state)
        for i in range(len(__el)):
            print "processing " + __el[i]
            if not elements.count(__el[i]):
                print __el[i] + " is not in " + str(elements)
                elements.append(__el[i])
                if not element.final_state(state):
                    print "calling fillist with next state"
                    self.fillList(elements, element, element.next_state(state, __el[i]))
       
        
        

def main():
    reader = Sax2.Reader(validate=1)
    filename="../test/gfs-node1-clonetest.xml"
    if len(sys.argv) > 1:
        filename=sys.argv[1]
    file=os.fdopen(os.open(filename,os.O_RDONLY))
    doc = reader.fromStream(file)
    dtd=reader.parser._parser.get_dtd()
    dtv=DOMTreeViewTest(doc.documentElement, dtd)
    gtk.main()

if __name__ == '__main__':
    main()
