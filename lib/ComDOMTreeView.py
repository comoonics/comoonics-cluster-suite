#!/usr/bin/env python
'''Tree View/Generic Tree Model

This test is designed to demonstrate creating a new type of tree model
in python for use with the new tree widget in gtk 2.0.'''

import gtk
import gobject
from xml.dom.minidom import parseString
from xml.dom.ext.reader import Sax2
import xml.dom
import sys
import os

class DOMTreeModel(gtk.TreeStore):
    NODE_KEY="node"
    def __init__(self, node):
        gtk.TreeStore.__init__(self, gobject.TYPE_STRING, gobject.TYPE_OBJECT)
        self.createTreeStoreModelFromNode(node)

    def createTreeStoreModelFromNode(self, node, parent=None):
        if node.nodeType == xml.dom.Node.ELEMENT_NODE:
            iter=self.append(parent)
            self.set_value(iter, 0, node.nodeName)
            gobj=gobject.GObject()
            gobj.set_data(DOMTreeModel.NODE_KEY, node)
            self.set_value(iter, 1, gobj)
        for child in node.childNodes:
            self.createTreeStoreModelFromNode(child, iter)
         
class DOMTreeView(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)
        renderer = gtk.CellRendererText()
        renderer.set_property("xalign", 0.0)
        column = gtk.TreeViewColumn("Name", renderer, text=0)
        #column = gtk_tree_view_get_column(GTK_TREE_VIEW(treeview), col_offset - 1);
        column.set_clickable(True)
        # self.get_selection().set_mode(gtk.SELECTION_SINGLE)

        self.append_column(column)
        
class DOMTreeViewTest(gtk.Window):
    def __init__(self, node, parent=None):
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: gtk.main_quit())
        self.set_title(self.__class__.__name__)
        self.set_default_size(650, 400)
        self.set_border_width(8)

        vbox = gtk.VBox(False, 8)
        self.add(vbox)

        label = gtk.Label("DOMTreeViewer")
        vbox.pack_start(label, False, False)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw)

        # create model
        # create treeview
        treeview = DOMTreeView()
        treeview.set_model(DOMTreeModel(node))
        treeview.set_rules_hint(True)

        sw.add(treeview)

        # expand all rows after the treeview widget has been realized
        treeview.connect('realize', lambda tv: tv.expand_all())
        treeview.get_selection().connect("changed", self.selection_changed)
        
        self.show_all()
        
    def selection_changed(self, parm):
        print "Selection changed %s" % parm
    
def main():
    reader = Sax2.Reader(validate=1)
    filename="../test/gfs-node1-clonetest.xml"
    if len(sys.argv) > 1:
        filename=sys.argv[1]
    file=os.fdopen(os.open(filename,os.O_RDONLY))
    doc = reader.fromStream(file)
    
    dtv=DOMTreeViewTest(doc.documentElement)
    gtk.main()

if __name__ == '__main__':
    main()
