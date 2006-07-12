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
import urllib2
import urllib
from xml.dom.NodeFilter import NodeFilter
from xml.dom.ext import PrettyPrint

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
    print "Filter Node %s" % node
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
    def __init__(self, edit=False, editfunc=None):
        gtk.TreeView.__init__(self)
        renderer = gtk.CellRendererText()
        renderer.set_data("column", DOMModel.COLUMN_NAME)
        renderer.set_property("xalign", 0.0)
        if edit:
            renderer.connect("edited", editfunc, self)

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
    def __init__(self, filename, parent=None):
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: gtk.main_quit())
        self.set_title(self.__class__.__name__)
        self.set_default_size(650, 400)
        self.set_border_width(8)

        menubar = self.create_main_menu()
        menubar.show()

        (doc, dtd) = self.openFile(filename)
        self.dtd=dtd
        node=doc.documentElement
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
        self.__listview = DOMNodeView(True, self.edit_attribute)
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
        vbox.add(hpaned)
        self.add(vbox)
        self.show_all()

    def openFile(self, filename):
        reader = Sax2.Reader(validate=1)
        stream = open(filename)
        doc = reader.fromStream(stream)
        dtd = reader.parser._parser.get_dtd()
        self.filename=filename
        return (doc, dtd)

    def openURI(self, uri):
        print "openURI(%s)" % uri        
        return self.openFile(filename)
        
    
    def saveFile(self, _uri=None):
        if not _uri:
            _uri=self.filename
        print "file: %s" % _uri
        stream=open(_uri,"w+")
        PrettyPrint(self.__basemodell.document, stream)
        self.filename=_uri
        
    def selection_changed(self, selection, dest, filter):
        (model, iter) = selection.get_selected()
        print "Selection changed %s, %s, %s %s" % (model, iter, dest, filter)
        dest.clear()
        if iter:
            dest.createStoreModelFromNode(model.get_value(iter, DOMModel.COLUMN_NODE).get_data(DOMModel.NODE_KEY))
        if filter:
            filter.refilter()
            
    def add_element(self, item, model, piter, name, iter=None):
        print "Menu Add Element... " + name + " pressed menuitem %s, model %s, piter %s, iter %s" % (item, model, piter, iter)
        if iter:
            value = model.get_value(iter, DOMModel.COLUMN_NODE)
            ref_node=value.get_data(DOMModel.NODE_KEY)
            ref_node=ref_node.nextSibling
            citer=model.convert_iter_to_child_iter(iter)
        else:
            citer=None
            ref_node=None
        value=model.get_value(piter, DOMModel.COLUMN_NODE)
        parent_node=value.get_data(DOMModel.NODE_KEY)
        print "parentnode: %s" % parent_node
        node=self.__basemodell.document.createElement(name)
        parent_node.insertBefore(node, ref_node)
        cpiter=model.convert_iter_to_child_iter(piter)
        iter_newnode=model.get_model().insert_after(cpiter, citer)
        gobj=gobject.GObject()
        gobj.set_data(DOMTreeModel.NODE_KEY, node)
        model.get_model().set_value(iter_newnode, DOMModel.COLUMN_NAME, node.nodeName)
        model.get_model().set_value(iter_newnode, DOMModel.COLUMN_VALUE, node.nodeValue)
        model.get_model().set_value(iter_newnode, DOMModel.COLUMN_EDITABLE, False)
        model.get_model().set_value(iter_newnode, DOMModel.COLUMN_NODE, gobj)
        
    def insert_element(self, item, model, iter, name):
        print "Menu Insert Element... " + name + " pressed menuitem %s, model %s, iter %s" % (item, model, iter)
        piter=model.iter_parent(iter)
        self.add_element(item, model, piter, name, iter)

    def delete_element(self, item, model, iter):
        print "Menu Delete Element... pressed menuitem %s, model %s" % (item, model)
        value = model.get_value(iter, DOMModel.COLUMN_NODE)
        ref_node=value.get_data(DOMModel.NODE_KEY)
        piter=model.iter_parent(iter)
        value=model.get_value(piter, DOMModel.COLUMN_NODE)
        parent_node=value.get_data(DOMModel.NODE_KEY)
        print "parentnode: %s" % parent_node
        parent_node.removeChild(ref_node)
        citer=model.convert_iter_to_child_iter(iter)
        model.get_model().remove(citer)
    
    def add_attribute(self, item, model, iter, name):
        print "Menu Add Attribute... " + name + " pressed menuitem %s, model %s, iter %s" % (item, model, iter)
        value = model.get_value(iter, DOMModel.COLUMN_NODE)
        ref_node=value.get_data(DOMModel.NODE_KEY)
        ref_node.setAttribute(name, "unset")
        print "ref_node: %s" % ref_node
        self.__basemodelr.clear()
        self.__basemodelr.createStoreModelFromNode(ref_node)

    def delete_attribute(self, item, model, iter, name):
        print "Menu Delete attribute... " + name + " pressed menuitem %s, model %s, iter %s" % (item, model, iter)
        value = model.get_value(iter, DOMModel.COLUMN_NODE)
        ref_node=value.get_data(DOMModel.NODE_KEY)
        ref_node.removeAttribute(name)
        print "ref_node: %s" % ref_node
        self.__basemodelr.clear()
        self.__basemodelr.createStoreModelFromNode(ref_node)
    
    def edit_attribute(self, cell, path_string, new_text, view):
        model=view.get_model()
        print "Menu Edit attribute... " + path_string + " pressed cell %s, model %s, new_text %s" % (cell, model, new_text)
        iter = model.get_iter_from_string(path_string)
        piter= model.iter_parent(iter)
        parent_node=model.get_value(iter, DOMModel.COLUMN_NODE).get_data(DOMModel.NODE_KEY)
        value = model.get_value(iter, DOMModel.COLUMN_NODE)
        ref_node=value.get_data(DOMModel.NODE_KEY)
        print "Path: %s" % (path_string)
        
        print "ref_node: %s" % ref_node
        ref_node.nodeValue=new_text
        citer=model.convert_iter_to_child_iter(iter)
        model.get_model().set(citer, DOMModel.COLUMN_VALUE, new_text)
            
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
    
    def file_new(self, number, menuitem):
        print "file_new pressed %s, %s." %(number, menuitem)
        
    def file_open(self, number, menuitem):
        print "file open pressed %s, %s." %(number, menuitem)
        dialog=gtk.FileChooserDialog("Choose file to open", self, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_OK, gtk.RESPONSE_OK,
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        xml_filter=gtk.FileFilter()
        xml_filter.add_pattern("*.xml")
        xml_filter.set_name("XML-Filter")
        conf_filter=gtk.FileFilter()
        conf_filter.add_pattern("*.conf")
        conf_filter.set_name("Conf-Filter")
        dialog.add_filter(xml_filter)
        dialog.add_filter(conf_filter)
        response=dialog.run()
        file=dialog.get_filename()
        dialog.destroy()
        if response == gtk.RESPONSE_OK:
            print "File: %s" % file
            self.openFile(file)
        
    def file_save(self, number, menuitem):
        print "file save pressed %s, %s." %(number, menuitem)
        self.saveFile()
        
    def file_save_as(self, number, menuitem):
        print "file save as pressed %s, %s." %(number, menuitem)
        dialog=gtk.FileChooserDialog("Choose file to open", self, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_OK, gtk.RESPONSE_OK,
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        xml_filter=gtk.FileFilter()
        xml_filter.add_pattern("*.xml")
        xml_filter.set_name("XML-Filter")
        conf_filter=gtk.FileFilter()
        conf_filter.add_pattern("*.conf")
        conf_filter.set_name("Conf-Filter")
        dialog.add_filter(xml_filter)
        dialog.add_filter(conf_filter)
        response=dialog.run()
        file=dialog.get_filename()
        dialog.destroy()
        if response == gtk.RESPONSE_OK:
            print "File: %s" % file
            self.saveFile(file)
    
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
            ( "/File/_New",     "<control>N", self.file_new, 0, None ),
            ( "/File/_Open",    "<control>O", self.file_open, 0, None ),
            ( "/File/_Save",    "<control>S", self.file_save, 0, None ),
            ( "/File/Save _As", None,         self.file_save_as, 0, None ),
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
    filename="../test/gfs-node1-clonetest.xml"
    if len(sys.argv) > 1:
        filename=sys.argv[1]
    dtv=DOMTreeViewTest(filename)
    gtk.main()

if __name__ == '__main__':
    main()
