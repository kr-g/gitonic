"""
    (c)2021 K. Goger - https://github.com/kr-g
    legal: https://github.com/kr-g/gitonic/blob/main/LICENSE.md
"""


import os

# loggin support

import logging

enableLogging = logging.DEBUG

_logger = logging.getLogger("ruckzuck")

if enableLogging:
    logging.basicConfig()
    _logger.setLevel(enableLogging)
else:
    _logger.addHandler(logging.NullHandler())


def _flat(args):
    fs = map(lambda x: str(x), args)
    return " ".join(fs)


def _log(level, args):
    if _logger.isEnabledFor(level):
        _logger.log(level, _flat(args))


def log(*args):
    _log(logging.INFO, args)


def print_t(*args):
    _log(logging.DEBUG, args)


def print_e(*args):
    _log(logging.CRITICAL, args)


#

from tkinter import *
from tktooltip import ToolTip

from tkinter import Tk, ttk, filedialog, scrolledtext

CAPTION = "caption"

VALUE = "value"
VALUES = "values"
MAP_VALUE = "map_value"
SOURCE = "source"

ON_CLICK = "on_click"
ON_RIGHT_CLICK = "on_right_click"
ON_DOUBLE_CLICK = "on_double_click"

ON_SELECT = "on_select"
ON_UNSELECT = "on_unselect"

ON_CHANGE = "on_change"

WIDTH = "width"
CAPTION_WIDTH = "caption_width"


class TkMixin(object):
    def init(self, root=None):
        self.tk = root

    def title(self, *args, **kwargs):
        self.tk.title(*args, *kwargs)

    def geometry(self, *args, **kwargs):
        self.tk.geometry(*args, *kwargs)

    def mainloop(self, *args, **kwargs):
        self.tk.mainloop(*args, *kwargs)

    def quit(self):
        self.tk.destroy()

    def resize_grip(self):
        self.tk.resizable(True, True)
        sizegrip = ttk.Sizegrip(self.tk)
        sizegrip.pack(side=RIGHT, anchor=SE)


_global_reg = {}
_global_hotkey = set()


def _add_hotkey(key):
    global _global_hotkey
    if key in _global_hotkey:
        raise Exception("already registered", key)
    _global_hotkey.add(key)


def gt(name):
    return _global_reg.get(name, None)


