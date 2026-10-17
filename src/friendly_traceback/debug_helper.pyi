from typing import Literal

from typing import Optional

DEBUG: Literal[False] = False
SHOW_DEBUG_HELPER: Literal[False] = False

def log_error(exc: Optional[BaseException] = None) -> None: ...
def log(*args: str) -> None: ...
def handle_internal_error(arg: str) -> None: ...
