"""Debug helper

The purpose of this file is to help during development.

The idea is to silence internal exceptions raised by Friendly
itself for most users by redirecting them here, and have them
printed only when debugging mode is activated.
"""
import inspect
import sys
from typing import Optional

from .ft_gettext import current_lang

_ = current_lang.translate

# DEBUG is set to True when running with pytest.
# It can also be set to True from __main__ or when
# using the debug() command in the console.

DEBUG = False
SHOW_DEBUG_HELPER = False


def log_error(exc: Optional[BaseException] = None) -> None:
    if DEBUG:  # pragma: no cover
        if exc is not None:
            print(repr(exc))
            frame = inspect.currentframe().f_back
            print(f"{frame.f_code.co_filename}, line: {frame.f_lineno}")
        sys.exit()


def log(*args: str) -> None:
    if DEBUG:
        for arg in args:
            print(arg)


def handle_internal_error(arg: str) -> None:
    print(_("Fatal error - aborting"), arg)
    print(_("Please report this issue."))
    sys.exit()
