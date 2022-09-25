"""
console_helpers.py
------------------

Functions that can be used in a friendly console or in other interactive
environments such as in a Jupyter notebook.
"""
# NOTE: __all__ is defined at the very bottom of this file
import inspect
import sys
import types
from typing import Any, Callable, Dict, List, Optional, Type, Union

import friendly_traceback
from friendly_traceback import __version__, base_formatters, debug_helper
from friendly_traceback.config import session
from friendly_traceback.ft_gettext import current_lang
from friendly_traceback.functions_help import add_help_attribute
from friendly_traceback.info_generic import get_generic_explanation
from friendly_traceback.path_info import show_paths
from friendly_traceback.syntax_errors.source_info import Statement
from friendly_traceback.tb_data import TracebackData
from friendly_traceback.typing_info import InclusionChoice, Site

_ = current_lang.translate


def _nothing_to_show():
    return _("Nothing to show: no exception recorded.")


def back() -> None:
    """Removes the last recorded traceback item.

    The intention is to allow recovering from a typo when trying interactively
    to find out specific information about a given exception.
    """
    if not session.recorded_tracebacks:
        session.write_err(_("Nothing to go back to: no exception recorded.") + "\n")
        return
    session.recorded_tracebacks.pop()
    if session.recorded_tracebacks:
        info = session.recorded_tracebacks[-1].info
        if info["lang"] != friendly_traceback.get_lang():
            info["lang"] = friendly_traceback.get_lang()
            session.recorded_tracebacks[-1].recompile_info()


def disable():
    """Disable friendly-traceback exception hook"""
    if not session.installed:
        print(_("Friendly-traceback is already disabled."))
        return
    session.uninstall()


def enable():
    """Enable friendly-traceback exception hook"""
    if session.installed:
        print(_("Friendly-traceback is already enabled."))
        return
    session.install()


def explain(index: int = -1, include: InclusionChoice = "explain") -> None:
    """Shows the previously recorded traceback info again,
    with the option to specify different items to include.
    For example, ``explain("why")`` is equivalent to ``why()``.
    """
    old_include = friendly_traceback.get_include()
    friendly_traceback.set_include(include)
    session.show_traceback_info_again(index)
    friendly_traceback.set_include(old_include)


def friendly_tb(index: int = -1) -> None:
    """Shows the simplified Python traceback,
    which includes the hint/suggestion if available.
    """
    explain(index, include="friendly_tb")


def hint(index: int = -1) -> None:
    """Shows hint/suggestion if available."""
    explain(index, include="hint")


def history() -> None:
    """Prints the list of error messages recorded so far."""
    if not session.recorded_tracebacks:
        session.write_err(_nothing_to_show() + "\n")
        return
    items = []
    for index, tb in enumerate(session.recorded_tracebacks):
        message = session.formatter(tb.info, include="message")
        if message:
            items.append(f"{index+1}. {message}")
    if items:
        session.write_err("".join(items))


def python_tb(index: int = -1) -> None:
    """Shows the Python traceback, excluding files from friendly
    itself.
    """
    explain(index, include="python_tb")


def toggle_prompt() -> None:
    """Toggles the style of prompt to use in the console."""
    session.ipython_prompt = not session.ipython_prompt


def what(
    exception_or_index: Union[
        Type[BaseException], str, bytes, types.CodeType, int, None
    ] = None,
    pre: bool = False,
) -> None:
    """If known, shows the generic explanation about a given exception.

    If the ``pre`` argument is set to ``True``, the output is
    formatted in a way that is suitable for inclusion in the
    documentation.
    """
    if exception_or_index is None:
        explain(index=-1, include="what")
        return
    elif isinstance(exception_or_index, int):
        explain(index=exception_or_index, include="what")
        return

    if inspect.isclass(exception_or_index) and issubclass(
        exception_or_index, BaseException
    ):
        result = get_generic_explanation(exception_or_index)
    else:
        try:
            exc = eval(exception_or_index)  # skipcq PYL-W0123
            if inspect.isclass(exc) and issubclass(exc, BaseException):
                result = get_generic_explanation(exc)
            else:
                result = _("{exception} is not an exception.").format(
                    exception=exception_or_index
                )
        except Exception:  # noqa
            result = _("{exception} is not an exception.").format(
                exception=exception_or_index
            )

    if pre:  # for documentation # pragma: no cover
        lines = result.split("\n")
        for line in lines:
            session.write_err(f"    {line}\n")
        session.write_err("\n")
    else:
        session.write_err(result)


def where(index: int = -1, more=False) -> None:
    """Shows the information about where the exception occurred"""
    if more:
        explain(index, "detailed_tb")
    else:
        explain(index, "where")


