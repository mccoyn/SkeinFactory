class Tk:
	"Mock type"

class Widget():
    """Internal class.

    Base class for a widget which can be positioned with the geometry managers
    Pack, Place or Grid."""
    pass

class StringVar:
    """Value holder for strings variables."""
    _default = ""
    def __init__(self, master=None, value=None, name=None):
        """Construct a string variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to "")
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """

    def get(self):
        """Return value of variable as string."""
        return ''

class Button(Widget):
    """Button widget."""
    def __init__(self, master=None, cnf={}):
        """Construct a button widget with the parent MASTER.

        STANDARD OPTIONS

            activebackground, activeforeground, anchor,
            background, bitmap, borderwidth, cursor,
            disabledforeground, font, foreground
            highlightbackground, highlightcolor,
            highlightthickness, image, justify,
            padx, pady, relief, repeatdelay,
            repeatinterval, takefocus, text,
            textvariable, underline, wraplength

        WIDGET-SPECIFIC OPTIONS

            command, compound, default, height,
            overrelief, state, width
        """
        Widget.__init__(self, master, 'button', cnf)

    def tkButtonEnter(self):
        self.tk.call('tkButtonEnter', self._w)

    def tkButtonLeave(self):
        self.tk.call('tkButtonLeave', self._w)

    def tkButtonDown(self):
        self.tk.call('tkButtonDown', self._w)

    def tkButtonUp(self):
        self.tk.call('tkButtonUp', self._w)

    def tkButtonInvoke(self):
        self.tk.call('tkButtonInvoke', self._w)

    def flash(self):
        """Flash the button.

        This is accomplished by redisplaying
        the button several times, alternating between active and
        normal colors. At the end of the flash the button is left
        in the same normal/active state as when the command was
        invoked. This command is ignored if the button's state is
        disabled.
        """
        self.tk.call(self._w, 'flash')

    def invoke(self):
        """Invoke the command associated with the button.

        The return value is the return value from the command,
        or an empty string if there is no command associated with
        the button. This command is ignored if the button's state
        is disabled.
        """
        return self.tk.call(self._w, 'invoke')

class Radiobutton(Widget):
    """Radiobutton widget which shows only one of several buttons in on-state."""
    def __init__(self, master=None, cnf={}):
        """Construct a radiobutton widget with the parent MASTER.

        Valid resource names: activebackground, activeforeground, anchor,
        background, bd, bg, bitmap, borderwidth, command, cursor,
        disabledforeground, fg, font, foreground, height,
        highlightbackground, highlightcolor, highlightthickness, image,
        indicatoron, justify, padx, pady, relief, selectcolor, selectimage,
        state, takefocus, text, textvariable, underline, value, variable,
        width, wraplength."""
        Widget.__init__(self, master, 'radiobutton', cnf)
    def deselect(self):
        """Put the button in off-state."""

        self.tk.call(self._w, 'deselect')
    def flash(self):
        """Flash the button."""
        self.tk.call(self._w, 'flash')
    def invoke(self):
        """Toggle the button and invoke a command if given as resource."""
        return self.tk.call(self._w, 'invoke')
    def select(self):
        """Put the button in on-state."""
        self.tk.call(self._w, 'select')

