"""
    (c)2025 K. Goger - https://github.com/kr-g
    legal: https://github.com/kr-g/gitonic/blob/main/LICENSE.md
"""

import os


class Cell(object):
    def __init__(self, val=None, opts=None, calc_cb=None):
        self._sink_cb = []
        self._changed = False
        self._val = val
        self.opts = opts
        self._calc_cb = calc_cb

    def __repr__(self):
        return self.__class__.__name__ + "(" + str(self._val) + "," + str(self._changed) + ")"

    def _notify(self):
        for listener in self._sink_cb:
            try:
                listener(self)
            except Exception as ex:
                print("err", ex, file=os.stderr)

    def _run_calc(self, ref):
        self.val = self.calc(ref)
        return self.val

    def calc(self, ref):
        if self._calc_cb:
            return self._calc_cb(self, ref)
        # just return same value as source object
        return ref.val

    def add(self, listener):
        assert listener is not None
        self._sink_cb.append(listener)

    def listen(self, cell):
        cell.add(self._run_calc)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, v=None):
        if self._val != v:
            self._changed = True
            self._val = v

    def fire(self):
        if self._changed:
            self._changed = False
            self._notify()
            return True


class DataFlow(object):
    def __init__(self):
        self._cells = []

    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join([str(x) for x in self._cells]) + ")"

    def add(self, *args):
        for cell in args:
            if type(cell) == list:
                self._cells.extend(cell)
            else:
                self._cells.append(cell)

    def propagate(self):
        total = 0
        cells = list(filter(lambda x: x._changed, self._cells))
        for c in cells:
            if c.fire():
                total += 1
        return total