class Tile(TkMixin):
    def __init__(self, parent=None, idn=None, tk_root=None, **kwargs):

        self.init(tk_root)

        self.idn = idn
        if idn != None:
            if gt(idn) != None:
                print_t("already defined", idn)
            _global_reg[idn] = self

        self._kwargs = kwargs

        self.frame = None
        self._elems = []
        self._frame = []

        self._visible = self.pref("visible", True)

        self.set_parent(parent)

        self._container = None

        self.__init__internal__()

    def __repr__(self):
        return self.__class__.__name__ + " " + (self.idn if self.idn else hex(id(self)))

    def __init__internal__(self):
        pass

    def set_parent(self, parent):
        self._parent = parent

    def parent_frame(self):
        return self._parent.frame if type(self._parent) == Tile else self._parent

    def get_root(self):
        root = self
        while True:
            if isinstance(root, Tile):
                root = self._parent
            else:
                if root.master is None:
                    break
                root = root.master
        return root

    def unregister_idn(self):
        for el in [self, *self._elems, *self._frame]:
            if isinstance(el, Tile):
                try:
                    if el.idn:
                        del _global_reg[el.idn]
                except:
                    pass
                if el != self:
                    el.unregister_idn()

    def destroy(self):
        for f in [self.frame, *self._frame]:
            if f:
                f.destroy()
        self._frame = []
        self.frame = None

    def add(self, elem):
        elem.set_parent(self)
        self._elems.append(elem)
        return self

    def _init_frame(self):
        if self.frame != None:
            raise Exception("frame alive")
        p = self.parent_frame()

        # opts = { "borderwidth":2,  "relief":"ridge" }  ##todo debug

        self.frame = ttk.Frame(p)  ## **opts

    def _end_frame(self):
        # todo rename this ...
        self.destroy()

    def layout(self):
        self._end_frame()

        if self._visible:
            self._init_frame()

            self._build()

            self._pack_elems()
            self._pack_frame()

        return self

    def _build(self):
        el = self.create_element()
        self._add_frames(el)

        for el in self._elems:
            if isinstance(el, Tile):
                print_t("h...ups", self)
                el.layout()
                self._add_frames(el.frame)
            else:
                print_t("...ups")
                self._add_frames(el)

        return self

    def _add_frames(self, el):
        if el == None:
            return
        if type(el) in [list, tuple]:
            self._frame.extend(el)
        else:
            self._frame.append(el)

    def create_element(self):
        pass

    def _pack_elems(self):
        opts = self.layout_options()
        for el in self._frame:
            # print("_pack_elems", el, self)
            if isinstance(el, Tile):
                print_t("pack child tile")
                el._pack_frame()
            else:
                el.pack(opts)

    def _pack_frame(self):
        # print("_pack_frame", self)
        opts = self.layout_frame_options()

        if self._visible != True:
            return

        self.frame.pack(opts)

    def layout_options(self):
        opts = self.pref(
            "pack", {"anchor": CENTER, "side": "left", "pady": 5, "padx": 5}
        )
        return opts

    def layout_frame_options(self):
        opts = self.pref("pack_frame", {"anchor": W})
        return opts

    #

    def focus(self):
        if self.frame:
            self.frame.focus_set()

    #

    def pref(self, name, defval=None):
        v = self._kwargs.setdefault(name, defval)
        return v

    def set_pref(self, name, val):
        self._kwargs[name] = val

    def pref_int(self, name, defval=None, none_ok=False):
        val = self.pref(name, defval)
        if val is None:
            if not none_ok:
                raise Exception("None val")
            return None
        return int(val)

    def pref_float(self, name, defval=None, none_ok=False):
        val = self.pref(name, defval)
        if val is None:
            if not none_ok:
                raise Exception("None val")
            return None
        return float(val)

    def get_caption(self):
        return self.pref(CAPTION, "... caption not-set" + str(self))


class TileLabel(Tile):
    def create_element(self):
        width = self.pref_int(CAPTION_WIDTH, none_ok=True)
        self._var = StringVar()
        self._lbl = ttk.Label(self.frame, textvariable=self._var, width=width)
        self.text(self.get_caption())
        return self._lbl

    def text(self, t):
        self._var.set(t)


class ClickHandlerMixIn(object):
    def _click_handler(self):
        self.pref(ON_CLICK, self.on_click)(self)

    def on_click(self, ref_self):
        print_t(self.__class__.__name__, ON_CLICK)


class TileLabelClick(TileLabel, ClickHandlerMixIn):
    def create_element(self):
        lbl = super().create_element()
        lbl.config(foreground="blue")
        lbl.config(cursor="hand1")
        lbl.bind("<Button-1>", self._click_event_handler)
        return lbl

    def _click_event_handler(self, event):
        self._click_handler()


class TileButton(Tile, ClickHandlerMixIn):
    def create_element(self):

        text = self.pref("commandtext", "...")
        image = self.pref("icon", None)
        hotkey = self.pref("hotkey", None)
        command = self.pref("command", self._click_handler)

        self._button = ttk.Button(
            self.frame,
            text=text,
            image=image,
            command=command,
        )

        if image:
            if hotkey:
                text = text + " / " + hotkey
            ToolTip(self._button, msg=text)

        if hotkey:
            _add_hotkey(hotkey)
            root = self.get_root()
            root.bind(hotkey, lambda x: command())

        return self._button


class TileCheckbutton(Tile):
    def create_element(self):
        self._var = StringVar()
        self.set_val(self.pref(VALUE, False))

        self._var_str = StringVar()
        self._var_str.set(
            self.pref(CAPTION, ""),
        )

        self._checkbutton = ttk.Checkbutton(
            self.frame,
            variable=self._var,
            textvariable=self._var_str,
            onvalue=self.pref("on_val", True),
            offvalue=self.pref("off_val", False),
            command=self._click_handler,
        )
        return self._checkbutton

    def text(self, val):
        self._var_str.set(val)

    def get_val(self):
        return self._var.get()

    def set_val(self, val):
        return self._var.set(val)

    def _click_handler(self):
        self.pref(ON_CLICK, self.on_click)(self)

    def on_click(self, ref_self):
        print_t(ON_CLICK, self.get_val())


