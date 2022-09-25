import os
import sys
import warnings


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from friendly_traceback import debug_helper

debug_helper.DEBUG = True
warnings.simplefilter("always")

