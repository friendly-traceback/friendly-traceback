"""config.py

Keep tabs of all settings.
"""
import sys
import types
from typing import List, Optional, Type, Union

from . import base_formatters, core, debug_helper
from .ft_gettext import current_lang
from .typing_info import _E, Formatter, InclusionChoice, Info, Writer

_ = current_lang.translate


def _write_err(text: Optional[str]) -> None:  # pragma: no cover
    """Default writer"""
    if text is None:
        return
    if not text.strip():
        return
    if not text.endswith("\n"):
        text += "\n"
    sys.stderr.write(text)


class _State:
    """Keeping track of various parameters in a single object meant
    to be instantiated only once.
    """

    def __init__(self) -> None:
        self._captured: List[str] = []
        self.write_err: Writer = _write_err
        self.installed: bool = False
        self.formatter: Formatter = base_formatters.repl
        self.recorded_tracebacks: List[core.FriendlyTraceback] = []
        self.include: InclusionChoice = "explain"
        self.lang: str = "en"
        self.install_gettext(self.lang)
        self.suggest_console: str = "\n" + _(
            "Are you using a regular Python console instead of a Friendly console?\n"
            "If so, to continue, try: `start_console(local_vars=locals())`.\n"
            "You will need to import `start_console` if you have not already done so.\n"
        )
        # Console; if ipython_prompt == True, prompt = '[digit]: '; False: '>>> '
        self.ipython_prompt: bool = True  # default iPython style prompt
        self.exception_before_import: bool = False
        self.sys_last_type = None
        self.sys_last_value = None

        # The following are not used by friendly-traceback but might be
        # used by friendly. We include them here as documentation.
        self.use_rich: bool = False
        self.rich_add_vspace: bool = True
        self.rich_width: Union[int, None] = None
        self.rich_tb_width: Union[int, None] = None
        self.is_jupyter: bool = False
        self.jupyter_button_style: str = ""

        self.old_excepthook = None
        # Include chain exception info in shortened/friendly traceback
        # this should be disabled by Friendly itself.
        self.include_chained_exception = True

    def show_traceback_info_again(self, index: int = -1) -> None:
        """If has not been cleared, write the traceback info again, using
        the default stream.

        This is intended to be used when a user changes the verbosity
        level and wishes to see a traceback reexplained without having
        to execute the code again.
        """
        if not self.recorded_tracebacks:
            print(_("Nothing to show: no exception recorded."))
            return
        try:
            info = self.recorded_tracebacks[index].info
        except IndexError:
            print(_("Invalid index value."))
            return
        if info["lang"] != self.lang:
            self.recorded_tracebacks[index].recompile_info()
            info = self.recorded_tracebacks[index].info

        explanation = self.formatter(info, include=self.include)
        self.write_err(explanation)
        # Do not combine with above as 'explanation' could be a list for IDLE
        self.write_err("\n")

    def capture(self, txt: str) -> None:
        """Captures the output instead of writing to stderr."""
        self._captured.append(txt)

    def get_captured(self, flush: bool = True) -> str:
        """Returns the result of captured output as a string"""
        result = "".join(self._captured)
        if flush:
            self._captured.clear()
        return result

    def set_lang(self, lang: str) -> None:
        """Sets the language and, if it is not the current language
        and a traceback exists, the information is recompiled for the
        new target language.
        """
        if lang == self.lang:
            return
        current_lang.install(lang)
        self.lang = lang

    def install_gettext(self, lang: str) -> None:
        """Sets the current language for gettext."""
        current_lang.install(lang)
        self.lang = lang

    def set_include(self, include: InclusionChoice) -> None:
        if include not in base_formatters.items_groups:  # pragma: no cover
            raise ValueError(f"{include} is not a valid value.")
        self.include = include

    def get_include(self) -> InclusionChoice:
        return self.include

    def set_formatter(self, formatter: Union[str, None, Formatter] = None) -> None:
        """Sets the default formatter. If no argument is given, the default
        formatter is used.
        """
        if formatter is None or formatter == "repl":
            self.formatter = base_formatters.repl
        elif formatter == "docs":  # pragma: no cover
            self.formatter = base_formatters.docs
        elif isinstance(formatter, str):  # pragma: no cover
            self.write_err(f"Unknown formatter: {formatter}\n")
            self.formatter = base_formatters.repl
        else:
            self.formatter = formatter  # could be provided as a function

    def install(
        self,
        lang: Optional[str] = None,
        redirect: Union[str, Writer, None] = None,
        include: InclusionChoice = None,
    ) -> None:
        """Replaces sys.excepthook by friendly's own version."""

        if lang is not None:
            self.install_gettext(lang)
        if redirect is not None:
            self.set_redirect(redirect=redirect)
        if include is not None:
            self.set_include(include)
        if self.installed:
            return

        self.old_excepthook = sys.excepthook
        sys.excepthook = self.exception_hook
        self.installed = True

    def uninstall(self) -> None:
        """Resets sys.excepthook to the excepthook used before installing friendly-traceback."""
        if not self.installed:
            return
        sys.excepthook = self.old_excepthook
        self.installed = False

    def set_redirect(self, redirect: Union[str, Writer, None] = None) -> None:
        """Sets where the output is redirected."""
        if redirect == "capture":
            self.write_err = self.capture
        elif redirect is not None:
            self.write_err = redirect
        else:
            self.write_err = _write_err

    def explain_traceback(self, redirect: Union[str, Writer, None] = None) -> None:
        """Replaces a standard traceback by a friendlier one, giving more
        information about a given exception than a standard traceback.
        Note that this excludes SystemExit and KeyboardInterrupt which
        are re-raised.

        By default, the output goes to sys.stderr or to some other stream
        set to be the default by another API call.  However, if
           redirect = some_stream
        is specified, the output goes to that stream, but without changing
        the global settings.
        """
        etype, value, tb = sys.exc_info()
        if etype is None:
            if not self.exception_before_import:
                print(_("Nothing to show: no exception recorded."))
                return
            if not (
                self.sys_last_type == sys.last_type
                and self.sys_last_value == sys.last_value
            ):
                session.get_traceback_info(
                    sys.last_type, sys.last_value, sys.last_traceback
                )
                self.sys_last_type = sys.last_type
                self.sys_last_value = sys.last_value
            info = self.recorded_tracebacks[-1].info
            self.output_info(info)
            return

        self.exception_before_import = False
        self.exception_hook(etype, value, tb, redirect=redirect)

    def exception_hook(
        self,
        etype: Type[_E],
        value: _E,
        tb: types.TracebackType,
        redirect: Union[str, Writer, None] = None,
    ) -> None:
        """Replaces a standard traceback by a friendlier one,
        except for SystemExit and KeyboardInterrupt which
        are re-raised.

        The values of the required arguments are typically the following:

            etype, value, tb = sys.exc_info()

        By default, the output goes to sys.stderr or to some other stream
        set to be the default by another API call.  However, if
           redirect = some_stream
        is specified, the output goes to that stream for this call,
        but the session settings is restored afterwards.
        """

        if etype.__name__ == "SystemExit":  # pragma: no cover
            raise SystemExit(str(value))
        if etype.__name__ == "KeyboardInterrupt":  # pragma: no cover
            raise KeyboardInterrupt(str(value))

        info = self.get_traceback_info(etype, value, tb)
        if not info:
            return
        self.output_info(info, redirect=redirect)

    def output_info(
        self, info: dict, redirect: Union[str, Writer, None] = None
    ) -> None:
        """Outputs the information obtained from a traceback.

        By default, the output goes to sys.stderr or to some other stream
        set to be the default by another API call.  However, if
           redirect = some_stream
        is specified, the output goes to that stream for this call,
        but the session settings is restored afterwards.
        """
        saved_current_redirect = None
        if redirect is not None:
            saved_current_redirect = self.write_err
            self.set_redirect(redirect=redirect)

        explanation = self.formatter(info, include=self.include)
        self.write_err(explanation)

        # Ensures that we start on a new line; essential for the console
        if hasattr(explanation, "endswith") and not explanation.endswith("\n"):
            self.write_err("\n")

        if saved_current_redirect is not None:
            self.set_redirect(redirect=saved_current_redirect)

    def get_traceback_info(
        self,
        etype: Type[_E],
        value: _E,
        tb: types.TracebackType,
    ) -> Info:
        """Obtains the information available after a traceback has been raised.

        The values of the required arguments are typically the following:

            etype, value, tb = sys.exc_info()

        Returns a dict containing the available info.
        """
        try:
            self.recorded_tracebacks.append(core.FriendlyTraceback(etype, value, tb))
            self.recorded_tracebacks[-1].compile_info()
            info = self.recorded_tracebacks[-1].info
        except Exception:  # pragma: no cover
            if not debug_helper.DEBUG:
                print(
                    "Exception raised by friendly-traceback. Please report this case."
                )
                return {}
            debug_helper.log("Exception raised in get_traceback_info().")
            raise
        return info


session = _State()
# It might sometimes be useful to import Friendly-traceback after an
# exception occurred.


def did_exception_occur_before() -> bool:
    """If an exception occurred before friendly-traceback was imported, it captures
    the information and prints an informative message to the user.

    Returns True if such information was captures, False otherwise.
    """
    # Note that if an exception occurred while friendly-traceback was imported,
    # this will not capture the information.
    # For example, suppose we try to do:
    #
    #    from friendly.python import *
    #
    # This will generate a traceback with no information being captured.
    # By calling did_exception_occur_before(), we might be able to see if an exception
    # had been raised and that there is some information available.
    def _exception_occurred():
        return _(
            "An exception occurred before friendly-traceback was imported.\n"
            "Some information is available."
        )

    if (
        hasattr(sys, "last_type")
        and hasattr(sys, "last_type")
        and hasattr(sys, "last_traceback")
    ):
        _info = session.get_traceback_info(
            sys.last_type, sys.last_value, sys.last_traceback
        )
        if _info:
            session.sys_last_type = sys.last_type
            session.sys_last_value = sys.last_value
            if not session.exception_before_import:
                print(_exception_occurred())
            session.exception_before_import = True
            return True
    return False
