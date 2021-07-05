"""source_cache.py

Used to cache and retrieve source code.
This is especially useful when a custom REPL is used.

Note that we monkeypatch Python's linecache.getlines.
"""

import linecache
import time


old_getlines = linecache.getlines


class Cache:
    """Class used to store source of files and similar objects"""

    def __init__(self):
        self.context = 4

    def add(self, filename, source):
        """Adds a source (received as a string) corresponding to a filename
        in the cache.

        The filename can be a true file name, or a fake one, like
        <friendly-console:42>, used for saving an REPL entry.
        """
        # filename could be a Path object,
        # which does not have a startswith() method used below
        filename = str(filename)
        lines = [line + "\n" for line in source.splitlines()]
        entry = (len(source), time.time(), lines, filename)
        linecache.cache[filename] = entry

    def remove(self, filename):
        """Removes an entry from the cache if it can be found."""
        if filename in linecache.cache:
            del linecache.cache[filename]

    def get_source_lines(self, filename, module_globals=None):
        """Given a filename, returns the corresponding source, either
        from the cache or from actually opening the file.

        If the filename corresponds to a true file, and the last time
        it was modified differs from the recorded value, a fresh copy
        is retrieved.

        The contents is stored as a string and returned as a list of lines,
        each line ending with a newline character.
        """
        lines = old_getlines(filename, module_globals=module_globals)
        lines.append("\n")  # required when dealing with EOF errors
        return lines


cache = Cache()
