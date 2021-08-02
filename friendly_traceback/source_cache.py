"""source_cache.py

Used to cache and retrieve source code.
This is especially useful when a custom REPL is used.

Note that we monkeypatch Python's linecache.getlines.
"""

import linecache
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

import stack_data

old_getlines = linecache.getlines  # To be monkeypatched.


class Cache:
    """Class used to store source of files and similar objects"""

    def __init__(self) -> None:
        self.cache: Dict[str, List[str]] = {}
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
        lines = [line + "\n" for line in source.splitlines()]
        entry = (len(source), time.time(), lines, filename)
        linecache.cache[filename] = entry  # type: ignore
        self.cache[filename] = lines

    def remove(self, filename: str) -> None:
        """Removes an entry from the cache if it can be found."""
        if filename in self.cache:
            del self.cache[filename]
        if filename in linecache.cache:  # type: ignore
            del linecache.cache[filename]  # type: ignore

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
        if not lines and filename in self.cache:
            lines = self.cache[filename]
        if not lines:  # can happen for f-strings and frozen modules
            lines = []
        lines.append("\n")  # required when dealing with EOF errors
        return lines


cache = Cache()

# Monkeypatch linecache to make our own cached content available to Python.
linecache.getlines = cache.get_source_lines


def highlight_source(
    lines: Sequence[stack_data.Line], text_range: Optional[Tuple[int, int]] = None
) -> Tuple[str, str]:
    """Extracts a few relevant lines from a file content given as a list
    of lines, adding line number information and identifying
    a particular line.

    When dealing with a ``SyntaxError`` or its subclasses, offset is an
    integer normally used by Python to indicate the position of
    the error with a ``^``, like::

        if True
              ^

    which, in this case, points to a missing colon. We use the same
    representation in this case.
    """
    if not lines:
        return "", ""
    new_lines = []
    problem_line = ""
    nb_digits = len(str(lines[-1].lineno))
    no_mark = "       {:%d}: " % nb_digits
    with_mark = "    -->{:%d}: " % nb_digits

    text_range_mark = None
    if text_range is not None:
        begin, end = text_range
        text_range_mark = " " * (8 + nb_digits + begin + 1) + "^" * (end - begin)

    marked = False
    for line_obj in lines:
        if line_obj is stack_data.LINE_GAP:
            new_lines.append(" " * 7 + "(...)")
        elif line_obj.is_current:
            num = with_mark.format(line_obj.lineno)
            problem_line = line_obj.text
            new_lines.append(num + problem_line.rstrip())
            if text_range_mark is not None:
                new_lines.append(text_range_mark)
            marked = True
        elif marked:
            if not line_obj.text.strip():  # do not add empty line if last line
                break
            num = no_mark.format(line_obj.lineno)
            new_lines.append(num + line_obj.text.rstrip())
        else:
            num = no_mark.format(line_obj.lineno)
            new_lines.append(num + line_obj.text.rstrip())
    return "\n".join(new_lines), problem_line
