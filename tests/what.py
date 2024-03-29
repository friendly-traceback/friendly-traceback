"""Creates a version of known.rst to insert in the documentation.
"""

import builtins
import os
import sys
import platform
from contextlib import redirect_stderr
this_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(this_dir, ".."))

import friendly_traceback

from friendly_traceback import console_helpers


# Make it possible to find docs
docs_root_dir = os.path.abspath(
    os.path.join(this_dir, "..", "..", "friendly-docs")
)
assert os.path.isdir(docs_root_dir), "Separate docs repo need to exist"

target = os.path.normpath(
    os.path.join(
        docs_root_dir, "source/known.rst"
    )
)

LANG = "en"
friendly_traceback.install()
friendly_traceback.set_lang(LANG)
friendly_traceback.set_formatter("docs")
friendly_traceback.debug_helper.DEBUG = False  # silence message about new cases

sys.path.insert(0, this_dir)
py_version = f"{sys.version_info.major}.{sys.version_info.minor}"


intro_text = """
Generic information about various exceptions
==============================================

.. note::

     The content of this page is generated by running
     what.py located in the ``tests/`` directory.
     This needs to be done explicitly, independently of updating the
     documentation using Sphinx.

This file contains the generic information provided by
Friendly-traceback about built-in exceptions.
By "generic information" we mean the information provided using
``what()`` in a friendly console.

Some exceptions will never be seen by users of Friendly-traceback.

For example, ``SystemExit`` and ``KeyboardInterrupt`` are never
intercepted by Friendly-traceback. Furthermore, exceptions such as
``GeneratorExit``, ``FloatingPointError``, and
``StopAsyncIteration``, would likely never be seen.

``FloatingPointError`` is actually
`not used by Python <https://docs.python.org/3.7/library/exceptions.html#FloatingPointError>`_.

``BaseException``, ``Exception``, and ``ArithmeticError`` are base classes which
are also not normally seen: some derived classes are normally used instead.

Information compiled using Friendly version: {friendly},
Python version: {python}

""".format(
    friendly=friendly_traceback.__version__, python=platform.python_version()
)


def write(text):
    sys.stderr.write(text + "\n")


def make_title(text):
    write("\n" + text)
    write("~" * len(text) + "\n")
    write(".. code-block:: none\n")


with open(target, "w", encoding="utf8") as out, redirect_stderr(out):
    write(intro_text)

    write("\n")
    write("Exceptions")
    write("----------")

    for item in dir(builtins):
        try:
            exc = eval(item)  # skipcq PYL-W0123
        except Exception:  # noqa
            continue
        try:
            if not issubclass(exc, BaseException) or issubclass(exc, Warning):
                continue
        except Exception:  # noqa
            continue
        make_title(item)
        console_helpers.what(item, pre=True)

    write("\n")
    write("Warnings")
    write("----------")

    for item in dir(builtins):
        try:
            exc = eval(item)  # skipcq PYL-W0123
        except Exception:  # noqa
            continue
        try:
            if not issubclass(exc, Warning):
                continue
        except Exception:  # noqa
            continue
        make_title(item)
        console_helpers.what(item, pre=True)
