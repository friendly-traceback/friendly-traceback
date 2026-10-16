from typing import Callable

import inspect
import linecache
import time
from typing import Any, Dict, Generator, List, Optional
import stack_data

old_getlines: Callable[..., list[str]]


class Cache:
    context: int
    local_cache: dict[str, list[str]]

    def __init__(self) -> None: ...

    def add(self, filename: str, source: str) -> None: ...

    def remove(self, filename: str) -> None: ...

    def get_source_lines(self, filename: str, module_globals: Optional[Dict[str, Any]] = None) -> List[str]: ...


cache: Cache
counter: Generator[int]


def friendly_exec(source: Any, globals_: Optional[Dict[str, None]] = None, locals_: Optional[Dict[str, None]] = None) -> None: ...