class Canvas(Widget):
    """Canvas widget to display graphical elements like lines or text."""
    def __init__(self, master=None):
        """Construct a canvas widget with the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, closeenough,
        confine, cursor, height, highlightbackground, highlightcolor,
        highlightthickness, insertbackground, insertborderwidth,
        insertofftime, insertontime, insertwidth, offset, relief,
        scrollregion, selectbackground, selectborderwidth, selectforeground,
        state, takefocus, width, xscrollcommand, xscrollincrement,
        yscrollcommand, yscrollincrement."""
        Widget.__init__(self, master, 'canvas')
    def addtag(self, name, value):
        """Internal function."""
        self.tk.call((self._w, 'addtag') + [name, value])
    def addtag_above(self, newtag, tagOrId):
        """Add tag NEWTAG to all items above TAGORID."""
        self.addtag(newtag, 'above', tagOrId)
    def addtag_all(self, newtag):
        """Add tag NEWTAG to all items."""
        self.addtag(newtag, 'all')
    def addtag_below(self, newtag, tagOrId):
        """Add tag NEWTAG to all items below TAGORID."""
        self.addtag(newtag, 'below', tagOrId)
    def addtag_closest(self, newtag, x, y, halo=None, start=None):
        """Add tag NEWTAG to item which is closest to pixel at X, Y.
        If several match take the top-most.
        All items closer than HALO are considered overlapping (all are
        closests). If START is specified the next below this tag is taken."""
        self.addtag(newtag, 'closest', x, y, halo, start)
    def addtag_enclosed(self, newtag, x1, y1, x2, y2):
        """Add tag NEWTAG to all items in the rectangle defined
        by X1,Y1,X2,Y2."""
        self.addtag(newtag, 'enclosed', x1, y1, x2, y2)
    def addtag_overlapping(self, newtag, x1, y1, x2, y2):
        """Add tag NEWTAG to all items which overlap the rectangle
        defined by X1,Y1,X2,Y2."""
        self.addtag(newtag, 'overlapping', x1, y1, x2, y2)
    def addtag_withtag(self, newtag, tagOrId):
        """Add tag NEWTAG to all items with TAGORID."""
        self.addtag(newtag, 'withtag', tagOrId)
    #def bbox(self, *args):
    #    """Return a tuple of X1,Y1,X2,Y2 coordinates for a rectangle
    #    which encloses all items with tags specified as arguments."""
    #    return self._getints(
    #        self.tk.call((self._w, 'bbox') + args)) or None
    def tag_unbind(self, tagOrId, sequence, funcid=None):
        """Unbind for all items with TAGORID for event SEQUENCE  the
        function identified with FUNCID."""
        self.tk.call(self._w, 'bind', tagOrId, sequence, '')
        if funcid:
            self.deletecommand(funcid)
    def tag_bind(self, tagOrId, sequence=None, func=None, add=None):
        """Bind to all items with TAGORID at event SEQUENCE a call to function FUNC.

        An additional boolean parameter ADD specifies whether FUNC will be
        called additionally to the other bound function or whether it will
        replace the previous function. See bind for the return value."""
        return self._bind((self._w, 'bind', tagOrId),
                  sequence, func, add)
    def canvasx(self, screenx, gridspacing=None):
        """Return the canvas x coordinate of pixel position SCREENX rounded
        to nearest multiple of GRIDSPACING units."""
        return getdouble(self.tk.call(
            self._w, 'canvasx', screenx, gridspacing))
    def canvasy(self, screeny, gridspacing=None):
        """Return the canvas y coordinate of pixel position SCREENY rounded
        to nearest multiple of GRIDSPACING units."""
        return getdouble(self.tk.call(
            self._w, 'canvasy', screeny, gridspacing))
    #def coords(self, *args):
    #    """Return a list of coordinates for the item given in ARGS."""
    #    # XXX Should use _flatten on args
    #    return map(getdouble,
    #                       self.tk.splitlist(
    #               self.tk.call((self._w, 'coords') + args)))
    #def _create(self, itemType, args, kw): # Args: (val, val, ..., cnf={})
    #    """Internal function."""
    #    args = _flatten(args)
    #    cnf = args[-1]
    #    if type(cnf) in (DictionaryType, TupleType):
    #        args = args[:-1]
    #    else:
    #        cnf = {}
    #    return getint(self.tk.call(
    #        self._w, 'create', itemType,
    #        *(args + self._options(cnf, kw))))
    #def create_arc(self, *args, **kw):
    #    """Create arc shaped region with coordinates x1,y1,x2,y2."""
    #    return self._create('arc', args, kw)
    #def create_bitmap(self, *args, **kw):
    #    """Create bitmap with coordinates x1,y1."""
    #    return self._create('bitmap', args, kw)
    #def create_image(self, *args, **kw):
    #    """Create image item with coordinates x1,y1."""
    #    return self._create('image', args, kw)
    #def create_line(self, *args, **kw):
    #    """Create line with coordinates x1,y1,...,xn,yn."""
    #    return self._create('line', args, kw)
    #def create_oval(self, *args, **kw):
    #    """Create oval with coordinates x1,y1,x2,y2."""
    #    return self._create('oval', args, kw)
    #def create_polygon(self, *args, **kw):
    #    """Create polygon with coordinates x1,y1,...,xn,yn."""
    #    return self._create('polygon', args, kw)
    #def create_rectangle(self, *args, **kw):
    #    """Create rectangle with coordinates x1,y1,x2,y2."""
    #    return self._create('rectangle', args, kw)
    #def create_text(self, *args, **kw):
    #    """Create text with coordinates x1,y1."""
    #    return self._create('text', args, kw)
    #def create_window(self, *args, **kw):
    #    """Create window with coordinates x1,y1,x2,y2."""
    #    return self._create('window', args, kw)
    #def dchars(self, *args):
    #    """Delete characters of text items identified by tag or id in ARGS (possibly
    #    several times) from FIRST to LAST character (including)."""
    #    self.tk.call((self._w, 'dchars') + args)
    #def delete(self, *args):
    #    """Delete items identified by all tag or ids contained in ARGS."""
    #    self.tk.call((self._w, 'delete') + args)
    #def dtag(self, *args):
    #    """Delete tag or id given as last arguments in ARGS from items
    #    identified by first argument in ARGS."""
    #    self.tk.call((self._w, 'dtag') + args)
    #def find(self, *args):
    #    """Internal function."""
    #    return self._getints(
    #        self.tk.call((self._w, 'find') + args)) or ()
    def find_above(self, tagOrId):
        """Return items above TAGORID."""
        return self.find('above', tagOrId)
    def find_all(self):
        """Return all items."""
        return self.find('all')
    def find_below(self, tagOrId):
        """Return all items below TAGORID."""
        return self.find('below', tagOrId)
    def find_closest(self, x, y, halo=None, start=None):
        """Return item which is closest to pixel at X, Y.
        If several match take the top-most.
        All items closer than HALO are considered overlapping (all are
        closests). If START is specified the next below this tag is taken."""
        return self.find('closest', x, y, halo, start)
    def find_enclosed(self, x1, y1, x2, y2):
        """Return all items in rectangle defined
        by X1,Y1,X2,Y2."""
        return self.find('enclosed', x1, y1, x2, y2)
    def find_overlapping(self, x1, y1, x2, y2):
        """Return all items which overlap the rectangle
        defined by X1,Y1,X2,Y2."""
        return self.find('overlapping', x1, y1, x2, y2)
    def find_withtag(self, tagOrId):
        """Return all items with TAGORID."""
        return self.find('withtag', tagOrId)
    #def focus(self, *args):
    #    """Set focus to the first item specified in ARGS."""
    #    return self.tk.call((self._w, 'focus') + args)
    #def gettags(self, *args):
    #    """Return tags associated with the first item specified in ARGS."""
    #    return self.tk.splitlist(
    #        self.tk.call((self._w, 'gettags') + args))
    #def icursor(self, *args):
    #    """Set cursor at position POS in the item identified by TAGORID.
    #    In ARGS TAGORID must be first."""
    #    self.tk.call((self._w, 'icursor') + args)
    #def index(self, *args):
    #    """Return position of cursor as integer in item specified in ARGS."""
    #    return getint(self.tk.call((self._w, 'index') + args))
    #def insert(self, *args):
    #    """Insert TEXT in item TAGORID at position POS. ARGS must
    #    be TAGORID POS TEXT."""
    #    self.tk.call((self._w, 'insert') + args)
    def itemcget(self, tagOrId, option):
        """Return the resource value for an OPTION for item TAGORID."""
        return self.tk.call(
            (self._w, 'itemcget') + (tagOrId, '-'+option))
    #def itemconfigure(self, tagOrId, cnf=None, **kw):
    #    """Configure resources of an item TAGORID.

    #    The values for resources are specified as keyword
    #    arguments. To get an overview about
    #    the allowed keyword arguments call the method without arguments.
    #    """
    #    return self._configure(('itemconfigure', tagOrId), cnf, kw)
    #itemconfig = itemconfigure
    # lower, tkraise/lift hide Misc.lower, Misc.tkraise/lift,
    # so the preferred name for them is tag_lower, tag_raise
    # (similar to tag_bind, and similar to the Text widget);
    # unfortunately can't delete the old ones yet (maybe in 1.6)
    #def tag_lower(self, *args):
    #    """Lower an item TAGORID given in ARGS
    #    (optional below another item)."""
    #    self.tk.call((self._w, 'lower') + args)
    #lower = tag_lower
    #def move(self, *args):
    #    """Move an item TAGORID given in ARGS."""
    #    self.tk.call((self._w, 'move') + args)
    #def postscript(self, cnf={}, **kw):
    #    """Print the contents of the canvas to a postscript
    #    file. Valid options: colormap, colormode, file, fontmap,
    #    height, pageanchor, pageheight, pagewidth, pagex, pagey,
    #    rotate, witdh, x, y."""
    #    return self.tk.call((self._w, 'postscript') +
    #                self._options(cnf, kw))
    #def tag_raise(self, *args):
    #    """Raise an item TAGORID given in ARGS
    #    (optional above another item)."""
    #    self.tk.call((self._w, 'raise') + args)
    #lift = tkraise = tag_raise
    #def scale(self, *args):
    #    """Scale item TAGORID with XORIGIN, YORIGIN, XSCALE, YSCALE."""
    #    self.tk.call((self._w, 'scale') + args)
    def scan_mark(self, x, y):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, 'scan', 'mark', x, y)
    def scan_dragto(self, x, y, gain=10):
        """Adjust the view of the canvas to GAIN times the
        difference between X and Y and the coordinates given in
        scan_mark."""
        self.tk.call(self._w, 'scan', 'dragto', x, y, gain)
    def select_adjust(self, tagOrId, index):
        """Adjust the end of the selection near the cursor of an item TAGORID to index."""
        self.tk.call(self._w, 'select', 'adjust', tagOrId, index)
    def select_clear(self):
        """Clear the selection if it is in this widget."""
        self.tk.call(self._w, 'select', 'clear')
    def select_from(self, tagOrId, index):
        """Set the fixed end of a selection in item TAGORID to INDEX."""
        self.tk.call(self._w, 'select', 'from', tagOrId, index)
    def select_item(self):
        """Return the item which has the selection."""
        return self.tk.call(self._w, 'select', 'item') or None
    def select_to(self, tagOrId, index):
        """Set the variable end of a selection in item TAGORID to INDEX."""
        self.tk.call(self._w, 'select', 'to', tagOrId, index)
    def type(self, tagOrId):
        """Return the type of the item TAGORID."""
        return self.tk.call(self._w, 'type', tagOrId) or None
    #def xview(self, *args):
    #    """Query and change horizontal position of the view."""
    #    if not args:
    #        return self._getdoubles(self.tk.call(self._w, 'xview'))
    #    self.tk.call((self._w, 'xview') + args)
    def xview_moveto(self, fraction):
        """Adjusts the view in the window so that FRACTION of the
        total width of the canvas is off-screen to the left."""
        self.tk.call(self._w, 'xview', 'moveto', fraction)
    def xview_scroll(self, number, what):
        """Shift the x-view according to NUMBER which is measured in "units" or "pages" (WHAT)."""
        self.tk.call(self._w, 'xview', 'scroll', number, what)
    #def yview(self, *args):
    #    """Query and change vertical position of the view."""
    #    if not args:
    #        return self._getdoubles(self.tk.call(self._w, 'yview'))
    #    self.tk.call((self._w, 'yview') + args)
    def yview_moveto(self, fraction):
        """Adjusts the view in the window so that FRACTION of the
        total height of the canvas is off-screen to the top."""
        self.tk.call(self._w, 'yview', 'moveto', fraction)
    def yview_scroll(self, number, what):
        """Shift the y-view according to NUMBER which is measured in "units" or "pages" (WHAT)."""
        self.tk.call(self._w, 'yview', 'scroll', number, what)

