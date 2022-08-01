_tk_root = None


def set_tk_root(tk_root):
    global _tk_root
    _tk_root = tk_root
    return tk_root


def get_tk_root():
    return _tk_root
