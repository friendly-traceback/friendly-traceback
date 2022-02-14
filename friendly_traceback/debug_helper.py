"""Debug helper

The purpose of this file is to help during development.

The idea is to silence internal exceptions raised by Friendly
itself for most users by redirecting them here, and have them
printed only when debugging mode is activated.
"""
import os
import sys
from typing import Optional

from .ft_gettext import current_lang

try:
    devtools_found = True
    from .devtools_patch import PatchedDebug
except ImportError:
    devtools_found = False

    def PatchedDebug(*args):
        pass


_ = current_lang.translate

# DEBUG is set to True for me. It can also be set to True from __main__ or when
# using the debug() command in the console.

IS_PYDEV = bool(os.environ.get("PYTHONDEVMODE", False))
IS_ANDRE = (
    r"users\andre\github\friendly" in __file__.lower()
    or r"users\andre\friendly" in __file__.lower()
)
DEBUG = IS_PYDEV or IS_ANDRE
SHOW_DEBUG_HELPER = False

if sys.version_info >= (3, 11):
    devtools_found = False
    if DEBUG:
        print("devtools is not supported for Python 3.11")


def log_error(exc: Optional[BaseException] = None) -> None:
    if DEBUG:  # pragma: no cover
        if exc is not None:
            print(repr(exc))
        sys.exit()


if DEBUG and devtools_found:
    # DEBUG could be turned off between defining here and calling
    def log(*args, **kwargs) -> None:
        if DEBUG:
            inner_log = PatchedDebug(additional_frame_depth=1)
            inner_log(*args, **kwargs)

    def log_1(*args, **kwargs) -> None:
        if DEBUG:
            inner_log = PatchedDebug(additional_frame_depth=2)
            inner_log(*args, **kwargs)

    def log_2(*args, **kwargs) -> None:
        if DEBUG:
            inner_log = PatchedDebug(additional_frame_depth=3)
            inner_log(*args, **kwargs)

else:

    def log(*args, **kwargs) -> None:
        pass

    log_2 = log_1 = log


def handle_internal_error(arg) -> None:
    print(_("Fatal error - aborting"))
    print(_("Please report this issue."))
    log_1(arg)
    sys.exit()