def why(index: int = -1) -> None:
    """Shows the likely cause of the exception."""
    # If no cause is found, and the exception name is not accompanied by a
    # message, as in "StopIteration:", we use the same info for
    # the cause as we used for the generic information as per issue #66
    try:
        if index == -1:
            info = session.recorded_tracebacks[-1].info
        else:
            info = session.recorded_tracebacks[index + 1].info
    except IndexError:
        info = {}
    if (
        ("cause" not in info or not info["cause"])
        and "message" in info
        and len(info["message"].split(":")) > 1
        and not info["message"].split(":")[1].strip()  # empty message
    ):
        explain(index, "what")
    else:
        explain(index, "why")


def www(site: Optional[Site] = None) -> None:  # pragma: no cover
    """This uses the ``webbrowser`` module to open a tab (or window)
     in the default browser, linking to a specific url
     or opening the default email client.

    * If the argument 'site' is not specified,
      and an exception has been raised,
      an internet search will be done using
      the exception message as the search string.

    * If the argument 'site' is not specified,
      and NO exception has been raised,
      Friendly's documentation will open.

    * If the argument 'site' == "friendly",
      Friendly's documentation will open.

    * If the argument 'site' == "python", Python's documentation site
      will open with the currently used Python version.

    * If the argument 'site' == "bug",
      the Issues page for Friendly on Github will open.

    * If the argument 'site' == "email",
      the default email client should open with Friendly's
      developer's address already filled in.

    * If the argument 'site' == "warnings", a specific issue
      on Github will be shown, inviting comments.
    """
    import urllib.parse
    import webbrowser

    urls: Dict[Site, str] = {
        "friendly": "https://friendly-traceback.github.io/docs/index.html",
        "python": "https://docs.python.org/3",
        "bug": "https://github.com/friendly-traceback/friendly-traceback/issues/new",
        "email": "mailto:andre.roberge@gmail.com",
        "warnings": "https://github.com/friendly-traceback/friendly-traceback/issues/7",
    }
    try:
        site = site.casefold()
    except Exception:  # noqa
        pass
    if site not in urls and site is not None:
        session.write_err(
            _(
                "Invalid argument for `www()`.\n"
                "Valid arguments include `None` or one of `{sites}`.\n"
            ).format(sites=repr(urls.keys()))
        )
        return

    info = session.recorded_tracebacks[-1].info if session.recorded_tracebacks else {}
    if site is None and info:
        message = info["message"].replace("'", "")
        if " (" in message:
            message = message.split("(")[0]
        url = "https://duckduckgo.com?q=" + urllib.parse.quote(message)  # noqa
    elif site is None:
        url = urls["friendly"]
    else:
        url = urls[site]

    if site == "python":
        url = url + f".{sys.version_info.minor}/"

    try:
        webbrowser.open_new_tab(url)
    except Exception:  # noqa
        session.write_err(_("The default web browser cannot be used for searching."))
        return


def set_debug(flag: bool = True) -> None:  # pragma: no cover
    """This sets the value of the debug flag for the current session."""
    debug_helper.DEBUG = flag
    debug_helper.SHOW_DEBUG_HELPER = flag


get_lang = friendly_traceback.get_lang
set_lang = friendly_traceback.set_lang
get_include = friendly_traceback.get_include
set_include = friendly_traceback.set_include
set_formatter = friendly_traceback.set_formatter

# ===== Debugging functions are not unit tested by choice =====


def _debug_tb() -> None:  # pragma: no cover
    """Shows the true Python traceback, which includes
    files from friendly itself.
    """
    explain(-1, include="debug_tb")


def _get_exception() -> Optional[BaseException]:  # pragma: no cover
    """Debugging tool: returns the exception instance or None if no exception
    has been raised.
    """
    if not session.recorded_tracebacks:
        print(_nothing_to_show())
        return None  # add explicit None here and elsewhere to silence mypy
    return session.recorded_tracebacks[-1].tb_data.exception_instance


def _get_frame() -> Optional[types.FrameType]:  # pragma: no cover
    """This returns the frame in which the exception occurred.

    This is not intended for end-users but is useful in development.
    """
    if not session.recorded_tracebacks:
        print(_nothing_to_show())
        return None
    return session.recorded_tracebacks[-1].tb_data.exception_frame


def _get_statement() -> Optional[Statement]:  # pragma: no cover
    """This returns a 'Statement' instance obtained for SyntaxErrors and
    subclasses.  Such a Statement instance contains essentially all
    the known information about the statement where the error occurred.

    This is not intended for end-users but is useful in development.
    """
    if not session.recorded_tracebacks:
        print(_nothing_to_show())
        return None
    if isinstance(
        session.recorded_tracebacks[-1].tb_data.exception_instance, SyntaxError
    ):
        return session.recorded_tracebacks[-1].tb_data.statement
    print("No statement: not a SyntaxError.")
    return None


def _get_tb_data() -> Optional[TracebackData]:  # pragma: no cover
    """This returns the TracebackData instance containing all the
    information we have obtained.

    This is not intended for end-users but is useful in development.
    """
    if not session.recorded_tracebacks:
        print(_nothing_to_show())
        return None
    return session.recorded_tracebacks[-1].tb_data