class Checkbutton(Widget):
    """Checkbutton widget which is either in on- or off-state."""
    def __init__(self, master=None, cnf={}):
        """Construct a checkbutton widget with the parent MASTER.

        Valid resource names: activebackground, activeforeground, anchor,
        background, bd, bg, bitmap, borderwidth, command, cursor,
        disabledforeground, fg, font, foreground, height,
        highlightbackground, highlightcolor, highlightthickness, image,
        indicatoron, justify, offvalue, onvalue, padx, pady, relief,
        selectcolor, selectimage, state, takefocus, text, textvariable,
        underline, variable, width, wraplength."""
        Widget.__init__(self, master, 'checkbutton', cnf)
    def deselect(self):
        """Put the button in off-state."""
        self.tk.call(self._w, 'deselect')
    def flash(self):
        """Flash the button."""
        self.tk.call(self._w, 'flash')
    def invoke(self):
        """Toggle the button and invoke a command if given as resource."""
        return self.tk.call(self._w, 'invoke')
    def select(self):
        """Put the button in on-state."""
        self.tk.call(self._w, 'select')
    def toggle(self):
        """Toggle the button."""
        self.tk.call(self._w, 'toggle')

class Entry(Widget):
    """Entry widget which allows to display simple text."""
    def __init__(self, master=None, cnf={}):
        """Construct an entry widget with the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, cursor,
        exportselection, fg, font, foreground, highlightbackground,
        highlightcolor, highlightthickness, insertbackground,
        insertborderwidth, insertofftime, insertontime, insertwidth,
        invalidcommand, invcmd, justify, relief, selectbackground,
        selectborderwidth, selectforeground, show, state, takefocus,
        textvariable, validate, validatecommand, vcmd, width,
        xscrollcommand."""
        Widget.__init__(self, master, 'entry', cnf)
    def delete(self, first, last=None):
        """Delete text from FIRST to LAST (not included)."""
        self.tk.call(self._w, 'delete', first, last)
    def get(self):
        """Return the text."""
        return self.tk.call(self._w, 'get')
    def icursor(self, index):
        """Insert cursor at INDEX."""
        self.tk.call(self._w, 'icursor', index)
    def index(self, index):
        """Return position of cursor."""
        return getint(self.tk.call(
            self._w, 'index', index))
    def insert(self, index, string):
        """Insert STRING at INDEX."""
        self.tk.call(self._w, 'insert', index, string)
    def scan_mark(self, x):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, 'scan', 'mark', x)
    def scan_dragto(self, x):
        """Adjust the view of the canvas to 10 times the
        difference between X and Y and the coordinates given in
        scan_mark."""
        self.tk.call(self._w, 'scan', 'dragto', x)
    def selection_adjust(self, index):
        """Adjust the end of the selection near the cursor to INDEX."""
        self.tk.call(self._w, 'selection', 'adjust', index)
    select_adjust = selection_adjust
    def selection_clear(self):
        """Clear the selection if it is in this widget."""
        self.tk.call(self._w, 'selection', 'clear')
    select_clear = selection_clear
    def selection_from(self, index):
        """Set the fixed end of a selection to INDEX."""
        self.tk.call(self._w, 'selection', 'from', index)
    select_from = selection_from
    def selection_present(self):
        """Return whether the widget has the selection."""
        return self.tk.getboolean(
            self.tk.call(self._w, 'selection', 'present'))
    select_present = selection_present
    def selection_range(self, start, end):
        """Set the selection from START to END (not included)."""
        self.tk.call(self._w, 'selection', 'range', start, end)
    select_range = selection_range
    def selection_to(self, index):
        """Set the variable end of a selection to INDEX."""
        self.tk.call(self._w, 'selection', 'to', index)
    select_to = selection_to
    def xview(self, index):
        """Query and change horizontal position of the view."""
        self.tk.call(self._w, 'xview', index)
    def xview_moveto(self, fraction):
        """Adjust the view in the window so that FRACTION of the
        total width of the entry is off-screen to the left."""
        self.tk.call(self._w, 'xview', 'moveto', fraction)
    def xview_scroll(self, number, what):
        """Shift the x-view according to NUMBER which is measured in "units" or "pages" (WHAT)."""
        self.tk.call(self._w, 'xview', 'scroll', number, what)

