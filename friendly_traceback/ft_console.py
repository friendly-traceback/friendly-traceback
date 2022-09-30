"""
ft_console.py
==========

Adaptation of Python's console found in code.py so that it can be
used to show some "friendly" tracebacks.
"""
import codeop  # need to import to exclude from tracebacks
import os
import platform
import sys
import traceback
import types
from code import InteractiveConsole
from typing import Any, Callable, Mapping, Optional, Union

import friendly_traceback

from . import source_cache
from .config import did_exception_occur_before, session
from .console_helpers import friendly_tb, helpers
from .ft_gettext import current_lang
from .typing_info import Formatter, InclusionChoice


def type_friendly() -> str:
    # Explicit type as mypy cannot infer correctly the return type on its own here
    _: Callable[[str], str] = current_lang.translate
    return _("Type 'Friendly' for help on special functions/methods.")


BANNER = "\nFriendly-traceback version {}. [Python version: {}]\n".format(
    friendly_traceback.__version__, platform.python_version()
)


_old_displayhook = sys.displayhook


def rich_displayhook(value: Any) -> None:
    """Custom display hook intended to show some brief function descriptions
    that can be translated into various languages, for functions that have
    a custom '__rich_repr__' attribute.
    Compatible with Rich (https://github.com/willmcgugan/rich)
    """
    if value is None:
        return
    if str(type(value)) == "<class 'function'>" and hasattr(value, "__rich_repr__"):
        print(f"{value.__name__}(): {value.__rich_repr__()[0]}")
        return
    _old_displayhook(value)


class FriendlyTracebackConsole(InteractiveConsole):
    def __init__(
        self,
        local_vars: Optional[Mapping[str, Any]] = None,
        formatter: Union[str, Formatter] = "repl",
        displayhook: Optional[Callable[[object], Any]] = None,
        ipython_prompt: bool = True,
    ) -> None:
        """This class builds upon Python's code.InteractiveConsole
        to provide friendly tracebacks. It keeps track
        of code fragment executed by treating each of them as
        an individual source file.
        """
        _ = current_lang.translate
        friendly_traceback.exclude_file_from_traceback(codeop.__file__)
        self.fake_filename = "<friendly-console:%d>"
        self.counter = 1
        friendly_traceback.set_formatter(formatter)
        if displayhook is not None:
            sys.displayhook = displayhook
        session.ipython_prompt = ipython_prompt
        if session.ipython_prompt:
            sys.ps1 = "[1]: "
            sys.ps2 = "...: "
        super().__init__(locals=local_vars)
        session.suggest_console = ""

    def interact(self, banner=None, exitmsg=None) -> None:
        if not session.exception_before_import:
            if did_exception_occur_before():
                print(banner)
                banner = ""
                friendly_tb()
        super().interact(banner=banner, exitmsg=exitmsg)

    def push(self, line: str) -> bool:
        """Push a line to the interpreter.

        The line should not have a trailing newline; it may have
        internal newlines.  The line is appended to a buffer and the
        interpreter's runsource() method is called with the
        concatenated contents of the buffer as source.  If this
        indicates that the command was executed or invalid, the buffer
        is reset; otherwise, the command is incomplete, and the buffer
        is left as it was after the line was appended.  The return
        value is True if more input is required, False if the line was dealt
        with in some way (this is the same as runsource()).
        """
        # mypy cannot get the type information from InteractiveConsole in stdlib
        self.buffer.append(line)  # type: ignore
        source = "\n".join(self.buffer)  # type: ignore

        # Each valid code sample is saved with its own fake filename.
        # They are numbered consecutively to help understand
        # the traceback history.
        # If self.counter was not updated, it means that the previous
        # code sample was not valid, and we reuse the same file name
        filename = self.fake_filename % self.counter
        source_cache.cache.add(filename, source)

        more = self.runsource(source, filename)
        if not more:
            self.resetbuffer()
            self.counter += 1
            if session.ipython_prompt:
                sys.ps1 = f"\n[{self.counter}]: "
                sys.ps2 = " " * (len(str(self.counter)) - 1) + "...: "
            else:
                sys.ps1 = ">>> "
                sys.ps2 = "... "
        return more

    def runsource(
        self, source: str, filename: str = "<friendly-console>", symbol: str = "single"
    ) -> bool:
        """Compile and run some source in the interpreter.

        Arguments are as for compile_command().

        One several things can happen:

        1) The input is incorrect; compile_command() raised an
        exception (SyntaxError or OverflowError).  A syntax traceback
        will be printed .

        2) The input is incomplete, and more input is required;
        compile_command() returned None.  Nothing happens.

        3) The input is complete; compile_command() returned a code
        object.  The code is executed by calling self.runcode() (which
        also handles run-time exceptions, except for SystemExit).

        The return value is True in case 2, False in the other cases (unless
        an exception is raised).  The return value can be used to
        decide whether to use sys.ps1 or sys.ps2 to prompt the next
        line.
        """
        try:
            code = self.compile(source, filename, symbol)  # type: ignore
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            if session.installed:
                friendly_traceback.explain_traceback()
            else:
                super().showsyntaxerror(filename)
            return False

        if code is None:
            # Case 2
            return True

        # Case 3
        self.runcode(code)
        return False

    def runcode(self, code: types.CodeType) -> None:
        """Execute a code object.

        When an exception occurs, friendly_traceback.explain_traceback() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which, unlike the case for the original version in the
        standard library, cleanly exists the program. This is done
        to avoid our Friendly's exception hook to intercept it and confuse the users.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.
        """
        _ = current_lang.translate
        try:
            exec(code, self.locals)  # type: ignore
        except SystemExit:
            os._exit(1)  # noqa -pycharm
        except Exception:  # noqa
            if session.installed:
                try:
                    friendly_traceback.explain_traceback()
                except Exception:  # noqa
                    print("Friendly Internal Error")
                    print("-" * 60)
                    traceback.print_exc()
                    print("-" * 60)
            else:
                super().showtraceback()

    # The following two methods are never used in this class, but they are
    # defined in the parent class. The following are the equivalent methods
    # that can be used if an explicit call is desired for some reason.

    def showsyntaxerror(self, filename: Optional[str] = None) -> None:
        if session.installed:
            friendly_traceback.explain_traceback()
        else:
            super().showsyntaxerror(filename)

    def showtraceback(self) -> None:
        if session.installed:
            friendly_traceback.explain_traceback()
        else:
            super().showtraceback()


def start_console(
    local_vars: Optional[Mapping[str, Any]] = None,
    formatter: Union[str, Formatter] = "repl",
    include: InclusionChoice = "friendly_tb",
    lang: str = "en",
    banner: Optional[str] = None,
    displayhook: Optional[Callable[[object], Any]] = None,
    ipython_prompt: bool = True,
) -> None:
    """Starts a console; modified from code.interact"""

    friendly_traceback.about_warnings.enable_warnings()
    if banner is None:
        banner = BANNER + type_friendly() + "\n"
    if displayhook is None:
        displayhook = rich_displayhook

    friendly_traceback.install(include=include, lang=lang)

    if local_vars is not None:
        # Make sure we don't overwrite with our own functions
        helpers.update(local_vars)
        helpers["friendly_exec"] = friendly_traceback.friendly_exec

    console = FriendlyTracebackConsole(
        local_vars=helpers,
        formatter=formatter,
        displayhook=displayhook,
        ipython_prompt=ipython_prompt,
    )
    console.interact(banner=banner)