def _get_info() -> list:
    """Debugging tool: returns the content of a traceback info."""
    return session.recorded_tracebacks[-1].info if session.recorded_tracebacks else []


def _show_info() -> None:  # pragma: no cover
    """Debugging tool: shows the complete content of traceback info.

    Prints ``''`` for a given item if it is not present.
    """
    info = session.recorded_tracebacks[-1].info if session.recorded_tracebacks else []

    for item in base_formatters.items_in_order:
        if item in info and info[item].strip():
            print(f"{item}:")
            for line in info[item].strip().split("\n"):
                print("   ", line)
            print()
        else:
            print(f"{item}: ''")

    for item in info:
        if item not in base_formatters.items_in_order:
            print(f"{item}: {info[item]}")


helpers: Dict[str, Callable[..., None]] = {
    "why": why,
    "what": what,
    "where": where,
    "www": www,
    "explain": explain,
    "hint": hint,
    "enable": enable,
    "disable": disable,
    "back": back,
    "history": history,
    "friendly_tb": friendly_tb,
    "python_tb": python_tb,
    "toggle_prompt": toggle_prompt,
    "show_paths": show_paths,
    "get_include": get_include,
    "set_include": set_include,
    "get_lang": get_lang,
    "set_lang": set_lang,
    "set_formatter": set_formatter,
    "set_debug": set_debug,
}
add_help_attribute(helpers)

debug_helper_methods: Dict[str, Callable[..., Any]] = {
    "_debug_tb": _debug_tb,
    "_get_frame": _get_frame,
    "_get_info": _get_info,
    "_show_info": _show_info,
    "_get_tb_data": _get_tb_data,
    "_get_exception": _get_exception,
    "_get_statement": _get_statement,
}
add_help_attribute(debug_helper_methods)


class FriendlyHelpers:
    """Helper class which can be used in a console as an alternative
    to using the helper functions directly.
    This can be helpful if one of the helper functions gets redefined.

    It is usually instantiated using the name ``Friendly``.

    For example, we can write ``Friendly.why()`` as equivalent to ``why()``.
    """

    version = __version__

    def __init__(self) -> None:
        self.helpers = {}

    def add_helper(self, function: Callable) -> None:  # pragma: no cover
        """Adds a helper base on its name and the function it refers to."""
        self.helpers[function.__name__] = function
        setattr(self, function.__name__, function)

    def remove_helper(self, name: str) -> None:  # pragma: no cover
        """Removes a helper from the FriendlyHelpers object"""
        if name in self.helpers:
            del self.helpers[name]
            delattr(self, name)
        else:
            message = f"Cannot remove {name}; it is not a known helper."
            debug_helper.log(message)

    def __dir__(self) -> List[str]:  # pragma: no cover
        """Only include useful friendly methods."""
        return sorted(list(self.helpers))

    def __repr__(self) -> str:  # pragma: no cover
        """Shows a brief description in the default language of what
        each function/method does.

        Debugging helper functions are only included if the DEBUG flag is set.
        """
        basic_helpers = {}
        _debug_helpers = {}
        for name in self.helpers:
            if name.startswith("_"):
                _debug_helpers[name] = self.helpers[name]
            else:
                basic_helpers[name] = self.helpers[name]

        # sort alphabetically, then by length name for nicer display
        basic_helpers = sorted(list(basic_helpers))
        basic_helpers = sorted(basic_helpers, key=len)
        _debug_helpers = sorted(list(_debug_helpers))
        _debug_helpers = sorted(_debug_helpers, key=len)

        header = _(
            "The following methods of the Friendly object should also "
            "be available as functions."
        )
        parts = [self.true_repr() + "\n" + header + "\n\n"]
        for name in basic_helpers:
            parts.append(name + "(): ")
            fn = self.helpers[name]
            if hasattr(fn, "help"):
                parts.append(fn.help() + "\n")
            else:
                print("Warning:", name, "has no help() method.")

        if debug_helper.SHOW_DEBUG_HELPER:
            more_header = "Debugging methods (English only)."
            parts.append("\n" + more_header + "\n\n")
            for name in _debug_helpers:
                parts.append(name + "(): ")
                fn = self.helpers[name]
                if hasattr(fn, "help"):
                    parts.append(fn.help() + "\n")
                else:
                    print("Warning:", name, "has no help() method.")
        return "".join(parts)

    def true_repr(self) -> str:  # pragma: no cover
        """Method that can be called when a normal looking repr is needed."""
        return "<class FriendlyHelpers>"


Friendly = FriendlyHelpers()
for helper_name in helpers:
    Friendly.add_helper(helpers[helper_name])
for helper_name in debug_helper_methods:
    Friendly.add_helper(debug_helper_methods[helper_name])

helpers["Friendly"] = Friendly
# We don't include the debug helpers in __all__ so that they do
# not show when doing dir() at a console; we only make them
# available as methods of the Friendly object.
__all__ = list(helpers.keys())