class TileLabelButton(TileLabel, TileButton):
    def create_element(
        self,
    ):
        TileLabel.create_element(self)
        TileButton.create_element(self)
        return [self._lbl, self._button]


class TileEntry(Tile):
    def create_element(self):
        width = self.pref_int(CAPTION_WIDTH, none_ok=True)
        self._lbl = ttk.Label(self.frame, text=self.get_caption(), width=width)
        self._var = self._create_var()
        self._entry = self._create_entry()

        try:
            val = self._val
        except:
            val = self.pref(VALUE, None)

        if val:
            self.set_val(val)

        return [self._lbl, self._entry]

    def _create_var(self):
        return StringVar()

    def _create_entry(self):
        width = self.pref_int("width", 20)
        te = ttk.Entry(self.frame, textvariable=self._var, width=width)
        self._bind_focus(te)
        return te

    def _bind_focus(self, te):
        te.bind("<FocusIn>", self.on_focus_enter)
        te.bind("<FocusOut>", self.on_focus_leave)
        self._old_val = None

    def focus(self):
        if self._entry:
            self._entry.focus_set()
        return self

    def get_val(self):
        return self._var.get()

    def clr(self):
        self.set_val("")
        return self

    def set_val(self, val=None):
        self._val = val
        self._var.set(val)
        return self

    def on_focus_enter(self, ev):
        self._old_val = self.get_val()

    def on_focus_leave(self, ev):
        try:
            nval = self.get_val()
            self._val = nval
        except:
            # validation error
            self.set_val(self._old_val)
            # todo error handling
            return
        if self._old_val != nval:
            self.on_change(self._old_val, nval)

    def on_change(self, oval, nval):
        self.pref(ON_CHANGE, self._on_change)(oval, nval)

    def _on_change(self, oval, nval):
        print_t(self, ON_CHANGE, "'" + str(oval) + "'", "'" + str(nval) + "'")


class TileEntryPassword(TileEntry):
    def _create_entry(self):
        te = ttk.Entry(self.frame, textvariable=self._var, show="*")
        return te

    def show(self, enable=True):
        show = "" if int(enable) == True else "*"
        self._entry.configure(show=show)


class TileEntryInt(TileEntry):
    def _create_var(self):
        return IntVar()

    def on_change(self, oval, nval):
        only_positiv = self.pref("only_positiv", None)
        if only_positiv == True and nval < 0:
            # todo error handling
            print_t("catched only_positiv")
            self.set_val(oval)
            return
        min_val = self.pref("min_val", None)
        if min_val != None:
            if nval < min_val:
                # todo error handling
                print_t("catched min_val")
                self.set_val(oval)
                return
        max_val = self.pref("max_val", None)
        if max_val != None:
            if nval > max_val:
                # todo error handling
                print_t("catched max_val")
                self.set_val(oval)
                return
        super().on_change(oval, nval)


class TileEntryText(TileEntry):
    def _create_entry(self):

        width = self.pref_int("width", 40)
        height = self.pref_int("height", 15)

        entry = scrolledtext.ScrolledText(
            self.frame,
            width=width,
            height=height,
        )
        if self.readonly:
            entry.config(state="disabled")

        return entry

    def __init__internal__(self):
        self.readonly = self.pref("readonly", False)

    def _preserve_state(self, begin=True):
        if self.readonly == False:
            return
        if begin:
            self._entry.config(state="normal")
        else:
            self._entry.config(state="disabled")

    def get_val(self):
        return self._entry.get("1.0", "end")

    def set_val(self, val):
        self.clr()
        self.append(val)

    def clr(self):
        self._preserve_state()
        self._entry.delete("1.0", "end")
        self._preserve_state(False)

    def append(self, val, nl=True):
        self._preserve_state()
        self._entry.insert("end", str(val))
        if nl:
            self._entry.insert("end", "\n")
        self._preserve_state(False)

    def extend(self, vals, nl=True):
        self._preserve_state()
        for val in vals:
            self._entry.insert("end", str(val))
            if nl:
                self._entry.insert("end", "\n")
        self._preserve_state(False)

    def gotoline(self, lineno=-1):
        if lineno < 0:
            lineno = "end"
        else:
            lineno = float(lineno)
        self._entry.yview_pickplace(lineno)

    def get_line_count(self):
        return int(float(self._entry.index("end-1c")))

    def remove_lines(self, first="1.0", last="end"):
        self._preserve_state()
        self._entry.delete(first, last)
        self._preserve_state(False)


