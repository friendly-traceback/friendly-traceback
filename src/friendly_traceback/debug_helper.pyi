from typing import Literal

import inspect
import sys
from typing import Optional
from .ft_gettext import current_lang

DEBUG: Literal[False] = False
SHOW_DEBUG_HELPER: Literal[False] = False


def log_error(exc: Optional[BaseException] = None) -> None: ...


def log(*args: str) -> None: ...


def handle_internal_error(arg: str) -> None: ...
