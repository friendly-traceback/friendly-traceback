"""source_cache.py

Used to cache and retrieve source code.
This is especially useful when a custom REPL is used.

Note that we monkeypatch Python's linecache.getlines.
"""

import linecache
import time
from typing import Any, Dict, List, Optional

import stack_data

old_getlines = linecache.getlines  # To be monkeypatched.


class Cache:
    """Class used to store source of files and similar objects"""

    def __init__(self) -> None:
        self.local_cache: Dict[str, List[str]] = {}
        self.context = 4

    def add(self, filename: str, source: str) -> None:
        """Adds a source (received as a string) corresponding to a filename
        in the cache.

        The filename can be a true file name, or a fake one, like
        <friendly-console:42>, used for saving an REPL entry.
        These fake filenames might not be retrieved by Python's linecache
        which is why we keep a duplicate of anything we add to linecache.cache
        """
        # filename could be a Path object,
        # which does not have a startswith() method used below
        filename = str(filename)
        self.remove(filename)
        lines = [line + "\n" for line in source.splitlines()]
        entry = (len(source), time.time(), lines, filename)
        # mypy cannot get the type information from linecache in stdlib
        linecache.cache[filename] = entry  # type: ignore
        self.local_cache[filename] = lines

    def remove(self, filename: str) -> None:
        """Removes an entry from the cache if it can be found."""
        if filename in self.local_cache:
            del self.local_cache[filename]
        if filename in linecache.cache:  # type: ignore
            del linecache.cache[filename]  # type: ignore
        # clear stack_data cache so it pulls fresh lines from linecache
        stack_data.Source._class_local("__source_cache", {}).pop(filename, None)

    def get_source_lines(
        self, filename: str, module_globals: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Given a filename, returns the corresponding source, either
        from the cache or from actually opening the file.

        If the filename corresponds to a true file, and the last time
        it was modified differs from the recorded value, a fresh copy
        is retrieved.

        The contents is stored as a string and returned as a list of lines,
        each line ending with a newline character.
        """
        lines = old_getlines(filename, module_globals=module_globals)
        if not lines and filename in self.local_cache:
            lines = self.local_cache[filename]
        if not lines:  # can happen for f-strings and frozen modules
            lines = []
        lines.append("\n")  # required when dealing with EOF errors
        return lines


cache = Cache()

# Monkeypatch linecache to make our own cached content available to Python.
linecache.getlines = cache.get_source_lines
