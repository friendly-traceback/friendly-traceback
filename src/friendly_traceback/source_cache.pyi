from typing import Any, Dict, List, Optional, Iterator, Callable

old_getlines: Callable[..., list[str]]

class Cache:
    context: int
    local_cache: dict[str, list[str]]

    def __init__(self) -> None: ...
    def add(self, filename: str, source: str) -> None: ...
    def remove(self, filename: str) -> None: ...
    def get_source_lines(
        self, filename: str, module_globals: Optional[Dict[str, Any]] = None
    ) -> List[str]: ...

cache: Cache
counter: Iterator[int]

def friendly_exec(
    source: str,
    globals_: Optional[Dict[str, None]] = None,
    locals_: Optional[Dict[str, None]] = None,
) -> None: ...
