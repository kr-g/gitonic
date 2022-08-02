import sys
from gitonic.main import main_func

# from .main import main_func as gui_func

if __name__ == "__main__":
    rc = main_func()
    sys.exit(rc)
