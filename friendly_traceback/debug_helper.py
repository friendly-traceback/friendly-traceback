"""Debug helper

The purpose of this file is to help during development.

The idea is to silence internal exceptions raised by Friendly
itself for most users by redirecting them here, and have them
printed only when debugging mode is activated.
"""
import os
import sys
from typing import Any, Optional

from .ft_gettext import current_lang

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


def log(text: Any) -> None:
    if DEBUG:  # pragma: no cover
        print("Log:", text)


def log_error(exc: Optional[BaseException] = None) -> None:
    if DEBUG:  # pragma: no cover
        if exc is not None:
            print(repr(exc))
        sys.exit()


def handle_internal_error() -> None:
    from . import explain_traceback, get_output, set_include, set_stream

    print(_("Please report this issue."))
    set_stream(redirect="capture")
    set_include("debug_tb")
    explain_traceback()
    result = get_output()
    dependencies = [
        item
        for item in ["executing", "stack_data", "asttokens", "pure_eval"]
        if item in result
    ]

    if dependencies:
        print(
            _(
                "The following package names used by friendly-traceback\n",
                "appear in the full traceback, which may indicate\n",
                "that one of them is the source of this error.",
            )
        )
        for dep in dependencies:
            print(dep)
    if DEBUG:
        print(result)
    log(_("Fatal error - aborting"))
    sys.exit()