class Label(Widget):
    """Label widget which can display text and bitmaps."""
    def __init__(self, master=None, cnf={}):
        """Construct a label widget with the parent MASTER.

        STANDARD OPTIONS

            activebackground, activeforeground, anchor,
            background, bitmap, borderwidth, cursor,
            disabledforeground, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, image, justify,
            padx, pady, relief, takefocus, text,
            textvariable, underline, wraplength

        WIDGET-SPECIFIC OPTIONS

            height, state, width

        """
        Widget.__init__(self, master, 'label', cnf)

class Menu(Widget):
    """Menu widget which allows to display menu bars, pull-down menus and pop-up menus."""
    """Menu widget which allows to display menu bars, pull-down menus and pop-up menus."""
    def __init__(self, master=None, cnf={}):
        """Construct menu widget with the parent MASTER.

        Valid resource names: activebackground, activeborderwidth,
        activeforeground, background, bd, bg, borderwidth, cursor,
        disabledforeground, fg, font, foreground, postcommand, relief,
        selectcolor, takefocus, tearoff, tearoffcommand, title, type."""
        Widget.__init__(self, master, 'menu', cnf)
    def tk_bindForTraversal(self):
        pass # obsolete since Tk 4.0
    def tk_mbPost(self):
        self.tk.call('tk_mbPost', self._w)
    def tk_mbUnpost(self):
        self.tk.call('tk_mbUnpost')
    def tk_traverseToMenu(self, char):
        self.tk.call('tk_traverseToMenu', self._w, char)
    def tk_traverseWithinMenu(self, char):
        self.tk.call('tk_traverseWithinMenu', self._w, char)
    def tk_getMenuButtons(self):
        return self.tk.call('tk_getMenuButtons', self._w)
    def tk_nextMenu(self, count):
        self.tk.call('tk_nextMenu', count)
    def tk_nextMenuEntry(self, count):
        self.tk.call('tk_nextMenuEntry', count)
    def tk_invokeMenu(self):
        self.tk.call('tk_invokeMenu', self._w)
    def tk_firstMenu(self):
        self.tk.call('tk_firstMenu', self._w)
    def tk_mbButtonDown(self):
        self.tk.call('tk_mbButtonDown', self._w)
    def tk_popup(self, x, y, entry=""):
        """Post the menu at position X,Y with entry ENTRY."""
        self.tk.call('tk_popup', self._w, x, y, entry)
    def activate(self, index):
        """Activate entry at INDEX."""
        self.tk.call(self._w, 'activate', index)
    #def add(self, itemType, cnf={}, **kw):
    #    """Internal function."""
    #    self.tk.call((self._w, 'add', itemType) +
    #             self._options(cnf, kw))
    #def add_cascade(self, cnf={}, **kw):
    #    """Add hierarchical menu item."""
    #    self.add('cascade', cnf or kw)
    #def add_checkbutton(self, cnf={}, **kw):
    #    """Add checkbutton menu item."""
    #    self.add('checkbutton', cnf or kw)
    #def add_command(self, cnf={}, **kw):
    #    """Add command menu item."""
    #    self.add('command', cnf or kw)
    #def add_radiobutton(self, cnf={}, **kw):
    #    """Addd radio menu item."""
    #    self.add('radiobutton', cnf or kw)
    #def add_separator(self, cnf={}, **kw):
    #    """Add separator."""
    #    self.add('separator', cnf or kw)
    #def insert(self, index, itemType, cnf={}, **kw):
    #    """Internal function."""
    #    self.tk.call((self._w, 'insert', index, itemType) +
    #             self._options(cnf, kw))
    #def insert_cascade(self, index, cnf={}, **kw):
    #    """Add hierarchical menu item at INDEX."""
    #    self.insert(index, 'cascade', cnf or kw)
    #def insert_checkbutton(self, index, cnf={}, **kw):
    #    """Add checkbutton menu item at INDEX."""
    #    self.insert(index, 'checkbutton', cnf or kw)
    #def insert_command(self, index, cnf={}, **kw):
    #    """Add command menu item at INDEX."""
    #    self.insert(index, 'command', cnf or kw)
    #def insert_radiobutton(self, index, cnf={}, **kw):
    #    """Addd radio menu item at INDEX."""
    #    self.insert(index, 'radiobutton', cnf or kw)
    #def insert_separator(self, index, cnf={}, **kw):
    #    """Add separator at INDEX."""
    #    self.insert(index, 'separator', cnf or kw)
    def delete(self, index1, index2=None):
        """Delete menu items between INDEX1 and INDEX2 (included)."""
        if index2 is None:
            index2 = index1

        num_index1, num_index2 = self.index(index1), self.index(index2)
        if (num_index1 is None) or (num_index2 is None):
            num_index1, num_index2 = 0, -1

        for i in range(num_index1, num_index2 + 1):
            if 'command' in self.entryconfig(i):
                c = str(self.entrycget(i, 'command'))
                if c:
                    self.deletecommand(c)
        self.tk.call(self._w, 'delete', index1, index2)
    def entrycget(self, index, option):
        """Return the resource value of an menu item for OPTION at INDEX."""
        return self.tk.call(self._w, 'entrycget', index, '-' + option)
    #def entryconfigure(self, index, cnf=None, **kw):
    #    """Configure a menu item at INDEX."""
    #    return self._configure(('entryconfigure', index), cnf, kw)
    #entryconfig = entryconfigure
    def index(self, index):
        """Return the index of a menu item identified by INDEX."""
        i = self.tk.call(self._w, 'index', index)
        if i == 'none': return None
        return getint(i)
    def invoke(self, index):
        """Invoke a menu item identified by INDEX and execute
        the associated command."""
        return self.tk.call(self._w, 'invoke', index)
    def post(self, x, y):
        """Display a menu at position X,Y."""
        self.tk.call(self._w, 'post', x, y)
    def type(self, index):
        """Return the type of the menu item at INDEX."""
        return self.tk.call(self._w, 'type', index)
    def unpost(self):
        """Unmap a menu."""
        self.tk.call(self._w, 'unpost')
    def yposition(self, index):
        """Return the y-position of the topmost pixel of the menu item at INDEX."""
        return getint(self.tk.call(
            self._w, 'yposition', index))
        
