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
    #print "Filter Node %s" % node.nodeName
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
     
    def __init__(self, doc):
         self.document=doc


class DOMTreeModel(gtk.TreeStore, DOMModel):
    def __init__(self, node, doc):
        gtk.TreeStore.__init__(self, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_BOOLEAN, gobject.TYPE_OBJECT)
        DOMModel.__init__(self, doc)
        self.createStoreModelFromNode(node)
        self.document=doc

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
    def __init__(self, node, doc):
        gtk.ListStore.__init__(self, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_BOOLEAN, gobject.TYPE_OBJECT)
        DOMModel.__init__(self, doc)
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
    def __init__(self, node, dtd, doc, parent=None):
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: gtk.main_quit())
        self.set_title(self.__class__.__name__)
        self.set_default_size(650, 400)
        self.set_border_width(8)
        self.dtd=dtd

        menubar = self.create_main_menu()
        menubar.show()

        label = gtk.Label("DOMTreeViewer")

        # create model
        # create treeview
        self.__basemodell=DOMTreeModel(node, doc)
        self.__basemodelr=DOMListModel(node, doc)
        modelfilterl=self.__basemodell.filter_new()
        modelfilterl.set_visible_func(acceptElements)
        modelfilterr=self.__basemodelr.filter_new()
        modelfilterr.set_visible_func(acceptAttributes)
        self.__treeview = DOMNodeView()
        self.__treeview.set_model(modelfilterl)
        self.__treeview.set_rules_hint(True)
        self.__treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        self.__listview = DOMNodeView()
        self.__listview.set_model(modelfilterr)
        self.__listview.set_rules_hint(True)
        self.__listview.get_selection().set_mode(gtk.SELECTION_SINGLE)

        # expand all rows after the treeview widget has been realized
        self.__treeview.connect('realize', lambda tv: tv.expand_all())
        self.__treeview.get_selection().connect("changed", self.selection_changed, self.__basemodelr, modelfilterr)
        self.__treeview.connect_object("button-press-event", self.button_press, self.__treeview)
        
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.__treeview)

        framel = gtk.Frame()
        framel.set_shadow_type(gtk.SHADOW_IN)
        framel.set_size_request(200, 200)
        framel.add(sw)
        
        framer = gtk.Frame()
        framer.set_shadow_type(gtk.SHADOW_IN)
        framer.set_size_request(200, 200)
        framer.add(self.__listview)
        
        hpaned = gtk.HPaned()
        hpaned.add1(framel)
        hpaned.add2(framer)
        vbox = gtk.VBox(False, 8)
        vbox.pack_start(menubar, False, False)
        vbox.add(label)
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
            
    def add_element(self, item, model, iter, name):
        print "Menu Add Element... " + name + " pressed menuitem %s, model %s, iter %s" % (item, model, iter)
        (_model, _iter)=self.__treeview.get_selection().get_selected()
        _piter=self.__basemodell.iter_parent(_iter)
        value=_model.get_value(_iter, DOMModel.COLUMN_NODE)
        print "Value: %s" % value
        domnode=value.get_data(DOMModel.NODE_KEY)
        print "domnode: %s" % domnode
        node=self.__basemodell.document.createElement(name)
        domnode.appendChild(node)
        self.__basemodell.createStoreModelFromNode(node, iter)
        self.__treeview.set_model(self.__basemodell)
        
    def delete_element(self, item, model, iter):
        print "Menu Delete Element... " + name + " pressed menuitem %s, model %s" % (item, model)
    
    def insert_element(self, item, model, iter, name):
        print "Menu Insert Element... " + name + " pressed menuitem %s, model %s" % (item, model)

    def add_attribute(self, item, model, iter, name):
        print "Menu Add Attribute... " + name + " pressed menuitem %s, model %s" % (item, model)

    def delete_attribute(self, item, model, iter, name):
        print "Menu Delete Element... " + name + " pressed menuitem %s, model %s" % (item, model)
    
    def button_press(self, widget, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            try:
                path, column, cell_x, cell_y = widget.get_path_at_pos(int(event.x), int(event.y))
                iter = widget.get_model().get_iter(path)
                selection = widget.get_selection()
                selection.select_path(path)
            except TypeError, e:
                return False
            __menu = gtk.Menu()
            __model, __i = widget.get_selection().get_selected()
            #Add Attribute
            __item=AddAttributeMenuItem(widget.get_selection(), self.dtd)
            __item.registerListener(self)
            __menu.append(__item)
            #Delete Attribute
            __item=DeleteAttributeMenuItem(widget.get_selection())
            __item.registerListener(self)
            __menu.append(__item)
            #Add Child Element
            __item=AddElementMenuItem(widget.get_selection(), self.dtd)
            __menu.append(__item)
            __item.registerListener(self)
            #Insert Element
            __item=InsertElementMenuItem(widget.get_selection(), self.dtd)
            __menu.append(__item)
            __item.registerListener(self)
            #Delete Element
            __item=DeleteElementMenuItem(widget.get_selection())
            __menu.append(__item)
            __item.registerListener(self)
            __menu.popup(None, None, None, event.button, event.time)
    
    """ 
    private methods
    """
    def create_main_menu(self):
        # This is the ItemFactoryEntry structure used to generate new menus.
        # Item 1: The menu path. The letter after the underscore indicates an
        #         accelerator key once the menu is open.
        # Item 2: The accelerator key for the entry
        # Item 3: The callback.
        # Item 4: The callback action.  This changes the parameters with
        #         which the callback is called.  The default is 0.
        # Item 5: The item type, used to define what kind of an item it is.
        #       Here are the possible values:
        #       NULL               -> "<Item>"
        #       ""                 -> "<Item>"
        #       "<Title>"          -> create a title item
        #       "<Item>"           -> create a simple item
        #       "<CheckItem>"      -> create a check item
        #       "<ToggleItem>"     -> create a toggle item
        #       "<RadioItem>"      -> create a radio item
        #       <path>             -> path of a radio item to link against
        #       "<Separator>"      -> create a separator
        #       "<Branch>"         -> create an item to hold sub items (optional)
        #       "<LastBranch>"     -> create a right justified branch 
        __menu_items=(
            ( "/_File",         None,         None, 0, "<Branch>" ),
            ( "/File/_New",     "<control>N", self.print_hello, 0, None ),
            ( "/File/_Open",    "<control>O", self.print_hello, 0, None ),
            ( "/File/_Save",    "<control>S", self.print_hello, 0, None ),
            ( "/File/Save _As", None,         None, 0, None ),
            ( "/File/sep1",     None,         None, 0, "<Separator>" ),
            ( "/File/Quit",     "<control>Q", gtk.main_quit, 0, None ),
            ( "/_Options",      None,         None, 0, "<Branch>" ),
            ( "/Options/Test",  None,         None, 0, None ),
            ( "/_Help",         None,         None, 0, "<LastBranch>" ),
            ( "/_Help/About",   None,         None, 0, None ),
            )
        
        __accel_group = gtk.AccelGroup()

        # This function initializes the item factory.
        # Param 1: The type of menu - can be MenuBar, Menu,
        #          or OptionMenu.
        # Param 2: The path of the menu.
        # Param 3: A reference to an AccelGroup. The item factory sets up
        #          the accelerator table while generating menus.
        self.item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", __accel_group)

        # This method generates the menu items. Pass to the item factory
        #  the list of menu items
        self.item_factory.create_items(__menu_items)

        # Attach the new accelerator group to the window.
        self.add_accel_group(__accel_group)

        # Finally, return the actual menu bar created by the item factory.
        return self.item_factory.get_widget("<main>")

    def print_hello(self, w, data):
        print "hello"

class AddElementMenuItem(gtk.MenuItem):
    def __init__(self, selection, dtd, label="add Child Element..."):
        gtk.MenuItem.__init__(self, label)       
        self.items=list()
        self.set_submenu(self.createMenu(selection, dtd))
        self.show()  
        
    
    def registerListener(self, listener):
        for i in range(len(self.items)):
            self.items[i][0].connect("activate", listener.add_element, \
                                     self.items[i][1], self.items[i][2], self.items[i][3])

    def createMenu(self, selection, dtd):
        __menu = gtk.Menu()
        __model, __i = selection.get_selected()
        __node = __model.get(__i, DOMModel.COLUMN_NODE)[0]
        __attr = ContentModelHelper(dtd).getValidElementNamesAppend(__node.get_data(DOMTreeModel.NODE_KEY))
        for i in range(len(__attr)):
            __item = gtk.MenuItem(__attr[i])
            __menu.append(__item)
            self.items.append([__item, __model, __i, __attr[i]])
            __item.show()
        __menu.show()
        return __menu
    
class InsertElementMenuItem(gtk.MenuItem):
    def __init__(self, selection, dtd, label="insert Element..."):
        gtk.MenuItem.__init__(self, label)       
        self.items=list()
        __item = self.createMenu(selection, dtd)
        if __item:
            self.set_submenu(__item)
            self.show()  
        
    
    def registerListener(self, listener):
        for i in range(len(self.items)):
            self.items[i][0].connect("activate", listener.insert_element, \
                                     self.items[i][1], self.items[i][2], self.items[i][3])

    def createMenu(self, selection, dtd):
        __menu = gtk.Menu()
        __model, __i = selection.get_selected()
        __node = __model.get(__i, DOMModel.COLUMN_NODE)[0]
        if not __node.get_data(DOMTreeModel.NODE_KEY).parentNode.nodeType == __node.get_data(DOMTreeModel.NODE_KEY).parentNode.ELEMENT_NODE:
            return None
        print __node.get_data(DOMTreeModel.NODE_KEY).parentNode
        __attr = ContentModelHelper(dtd). \
            getValidElementNamesInsert(__node.get_data(DOMTreeModel.NODE_KEY))
        for i in range(len(__attr)):
            __item = gtk.MenuItem(__attr[i])
            __menu.append(__item)
            self.items.append([__item, __model, __i, __attr[i]])
            __item.show()
        __menu.show()
        return __menu
    

class DeleteElementMenuItem(gtk.MenuItem):
    def __init__(self, selection, label="delete"):
        gtk.MenuItem.__init__(self, label)
        self.selection=selection
        self.show()
        
    def registerListener(self, listener):
        __model, __i = self.selection.get_selected()
        self.connect("activate", listener.delete_element,  __model, __i)    
        
class AddAttributeMenuItem(gtk.MenuItem):
    def __init__(self, selection, dtd, label="add Attribute..."):
        gtk.MenuItem.__init__(self, label)
        self.items=list()
        self.set_submenu(self.createMenu(selection, dtd))
        self.show()  
        
    def registerListener(self, listener):
        for i in range(len(self.items)):
            self.items[i][0].connect("activate", listener.add_attribute, \
                                     self.items[i][1], self.items[i][2], self.items[i][3])    
        
    def createMenu(self, selection, dtd):
        __menu = gtk.Menu()
        __model, __i = selection.get_selected()
        __node = __model.get(__i, DOMModel.COLUMN_NODE)[0].get_data(DOMTreeModel.NODE_KEY)
        __attr = dtd.get_elem(__node.tagName).get_attr_list()
        for i in range(len(__attr)):
            if not __node.hasAttribute(__attr[i]):
                __item = gtk.MenuItem(__attr[i])
                __menu.append(__item)
                self.items.append([__item, __model, __i, __attr[i]])
                __item.show()
        __menu.show()
        return __menu
       
    
class DeleteAttributeMenuItem(gtk.MenuItem):
    def __init__(self, selection, label="delete Attribute..."):
        gtk.MenuItem.__init__(self, label)
        self.items=list()
        self.set_submenu(self.createMenu(selection))
        self.show()           
            
    def registerListener(self, listener):
        for i in range(len(self.items)):
            self.items[i][0].connect("activate", listener.delete_attribute, \
                                     self.items[i][1], self.items[i][2], self.items[i][3])    
            
    def createMenu(self, selection):
        __menu = gtk.Menu()
        __model, __i = selection.get_selected()
        __node = __model.get(__i, DOMModel.COLUMN_NODE)[0]
        __elem= __node.get_data(DOMTreeModel.NODE_KEY)
        __attr = __elem.attributes
        for i in range(len(__attr)):
            __item = gtk.MenuItem(__attr[i].name)
            self.items.append([__item, __model, __i, __attr[i].name])
            __menu.append(__item)
            __item.show()
        __menu.show()
        return __menu
            
            
class ContentModelHelper:
    def __init__(self, dtd):
        self.dtd=dtd
    
    def getValidElementNamesAppend(self, element):
        __elem=self.dtd.get_elem(element.tagName)
        __state=__elem.get_start_state()
        __nodes=element.childNodes
        for i in range(len(__nodes)):
            print "found element %s" %__nodes[i].tagName
            __state=__elem.next_state(__state, __nodes[i].tagName)
        return __elem.get_valid_elements(__state)
        
    def getValidElementNamesInsert(self, element):
        ret=list()
        oelement=element
        parent=element.parentNode
        __elem=self.dtd.get_elem(parent.tagName)
        __state=__elem.get_start_state()
        __nodes=[element]
        while element.previousSibling:
            if element.nodeType == element.ELEMENT_NODE:
                __nodes.append(element)
                element = element.previousSibling 
        __nodes.reverse()
        for i in range(len(__nodes)):
            print "found element %s" %__nodes[i].tagName
            #if __elem.final_state(__state):
             #   return ret
        __state=__elem.next_state(__state, __nodes[i].tagName)
       
        __elements=__elem.get_valid_elements(__state)
        for i in range(len(__elements)):
            print "testing element " + __elements[i]
            ooelement=oelement
            try: 
                __tstate=__elem.next_state(__state, __elements[i])
                while oelement.nextSibling:
                    oelement=oelement.nextSibling
                    if element.nodeType == element.ELEMENT_NODE:
                        __tstate=__elem.next_state(__tstate, oelement.tagName)
            except KeyError, e:
                print "element : " + __elements[i]
                print e
                continue
            ret.append(__elements[i])
        print ret
        return ret
        
    def getValidElementNames2(self, element):
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
    dtv=DOMTreeViewTest(doc.documentElement, dtd, doc)
    gtk.main()

if __name__ == '__main__':
    main()