class TileEntryButton(TileEntry, TileButton):
    def create_element(self):
        vars = TileEntry.create_element(self)
        TileButton.create_element(self)
        vars.append(self._button)
        return vars


class TileEntryCombo(TileEntry):
    def create_element(self):

        vars = super().create_element()

        values = list(self.pref(VALUES, []))
        self.set_values(values)

        sel_idx = self.pref("sel_idx", None)
        if sel_idx != None:
            self.set_index(sel_idx)

        return vars

    def _create_entry(self):
        width = self.pref_int("width", 20)
        self._combo = ttk.Combobox(self.frame, textvariable=self._var, width=width)
        self._combo.bind("<<ComboboxSelected>>", self._handler)

        self._bind_focus(self._combo)

        return self._combo

    def _handler(self, event):
        idx = self.get_index()
        val = self.get_val()
        self.pref(ON_SELECT, self.on_select)(idx, val)

    def on_select(self, ref_self, idx, val):
        print(self.__class__.__name__, ON_SELECT, self.get_select())

    def get_index(self):
        return self._combo.current()

    def set_index(self, pos):
        self._combo.current(pos)

    def set_values(self, values):
        self._values = values
        mf = self.pref(MAP_VALUE, lambda x: x)
        self._map_values = list(map(mf, self._values))
        self._combo[VALUES] = self._map_values

    def get_values(self):
        return self._combo[VALUES]

    def get_select(self):
        # todo refactor ?
        idx = self.get_index()
        if idx < 0:
            return
        return self._values[idx]