class Scrollbar(Widget):
    """Scrollbar widget which displays a slider at a certain position."""
    def __init__(self, master=None):
        """Construct a scrollbar widget with the parent MASTER.

        Valid resource names: activebackground, activerelief,
        background, bd, bg, borderwidth, command, cursor,
        elementborderwidth, highlightbackground,
        highlightcolor, highlightthickness, jump, orient,
        relief, repeatdelay, repeatinterval, takefocus,
        troughcolor, width."""
        Widget.__init__(self, master, 'scrollbar')
    def activate(self, index):
        """Display the element at INDEX with activebackground and activerelief.
        INDEX can be "arrow1","slider" or "arrow2"."""
        self.tk.call(self._w, 'activate', index)
    def delta(self, deltax, deltay):
        """Return the fractional change of the scrollbar setting if it
        would be moved by DELTAX or DELTAY pixels."""
        return getdouble(
            self.tk.call(self._w, 'delta', deltax, deltay))
    def fraction(self, x, y):
        """Return the fractional value which corresponds to a slider
        position of X,Y."""
        return getdouble(self.tk.call(self._w, 'fraction', x, y))
    def identify(self, x, y):
        """Return the element under position X,Y as one of
        "arrow1","slider","arrow2" or ""."""
        return self.tk.call(self._w, 'identify', x, y)
    def get(self):
        """Return the current fractional values (upper and lower end)
        of the slider position."""
        return self._getdoubles(self.tk.call(self._w, 'get'))
    #def set(self, *args):
    #    """Set the fractional values of the slider position (upper and
    #    lower ends as value between 0 and 1)."""
    #    self.tk.call((self._w, 'set') + args)
    
