import sys

import tkinter as tk
import tkinter.ttk as ttk

# from PIL import Image, ImageTk


from tkinter import StringVar, IntVar, Menu

from tkinter.scrolledtext import ScrolledText

from tktooltip import ToolTip

from tkuicore import tk_get_root, tk_get_icon, tk_get_add_par, tk_add_hotkey, tk_add_bg_callb, tk_open_browser_url


#

class TNContext(object):
    def __repr__(self):
        return str(self.__dict__)


#


class TNLabel(ttk.Label):

    def __init__(self, *args, **kwargs):
        self.var = StringVar()
        text = tk_get_add_par("text", "", kwargs)
        self.set_val(text)

        image = tk_get_add_par("image", None, kwargs)
        self.image_con = tk_get_icon(image) if image else None

        super().__init__(*args, textvariable=self.var, image=self.image_con, **kwargs)

    def get_val(self):
        return self.var.get()

    def set_val(self, val):
        return self.var.set(val)


class TNLabelClick(TNLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(foreground="blue")
        self.config(cursor="hand2")
        self.bind("<Button-1>", self._on_click)

    def _on_click(self, ev):
        self.on_click()

    def on_click(self):
        print("click", self)


class TNLabelClickUrl(TNLabelClick):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ToolTip(self, "open in external web browser")

    def set_url(self, url):
        self._url = url
        return self

    def on_click(self):
        try:
            url = self._url
            if url is None or len(url) == 0:
                raise Exception()
        except Exception as ex:
            url = self.get_val()
        # print("click-url", self, url)
        tk_open_browser_url(url)

#


class TNButton(ttk.Button):

    def __init__(self, *args, **kwargs):
        image = tk_get_add_par("image", None, kwargs)
        imagefg = tk_get_add_par("imagefg", "black", kwargs)
        textx = tk_get_add_par("text", "...", kwargs)
        hotkey = tk_get_add_par("hotkey", None, kwargs)
        self.image_con = tk_get_icon(image, fg=imagefg) if image else None

        super().__init__(*args, image=self.image_con, text=textx, **kwargs)

        if hotkey:
            textx += f" / {hotkey}"
            tk_add_hotkey(hotkey, lambda: self._on_click(None))

        ToolTip(self, textx)
        self.bind("<1>", self._on_click)

    def _on_click(self, ev):
        self.on_click()

    def on_click(self):
        print("click", self)

#


class TNCheckButton(ttk.Checkbutton):

    def __init__(self, *args, **kwargs):
        self.var = tk.BooleanVar()

        infotext = tk_get_add_par("infotext", None, kwargs)
        image = tk_get_add_par("image", None, kwargs)
        self.image_con = tk_get_icon(image) if image else None

        super().__init__(*args, variable=self.var,
                         command=self._on_change, image=self.image_con, **kwargs)
        if infotext:
            ToolTip(self, infotext)

    def get_val(self):
        return self.var.get()

    def set_val(self, val):
        return self.var.set(val)

    def _on_change(self):
        self.on_change(self.get_val())

    def on_change(self, curval):
        print("changed", self, curval)

#


class TNEntry(ttk.Entry):
    def __init__(self, *args, **kwargs):

        self.min_val = None
        self.max_val = None

        textvariable = tk_get_add_par("textvariable", None, kwargs)
        if textvariable:
            self.var = textvariable
        else:
            self.var = self._create_var()

        super().__init__(*args, textvariable=self.var, **kwargs)

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _create_var(self):
        return None

    def set_val(self, val):
        self.var.set(val)

    def get_val(self):
        return self.var.get()

    def conv(self, val):
        return val

    def validate(self):
        try:
            cur_val = self.conv(self.get_val())
        except Exception as ex:
            print("conv error", ex)
            return False

        if self.min_val is not None:
            if cur_val < self.min_val:
                # print("too small")
                return False
        if self.max_val is not None:
            if cur_val > self.max_val:
                # print("too big")
                return False
        return True

    def _on_focus_in(self, ev):
        self.old_val = self.get_val()

    def _on_focus_out(self, ev):
        if self.validate():
            cur_val = self.get_val()
            if cur_val != self.old_val:
                self.on_change(cur_val)
            self.old_val = None
        else:
            self.set_val(self.old_val)
        self.old_val = None

    def on_change(self, val):
        print("changed", self, val)


class TNEntryString(TNEntry):
    def _create_var(self):
        return StringVar()


class TNEntryInt(TNEntry):
    def _create_var(self):
        self.min_val = 1
        return IntVar()

    # def conv(self,val):
    #     return int(val, 10)


#

class TNCombobox(ttk.Combobox):
    def __init__(self, *args, **kwargs):
        self.var = tk.StringVar()
        super().__init__(*args, textvariable=self.var, **kwargs)
        self.bind('<<ComboboxSelected>>', self._on_change)

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _on_change(self, ev):
        cur_val = self.get_val()
        self.on_change(cur_val)

    def _on_focus_in(self, ev):
        self.old_val = self.get_val()

    def _on_focus_out(self, ev):
        cur_val = self.get_val()
        if cur_val != self.old_val:
            self.on_change(cur_val)
        self.old_val = None

    def on_change(self, val):
        print("changed", self, val)

    def get_val(self):
        return self.var.get()

    def set_val(self, val):
        return self.var.set(val)

    def set_values(self, vals):
        self['values'] = vals

    def get_values(self):
        return self['values']


#

class TNListbox(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(args[0])

        _items = tk_get_add_par("values", [], kwargs)
        self.var_items = tk.Variable(value=_items)

        self.lb = tk.Listbox(self, listvariable=self.var_items,
                             exportselection=False, **kwargs)
        self.lb.grid(row=0, column=0, sticky=tk.NSEW)

        self.configure_scroll()

        self.lb.bind('<<ListboxSelect>>', self._on_click)
        self.lb.bind('<3>', self._on_clickr)

    #

    def curselection(self):
        return self.lb.curselection()

    #

    def clr_selection(self):
        self.lb.select_clear(0, "end")

    def selected_values(self):
        sel = self.curselection()
        return [self.var_items.get()[x] for x in sel]

    def select_index(self, idx):
        self.lb.selection_set(idx)
        self.lb.see(idx)

    def select_values(self, select_vals=None):
        self.clr_selection()
        if select_vals is None:
            return
        if select_vals == -1:
            select_vals = self.var_items.get()
        for i, sel in enumerate(self.var_items.get()):
            if sel in select_vals:
                self.lb.selection_set(i)
                self.lb.see(i)

    #

    def _on_clickr(self, ev):
        ctx = self._context_from_event(ev)
        self.on_clickr(ctx)

    def on_clickr(self, ctx):
        print("click-r", self, ctx, ctx.row in ctx.selected)

    #
    def _context_from_event(self, ev):

        ctx = TNContext()

        ctx.ev = ev
        xp = ctx.x = ev.x
        yp = ctx.y = ev.y
        ctx.button = ev.num

        ctx.row = self.lb.nearest(ev.y)

        ctx.selected = self.lb.curselection()

        return ctx

    def _on_click(self, ev):
        selected_indices = self.lb.curselection()
        self.on_click(selected_indices)

    def on_click(self, selected):
        print("sel", self, selected)

    #

    def set_values(self, items):
        self.var_items.set(items)
        self.configure_scroll()

    #

    def configure_scroll(self):
        cur_height = self.lb.config("height")[-1]
        cur_width = self.lb.config("width")[-1]

        _items = self.var_items.get()

        if len(_items) > cur_height:
            sy = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.lb.yview)
            sy.grid(row=0, column=1, sticky=tk.NSEW)
            self.lb.configure(yscrollcommand=sy.set)

        else:
            pass
            # print("remove y scroll")

            empty = ttk.Frame(self)
            empty.grid(row=0, column=1, sticky=tk.NSEW)
            self.lb.configure(yscrollcommand=None)

        if len(_items) > 0:
            max_width = max(map(lambda x: len(x), _items))

            if max_width > cur_width:
                sx = ttk.Scrollbar(self, orient=tk.HORIZONTAL,
                                   command=self.lb.xview)
                sx.grid(row=1, column=0, sticky=tk.NSEW)
                self.lb.configure(xscrollcommand=sx.set)

            else:
                # print("remove x scroll")

                empty = ttk.Frame(self)
                empty.grid(row=1, column=0, sticky=tk.NSEW)
                self.lb.configure(xscrollcommand=None)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

#


class TNScrolledText(ScrolledText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<FocusIn>", self._focus_in)
        self.bind("<FocusOut>", self._focus_out)
        self.readonly = False
        self.old_val = None

    def set_readonly(self):
        self.config(state=tk.DISABLED)
        self.readonly = True
        return self

    def _focus_in(self, ev):
        if self.readonly:
            return
        self.old_val = self.get_val()

    def _focus_out(self, ev):
        if self.readonly:
            return
        cur_val = self.get_val()
        if cur_val != self.old_val:
            self.on_change(cur_val)
        self.old_val = None

    def _preserve_state(self, begin=True):
        if self.readonly == False:
            return
        if begin:
            self.config(state=tk.NORMAL)
        else:
            self.config(state=tk.DISABLED)

    def on_change(self, cur_val):
        print("changed", self, cur_val)

    def get_val(self):
        return self.get("1.0", "end")

    def set_val(self, val):
        self.clr()
        self.append(val)

    def clr(self):
        self.remove_lines()

    def append(self, val, nl=True):
        self._preserve_state()
        self.insert("end", str(val))
        if nl:
            self.insert("end", "\n")
        self._preserve_state(False)

    def extend(self, vals, nl=True):
        self._preserve_state()
        for val in vals:
            self.insert("end", str(val))
            if nl:
                self.insert("end", "\n")
        self._preserve_state(False)

    def gotoline(self, lineno=-1):
        if lineno < 0:
            lineno = "end"
        else:
            lineno = float(lineno)
        self.yview_pickplace(lineno)

    def get_line_count(self):
        return int(float(self.index("end-1c")))

    def remove_lines(self, first="1.0", last="end"):
        self._preserve_state()
        self.delete(first, last)
        self._preserve_state(False)


#


class TNContextMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(tearoff=0, *args, **kwargs)
        self.bind("<Leave>", lambda x: self.destroy())

    def show(self, ev):
        self.post(ev.x_root, ev.y_root)

    def hide(self):
        self.destroy()

    def add_command(self, label, command,  *args, **kwargs):

        def _call(args):
            self.hide()
            if command:
                command(args)

        super().add_command(label=label, command=lambda: _call(args),  *args, **kwargs)

#


class TNTreeview(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(args[0])

        self._columns = tk_get_add_par("columns", None, kwargs)

        self.tree = ttk.Treeview(self, columns=self._columns, **kwargs)
        self.sy = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.sy.set)

        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.sy.grid(row=0, column=1, sticky=tk.NSEW)

        self.columnconfigure(0, weight=1)
        # self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # self.tree.bind("<<TreeviewOpen>>", self._node_open)
        # self.tree.bind("<<TreeviewClose>>", self._node_close)
        self.tree.bind("<<TreeviewSelect>>", self._tree_select)
        self.tree.bind("<Double-1>", self._tree_double_click)
        self.tree.bind("<3>", self._tree_context_menu)

        self._iid = []

    def config_column(self, namid, text=None, width=None, anchor=None):
        if text:
            self.tree.heading(namid, text=text)
        if width:
            self.tree.column(namid, width=width)
        if anchor:
            self.tree.column(namid, anchor=anchor)

    def clear(self):
        self._iid.clear()
        self.tree.delete(*self.tree.get_children())

    def insert(self, *args, **kwargs):
        iid = self.tree.insert(*args, **kwargs)
        self._iid.append(iid)
        return iid

    def set(self, *args, **kwargs):
        return self.tree.set(*args, **kwargs)

    # def _node_open(self, ev):
    #     print("node open", ev, self._iid_from_event(ev))

    # def _node_close(self, ev):
    #     print("node close", ev, self._iid_from_event(ev))

    def _int(self, x):
        return int(x[1:], 16)

    def _sel2row(self, sel):
        try:
            return self._iid.index(sel)
        except:
            print("not found", sel, file=sys.stderr)
            return -1

    def _get_sel_num(self):
        select = self.tree.selection()

        # selnum = list(map(lambda x: self._int(x), select))

        selrows = list(map(lambda x: self._sel2row(x), select))

        return select, selrows

    def clr_selection(self):
        if len(self.tree.selection()) > 0:
            self.tree.selection_remove(self.tree.selection())

    def select_row(self, row):
        assert row >= 0 and row < len(self._iid)
        v = self._iid[row]
        self.tree.selection_add(v)
        self.tree.see(v)

    def get_selected_rows(self):
        return self._get_sel_num()[1]

    def _tree_select(self, ev):
        if self.on_click:
            select, selnum = self._get_sel_num()
            self.on_click(select, selnum)

    def on_click(self, selected, sel_nums):
        print("click", selected, sel_nums)

    def _tree_double_click(self, ev):
        ctx = self._context_from_event(ev)
        if ctx.heading is False:
            self.on_click_dbl(ctx)
        else:
            self.on_click_dbl_header(ctx)

    def on_click_dbl(self, ctx):
        print("click-dbl", ctx.iid, ctx.row, ctx.column)

    def on_click_dbl_header(self, ctx):
        print("click-dbl-header", ctx)

    def _tree_context_menu(self, ev):
        ctx = self._context_from_event(ev)
        self.on_clickr(ctx)

    def on_clickr(self, ctx):
        if ctx.heading is False:
            print("click-r", ctx, ctx.iid in ctx.select)
        else:
            print("click-r", ctx)

    def _context_from_event(self, ev):

        ctx = TNContext()

        ctx.ev = ev
        xp = ctx.x = ev.x
        yp = ctx.y = ev.y
        ctx.button = ev.num

        ctx.select, ctx.selnum = self._get_sel_num()

        ctx.region = self.tree.identify("region", xp, yp)
        ctx.heading = ctx.region == 'heading'

        ctx.row = self.tree.identify("row", xp, yp)
        if ctx.row.startswith("I"):
            ctx.row = ctx.row, self._sel2row(ctx.row)

        ctx.column = self.tree.identify("column", xp, yp)
        if ctx.column.startswith("#"):
            no = int(ctx.column[1:])
            nam = self._columns[no-1] if no > 0 else ctx.column
            ctx.column = (ctx.column, no, nam)

        if ctx.heading:
            return ctx

        ctx.iid = self.tree.identify("item", xp, yp)
        ctx.iid_num = self._sel2row(ctx.iid)

        ctx.isopen = self.tree.item(ctx.iid, "open")

        return ctx


#


class TNNotebook(ttk.Notebook):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._names = {}

    def add(self, child, **kwargs):
        super().add(child, **kwargs)
        text = tk_get_add_par("text", None, kwargs)
        if text:
            self._names[text] = len(self._names)

    def hide_name(self, tabnam):
        if tabnam in self._names:
            self.hide(self._names[tabnam])

    def select_name(self, tabnam):
        if tabnam in self._names:
            self.select(self._names[tabnam])
        return True