class TileEntryListbox(TileEntry):
    def __init__internal__(self):
        super().__init__internal__()
        self.scrollbar()

        self._lastsel = None

        self._show_scrollb = self.pref("show_scroll", False)
        self._auto_scrollb = int(self.pref("max_show", 5))
        vals = self.pref(VALUES, [])
        self._values = list(vals if vals else [])

        self._width = int(self.pref("width", 20))

        self._sel_mode = int(self.pref("select_many", False))
        ##todo self._height = int(self.pref("height", 5))

    def destroy(self):
        super().destroy()
        ## init tile (move?)
        self._lastsel = None

    def scrollbar(self, enable=True):
        self._scrollable = enable
        return self

    def set_values(self, values):
        self._do_map(values)
        self._scroll_height()
        self.clr_selection()

        if not self._scrollable:
            self._scrollb_y.forget()
        else:
            self._scrollb_y_pack()

    def _do_map(self, values):
        mf = self.pref(MAP_VALUE, lambda x: f"{x} > {x}")
        self._values = list(values)
        self._map_values = list(map(mf, values))
        self._var.set(self._map_values)

    def create_element(self):

        self._listb_wg_parent = ttk.Frame(self.frame)
        self._listb_wg = ttk.Frame(self._listb_wg_parent)

        vars = super().create_element()
        # print("list", self, vars)

        self._do_map(self._values)

        if len(self._values) > 0:
            self.set_val(self._values[0])

        return vars

    def _pack_elems(self):
        super()._pack_elems()

        self._listb.pack({"side": "left"})

        self._scrollb_x = ttk.Scrollbar(
            self._listb_wg_parent,
            orient=HORIZONTAL,
            command=self._listb.xview,
        )

        self._listb.configure(xscrollcommand=self._scrollb_x.set)
        self._scrollb_x.pack(side="bottom", fill="both", padx=0)

        self._scrollb_y = ttk.Scrollbar(
            self._listb_wg,
            orient=VERTICAL,
            command=self._listb.yview,
        )
        self._listb.configure(yscrollcommand=self._scrollb_y.set)

        self._scrollb_y_pack()

        if not self._show_scrollb:
            if not self._scrollable:
                self._scrollb_y.forget()

        self._listb_wg.pack(anchor=CENTER, side="left", padx=0, pady=0)
        self._listb_wg_parent.pack(anchor=CENTER, side="left", padx=0, pady=0)

        self._listb.bind("<<ListboxSelect>>", self._select_handler)
        self._listb.bind("<Button-3>", self._right_click_handler)
        self._listb.bind("<Double-Button-1>", self._double_click_handler)

    def _scrollb_y_pack(self):
        self._scrollb_y.pack(side="right", fill="both", padx=0)

    def _scroll_height(self):
        self.scrollbar()
        h = len(self._values)
        if h > self._auto_scrollb:
            self.scrollbar(True)
        else:
            self.scrollbar(False)
        h = self._auto_scrollb
        return h

    def _create_entry(self):

        h = self._scroll_height()

        self._listb = Listbox(
            self._listb_wg,
            listvariable=self._var,
            exportselection=False,
            height=h,
            width=self._width,
            selectmode="multiple" if self._sel_mode else None,
        )

        return self._listb_wg_parent

    def _right_click_handler(self, event):
        self.pref(ON_RIGHT_CLICK, self.on_right_click)(self)

    def on_right_click(self, ref_self):
        print_t(ON_RIGHT_CLICK, ref_self)

    def _double_click_handler(self, event):
        # sel = self._listb.curselection()
        self.pref(ON_DOUBLE_CLICK, self.on_double_click)(self)

    def on_double_click(self, ref_self):
        print_t(ON_DOUBLE_CLICK, ref_self)

    def _select_handler(self, event):
        if self._sel_mode:
            # todo select and unselect
            self.pref("on_sel", self.on_sel)(self)
            return
        sel = self._listb.curselection()
        nullable = self.pref("nullable", True)
        if sel == self._lastsel and nullable:
            sel = None
            self.clr_selection()
            self.pref(ON_UNSELECT, self.on_unselect)(self)
        else:
            self.pref(ON_SELECT, self.on_select)(self)
        self._lastsel = sel

    def get_selection(self):
        sel = self._listb.curselection()
        return sel

    def get_selection_values(self):
        sel = self._listb.curselection()
        vals = list(map(lambda x: (x, self._values[x]), sel))
        return vals

    def set_selection(self, vals):
        self.clr_selection()
        if vals == -1:
            # select all
            vals = self._values
        for v in vals:
            try:
                idx = self._values.index(v)
                self._listb.selection_set(idx)
                self._listb.see(idx)
            except:
                print_t("not found", v)

    def on_sel(self, ref_self):
        print_t(
            self.__class__.__name__, "on_sel", ref_self, ref_self.get_selection_values()
        )

    def on_select(self, ref_self):
        print_t(self.__class__.__name__, ON_SELECT, ref_self.get_val())

    def on_unselect(self, ref_self):
        print_t(self.__class__.__name__, ON_UNSELECT, ref_self.get_val())

    def get_val(self):
        idx = self.get_index()
        if idx is not None:
            return (idx, self._values[idx])

    def get_index(self):
        idx = self._listb.curselection()  # no range
        if len(idx) == 0:
            return None
        else:
            idx = idx[0]
        return idx

    def set_index(self, idx=0):
        if idx < 0:
            idx = len(self._values) + idx if self._values else 0
        self._listb.selection_set(idx)
        self._listb.see(idx)

    def get_mapval(self):
        val = self.get_val()
        if val:
            return val[1]

    def clr_selection(self):
        self._listb.select_clear(0, END)
        self._lastsel = None

    def set_val(self, val):
        self.clr_selection()
        if val:
            idx = self._values.index(val)
            self.set_index(idx)
            self._lastsel = self.get_index()