class Spinbox(Widget):
    """spinbox widget."""
    def __init__(self, master=None, cnf={}):
        """Construct a spinbox widget with the parent MASTER.

        STANDARD OPTIONS

            activebackground, background, borderwidth,
            cursor, exportselection, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, insertbackground,
            insertborderwidth, insertofftime,
            insertontime, insertwidth, justify, relief,
            repeatdelay, repeatinterval,
            selectbackground, selectborderwidth
            selectforeground, takefocus, textvariable
            xscrollcommand.

        WIDGET-SPECIFIC OPTIONS

            buttonbackground, buttoncursor,
            buttondownrelief, buttonuprelief,
            command, disabledbackground,
            disabledforeground, format, from,
            invalidcommand, increment,
            readonlybackground, state, to,
            validate, validatecommand values,
            width, wrap,
        """
        Widget.__init__(self, master, 'spinbox', cnf)

    def bbox(self, index):
        """Return a tuple of X1,Y1,X2,Y2 coordinates for a
        rectangle which encloses the character given by index.

        The first two elements of the list give the x and y
        coordinates of the upper-left corner of the screen
        area covered by the character (in pixels relative
        to the widget) and the last two elements give the
        width and height of the character, in pixels. The
        bounding box may refer to a region outside the
        visible area of the window.
        """
        return self.tk.call(self._w, 'bbox', index)

    def delete(self, first, last=None):
        """Delete one or more elements of the spinbox.

        First is the index of the first character to delete,
        and last is the index of the character just after
        the last one to delete. If last isn't specified it
        defaults to first+1, i.e. a single character is
        deleted.  This command returns an empty string.
        """
        return self.tk.call(self._w, 'delete', first, last)

    def get(self):
        """Returns the spinbox's string"""
        return self.tk.call(self._w, 'get')

    def icursor(self, index):
        """Alter the position of the insertion cursor.

        The insertion cursor will be displayed just before
        the character given by index. Returns an empty string
        """
        return self.tk.call(self._w, 'icursor', index)

    def identify(self, x, y):
        """Returns the name of the widget at position x, y

        Return value is one of: none, buttondown, buttonup, entry
        """
        return self.tk.call(self._w, 'identify', x, y)

    def index(self, index):
        """Returns the numerical index corresponding to index
        """
        return self.tk.call(self._w, 'index', index)

    def insert(self, index, s):
        """Insert string s at index

         Returns an empty string.
        """
        return self.tk.call(self._w, 'insert', index, s)

    def invoke(self, element):
        """Causes the specified element to be invoked

        The element could be buttondown or buttonup
        triggering the action associated with it.
        """
        return self.tk.call(self._w, 'invoke', element)

    #def scan(self, *args):
    #    """Internal function."""
    #    return self._getints(
    #        self.tk.call((self._w, 'scan') + args)) or ()

    #def scan_mark(self, x):
    #    """Records x and the current view in the spinbox window;
    #
    #    used in conjunction with later scan dragto commands.
    #    Typically this command is associated with a mouse button
    #    press in the widget. It returns an empty string.
    #    """
    #    return self.scan("mark", x)

    #def scan_dragto(self, x):
    #    """Compute the difference between the given x argument
    #    and the x argument to the last scan mark command
    #
    #    It then adjusts the view left or right by 10 times the
    #    difference in x-coordinates. This command is typically
    #    associated with mouse motion events in the widget, to
    #    produce the effect of dragging the spinbox at high speed
    #    through the window. The return value is an empty string.
    #    """
    #    return self.scan("dragto", x)

    #def selection(self, *args):
    #    """Internal function."""
    #    return self._getints(
    #        self.tk.call((self._w, 'selection') + args)) or ()

    #def selection_adjust(self, index):
    #    """Locate the end of the selection nearest to the character
    #    given by index,
    #
    #    Then adjust that end of the selection to be at index
    #    (i.e including but not going beyond index). The other
    #    end of the selection is made the anchor point for future
    #    select to commands. If the selection isn't currently in
    #    the spinbox, then a new selection is created to include
    #    the characters between index and the most recent selection
    #    anchor point, inclusive. Returns an empty string.
    #    """
    #    return self.selection("adjust", index)

    #def selection_clear(self):
    #    """Clear the selection
    #
    #    If the selection isn't in this widget then the
    #    command has no effect. Returns an empty string.
    #    """
    #    return self.selection("clear")

    #def selection_element(self, element=None):
    #    """Sets or gets the currently selected element.
    #
    #    If a spinbutton element is specified, it will be
    #    displayed depressed
    #    """
    #    return self.selection("element", element)
    
