"""source_cache.py

Used to cache and retrieve source code.
This is especially useful when a custom REPL is used.

Note that we monkeypatch Python's linecache.getlines.
"""
import inspect
import linecache
import time
from typing import Any, Dict, Generator, List, Optional

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
        linecache.cache[filename] = entry
        self.local_cache[filename] = lines

    def remove(self, filename: str) -> None:
        """Removes an entry from the cache if it can be found."""
        if filename in self.local_cache:
            del self.local_cache[filename]
        if filename in linecache.cache:
            del linecache.cache[filename]
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
        # Adding ["\n"] is required when dealing with EOF errors
        # Do not use append; see #174.
        return lines + ["\n"]


cache = Cache()

# Monkeypatch linecache to make our own cached content available to Python.
linecache.getlines = cache.get_source_lines


def _counter() -> Generator[int, None, None]:
    num = 0
    while True:
        yield num
        num += 1


counter = _counter()


def friendly_exec(
    source: Any,
    globals_: Optional[Dict[str, None]] = None,
    locals_: Optional[Dict[str, None]] = None,
) -> None:
    """A version of exec that uses a different filename each time
    instead of the Python default '<string>', and caches the source.
    This makes it possible to provide more help on code executed via 'exec'.
    """
    # We use globals_ instead of globals as an argument name
    # (and similarly for locals_)
    # because friendly_traceback would give a warning about redefining
    # the builtins globals and locals if an exception were to be raised.

    # Note: if locals_ is None, we do not want to assign variables to
    # locals() defined inside this function, or globals() defined in this
    # module, but rather to that of the calling scope which is what exec does.
    frame = inspect.getouterframes(inspect.currentframe())[1].frame
    true_globals = frame.f_globals
    true_locals = frame.f_locals
    if globals_ is None:
        globals_ = true_globals
        if locals_ is None:
            locals_ = true_locals
    else:
        if locals_ is None:
            locals_ = true_globals
    # Let any exception bubble up: they will be correctly handled
    # by friendly-traceback
    if not isinstance(source, str):
        return exec(source, globals_, locals_)

    filename = "<friendly-exec-%d>" % next(counter)
    cache.add(filename, source)
    code = compile(source, filename, "exec")
    return exec(code, globals_, locals_)
