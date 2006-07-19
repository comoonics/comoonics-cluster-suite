# This is an example for demonstrating use of the GtkTreeView widget.
# The code in this example is not particularly good: it is written to
# concentrate on widget usage demonstration, not for maintainability.

import pygtk
pygtk.require("2.0")
import gtk
import gobject

view = None
choose_parent_view = None
dialog = None

def move(old_iter, new_parent, model):
    if old_iter:
        folder = model.get_value(old_iter, 0)
        model.remove(old_iter)
        new_iter = model.insert_before(new_parent, None)
        model.set_value(new_iter, 0, folder)
        model.set_value(new_iter, 1, folder["name"])

def dialog_ok(*args):
    dialog.hide()
    model, parent_iter = choose_parent_view.get_selection().get_selected()
    model, old_iter = view.get_selection().get_selected()
    if parent_iter and old_iter:
        move(old_iter, parent_iter, model)

def dialog_cancel(*args):
    dialog.hide()

def choose_parent(*args):
    dialog.show()

def move_to_top(*args):
    model, old_iter = view.get_selection().get_selected()
    if old_iter:
        move(old_iter, None, model)

def quit(*args):
    gtk.main_quit()

def make_view(model):
    # Create the view itself.
    view = gtk.TreeView(model)
    renderer = gtk.CellRendererText()
    column = gtk.TreeViewColumn("Folder", renderer, text=1)
    view.append_column(column)
    view.show()

    # Create scrollbars around the view.
    scrolled = gtk.ScrolledWindow()
    scrolled.add(view)
    scrolled.show()

    return view, scrolled

def make_buttons(list):
    buttonbox = gtk.HBox()
    for label, func in list:
        button = gtk.Button()
        button.set_label(label)
        button.connect("clicked", func)
        button.show()
        buttonbox.pack_start(button, expand=gtk.FALSE, fill=gtk.FALSE)
    buttonbox.show()
    return buttonbox

def main():
    # Create the model.
    model = gtk.TreeStore(gobject.TYPE_PYOBJECT, gobject.TYPE_STRING)

    # Populate the model with data. We represent folders with Python
    # dicts (hash tables or hashmaps in other languages), for simplicity.
    # In a real program, they would be programmer defined classes.
    for i in range(100):
        folder = { "name": "folder %d" % i, "files": ["foo", "bar"] }
        iter = model.insert_before(None, None)
        model.set_value(iter, 0, folder)
        model.set_value(iter, 1, folder["name"])
    
    # Create the main view.
    global view
    view, scrolled = make_view(model)
    view.set_reorderable(gtk.TRUE)

    # Create some command buttons.
    buttonbox = make_buttons([("Quit", quit), ("Choose parent", choose_parent),
                              ("Move to top", move_to_top)])
    
    # Create a vertical box to hold the above stuff.
    vbox = gtk.VBox()
    vbox.pack_start(buttonbox, expand=gtk.FALSE, fill=gtk.FALSE)
    vbox.pack_start(scrolled, expand=gtk.TRUE, fill=gtk.TRUE)
    vbox.show()

    # Create toplevel window to show it all.
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("delete_event", quit)
    win.add(vbox)
    win.show()
    win.resize(300, 500)
    
    # Create the GtkTreeView for choosing a parent.
    global choose_parent_view
    choose_parent_view, scrolled = make_view(model)
    
    buttonbox = make_buttons([("OK", dialog_ok), ("Cancel", dialog_cancel)])

    vbox = gtk.VBox()
    vbox.pack_start(scrolled, expand=gtk.TRUE, fill=gtk.TRUE)
    vbox.pack_start(buttonbox, expand=gtk.FALSE, fill=gtk.FALSE)
    vbox.show()

    global dialog
    dialog = gtk.Window(gtk.WINDOW_TOPLEVEL)
    dialog.set_default_size(200, 400)
    dialog.add(vbox)
    
    # Run the Gtk+ main loop.
    gtk.main()
    
if __name__ == "__main__":
    main()