class TileEntrySpinbox(TileEntry):
    def create_element(self):

        vars = super().create_element()

        self._values = list(self.pref(VALUES, []))
        mf = self.pref(MAP_VALUE, lambda x: f"{x} > {x}")
        self._map_values = list(map(mf, self._values))

        _spin_opts = self.pref("spin_opts", {})
        _spin_opts[VALUES] = self._map_values

        self._spinb.config(**_spin_opts)

        return vars

    def _create_entry(self):
        self._spinb = ttk.Spinbox(self.frame, textvariable=self._var)
        self._spinb.bind("<<Increment>>", self._change_handler)
        self._spinb.bind("<<Decrement>>", self._change_handler)
        return self._spinb

    def _change_handler(self, event):
        self.pref(ON_CHANGE, self.on_change)()

    def on_change(self):
        print_t(self.__class__.__name__, ON_CHANGE, self.get_index(), self.get_val())

    def get_index(self):
        return self._map_values.index(self.get_val())

    def get_val(self):
        return self._spinb.get()

    def set_val(self, val):
        self._spinb.set(val)


class TileFileSelect(TileEntryButton):

    PATH = "path"
    """path: always add os.sep at the end"""

    def create_element(self):
        vars = super().create_element()

        self._filetypes = self.pref("filetypes", self.file_types())

        path = self.pref(self.PATH, self.get_base())
        self.path = self.fullpath(path)
        self.set_val(self.path)

        self._bind_focus(self._entry)

        return vars

    def _bind_focus(self, te):
        te.bind("<FocusIn>", self.on_focus_enter)
        te.bind("<FocusOut>", self.on_focus_leave)

    def on_click(self, o):

        basedir = os.path.dirname(self.get_val())

        file = filedialog.askopenfilename(
            initialdir=basedir, title=self.get_caption(), filetypes=self._filetypes
        )

        if file:
            self.set_val(file)
            self._on_select_file()

    def on_focus_enter(self, ev):
        pass

    def on_focus_leave(self, ev):
        self._on_select_file()

    def _on_select_file(self):
        file = self.get_val()
        if self.path != file:
            print_t("selected", file)
            self.pref(ON_SELECT, self.on_select)(file)

    def on_select(self, file):
        print(ON_SELECT, file)

    def get_base(self):
        return os.getcwdb()

    def file_types(self):
        return [("all files", "*.*")]

    def fullpath(self, path):
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        path = os.path.abspath(path)
        return path


class TileDirectorySelect(TileFileSelect):
    def on_click(self, o):

        basedir = self.get_val()

        file = filedialog.askdirectory(
            initialdir=basedir,
            title=self.get_caption(),
        )

        if file:
            print_t("selected", file)
            self.set_val(file)
            self.pref(ON_SELECT, self.on_select)(file)


class TileCompositFlow(Tile):
    def create_element(self):
        # print("create_element", self.__class__)
        vars = []
        for el in self.pref(SOURCE, []):

            if el == None:
                continue

            el.set_parent(self.frame)
            el.layout()

            opts = self._flow_pack_options(el)
            if opts:
                el.frame.pack(**opts)

            vars.append(el)

        return []

    def _flow_pack_options(self, el):
        pass

    def unregister_idn(self):
        super().unregister_idn()
        for el in self.pref(SOURCE, []):
            if isinstance(el, Tile):
                try:
                    if el.idn:
                        del _global_reg[el.idn]
                except:
                    pass
                el.unregister_idn()


class TileRows(TileCompositFlow):
    pass


class TileCols(TileCompositFlow):
    def _flow_pack_options(self, el):
        opts = self.layout_options()
        opts["anchor"] = W
        return opts

    def layout_options(self):
        return super().layout_options()
        # return {"anchor": CENTER, "side": "left", "pady": 5, "padx": 5}


