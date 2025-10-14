import logging
import sys
import os

#

sys.path.append(os.path.join(os.path.dirname(__file__)))

#

log = logging.getLogger('expert').addHandler(logging.NullHandler())
