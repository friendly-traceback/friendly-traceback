"""config.py

Keeps tabs of all settings.
"""
import sys
import types
from typing import List, Optional, Type, Union

from . import base_formatters, core, debug_helper
from .ft_gettext import current_lang
from .typing import _E, Formatter, InclusionChoice, Info, Writer

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
        self.saved_info: List[Info] = []
        self.friendly_info: List[core.FriendlyTraceback] = []
        # TODO: is having both saved_info and friendly_info redundant?
        self.include: InclusionChoice = "explain"
        self.lang: str = "en"
        self.install_gettext(self.lang)
        # Console; if ipython_prompt == True, prompt = '[digit]'
        self.ipython_prompt: bool = False  # default prompt = '>>>'

        # The following are not used by friendly-traceback but might be
        # used by friendly. We include them here as documentation.
        self.use_rich: bool = False
        self.rich_add_vspace: bool = True
        self.rich_width: Union[int, None] = None
        self.rich_tb_width: Union[int, None] = None
        self.is_jupyter: bool = False
        self.jupyter_button_style: str = ""

    def show_traceback_info_again(self) -> None:
        """If has not been cleared, write the traceback info again, using
        the default stream.

        This is intended to be used when a user changes the verbosity
        level and wishes to see a traceback reexplained without having
        to execute the code again.
        """
        if not self.saved_info:
            print(_("Nothing to show: no exception recorded."))
            return
        explanation = self.formatter(self.saved_info[-1], include=self.include)
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
        if self.saved_info:
            if not self.friendly_info:  # pragma: no cover
                debug_helper.log(
                    "Problem: saved_info includes content but friendly doesn't."
                )
            self.friendly_info[-1].recompile_info()
            self.friendly_info[-1].info["lang"] = lang

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
        include: InclusionChoice = "explain",
    ) -> None:
        """Replaces sys.excepthook by friendly's own version."""

        if lang is not None:
            self.install_gettext(lang)
        if redirect is not None:
            self.set_redirect(redirect=redirect)
        if include != self.include:
            self.set_include(include)

        sys.excepthook = self.exception_hook
        self.installed = True

    def uninstall(self) -> None:
        """Resets sys.excepthook to the Python default."""
        self.installed = False
        sys.excepthook = sys.__excepthook__

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
            print(_("Nothing to show: no exception recorded."))
            return
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

        saved_current_redirect = None
        if redirect is not None:
            saved_current_redirect = self.write_err
            self.set_redirect(redirect=redirect)

        try:
            self.friendly_info.append(core.FriendlyTraceback(etype, value, tb))
            self.friendly_info[-1].compile_info()
            info = self.friendly_info[-1].info
            info["lang"] = self.lang
            self.saved_info.append(info)
            explanation = self.formatter(info, include=self.include)
        except Exception as e:  # pragma: no cover
            debug_helper.log("Exception raised in exception_hook().")
            try:
                debug_helper.log(self.friendly_info[-1].tb_data.filename)
            except Exception:  # noqa
                pass
            debug_helper.log_error(e)
            return

        self.write_err(explanation)

        # Ensures that we start on a new line; essential for the console
        if hasattr(explanation, "endswith") and not explanation.endswith("\n"):
            self.write_err("\n")

        if saved_current_redirect is not None:
            self.set_redirect(redirect=saved_current_redirect)


session = _State()