class TileTab(Tile):
    def __init__internal__(self):
        self._tabs = {}
        self._tabs_show = {}

    def create_element(self):

        self._tab = ttk.Notebook(self.frame)
        self._elem = []
        self._tabs.clear()

        for el in self.pref(SOURCE, []):
            caption = ""
            if type(el) == tuple:
                caption = el[0]
                if type(caption) == tuple:
                    caption, idn = caption
                else:
                    idn = "tab_" + caption
                if len(el) > 2:
                    # visible or not
                    self._tabs_show[idn] = el[2]

            if idn not in self._tabs_show:
                self._tabs_show[idn] = True

            if self._tabs_show[idn]:
                elem = el[1]
                elem.set_parent(self.frame)
                elem.layout()
                self._elem.append(elem)

                self._tab.add(elem.frame, text=caption)

                idx = str(len(self._tab.tabs()) - 1)
                self._tabs[idn] = idx

            self._tab_sel = 0

        self._tab.bind("<<NotebookTabChanged>>", self._tab_handler)
        return self._tab

    def _tab_handler(self, event):
        cur = self.get_index()
        if cur == self._tab_sel:
            return
        self._tab_sel = cur
        self.pref(ON_CHANGE, self.on_change)()

    def on_change(self):
        selidx = self.get_index()
        nam = list(filter(lambda x: int(x[1]) == selidx, self._tabs.items()))
        print_t(self.__class__.__name__, ON_CHANGE, selidx, nam)

    def get_index(self):
        return self._tab.index(self._tab.select())

    def select(self, nam):
        print_t("select", self._tabs)
        idx = self._tabs[nam]
        self._tab.select(idx)

    def show_tab(self, idn, show=True):
        # todo
        raise Exception("untested")
        self._tabs_show[idn] = show

    def hide_tab(self, idn):
        # todo
        raise Exception("untested")
        self.show_tab(idn, False)


class TileTreeView(Tile):
    def create_element(self):

        header = self.pref("header", [])
        header_width = self.pref("header_width", [])
        height = self.pref("height", None)

        self.header_name = []
        self.header_title = []

        for key, cap in header:
            self.header_name.append(key)
            if cap is None:
                cap = key
            self.header_title.append(cap)

        self._cont = ttk.Frame(self.frame)

        self._treeview = ttk.Treeview(
            self._cont,
            columns=self.header_name,
            show="headings",
            height=height,
        )
        self._treeview.bind("<<TreeviewSelect>>", self._select_handler)

        self._yscroll = ttk.Scrollbar(
            self._cont, orient="vertical", command=self._treeview.yview
        )
        self._treeview.configure(yscrollcommand=self._yscroll.set)

        self._treeview.pack(side="left")
        self._yscroll.pack(side="right", fill="both", padx=0)

        for key, cap in header:
            if cap is None:
                cap = key
            self._treeview.heading(key, text=cap)

        for i in range(0, len(header_width)):
            width = header_width[i]
            if width:
                self._treeview.column(self.header_name[i], width=width)

        values = self.pref(VALUES, [])
        self.set_values(values)

        return self._cont

    def _select_handler(self, event):
        print("_select_handler", event)
        self.pref(ON_CLICK, self.on_select)(self)

    def on_select(self, ref_self):
        print_t(
            self.__class__.__name__,
            ON_SELECT,
        )

        sel = self._treeview.focus()
        sel = self._treeview.item(sel)

        nullable = self.pref("nullable", True)

    def clear(self):
        self._treeview.delete(*self._treeview.get_children())

    def set_values(self, values, mapval=True):
        print("set_values", values)
        self._values = values
        self._iid = []
        self.clear()
        for v in self._values:
            if mapval:
                try:
                    v = v.__dict__
                except:
                    pass
                rec = self.get_record(v)
            else:
                rec = v

            iid = self._treeview.insert("", "end", values=rec)
            self._iid.append(iid)

    def get_record(self, vals):
        rec = list(map(lambda x: vals[x], self.header_name))
        return rec

    def get_iid(self, val):
        pos = self._values.index(val)
        return self._iid[pos]

    def clr_selection(self):
        if len(self._treeview.selection()) > 0:
            self._treeview.selection_remove(self._treeview.selection())

    def set_selection(self, vals):
        self.clr_selection()
        if vals == -1:
            vals = self._iid
        else:
            vals = list(map(lambda x: self.get_iid(x), vals))
        for v in vals:
            self._treeview.selection_add(v)
            self._treeview.see(v)

    def get_selection(self):
        return self._treeview.selection()

    def get_selection_values(self):
        sel = self.get_selection()
        vals = []
        for iid in sel:
            try:
                pos = self._iid.index(iid)
                vals.append(self._values[pos])
            except:
                print("not found", iid)

        return vals
