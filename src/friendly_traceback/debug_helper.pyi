from typing import Literal

from typing import Optional

DEBUG: bool
SHOW_DEBUG_HELPER: bool

def log_error(exc: Optional[BaseException] = None) -> None: ...
def log(*args: str) -> None: ...
def handle_internal_error(arg: str) -> None: ...
