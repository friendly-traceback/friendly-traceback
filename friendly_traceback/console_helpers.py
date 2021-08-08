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
from typing import Any, Callable, Dict, Iterable, List, Optional, Union, Type
import friendly_traceback

from friendly_traceback import debug_helper, base_formatters, __version__
from friendly_traceback.config import session
from friendly_traceback.core import TracebackData
from friendly_traceback.info_generic import get_generic_explanation
from friendly_traceback.path_info import show_paths
from friendly_traceback.ft_gettext import current_lang
from friendly_traceback.syntax_errors.source_info import Statement
from friendly_traceback.typing import InclusionChoice, Site
from friendly_traceback.utils import add_rich_repr


_ = current_lang.translate


def back() -> None:
    """Removes the last recorded traceback item.

    The intention is to allow recovering from a typo when trying interactively
    to find out specific information about a given exception.
    """
    if not session.saved_info:
        session.write_err(_("Nothing to go back to: no exception recorded.") + "\n")
        return
    if not session.friendly_info:  # pragma: no cover
        debug_helper.log("Problem: saved info is not empty but friendly is")
    session.saved_info.pop()
    session.friendly_info.pop()
    if session.saved_info:
        info = session.saved_info[-1]
        if info["lang"] != friendly_traceback.get_lang():
            info["lang"] = friendly_traceback.get_lang()
            session.friendly_info[-1].recompile_info()


def explain(include: InclusionChoice = "explain") -> None:
    """Shows the previously recorded traceback info again,
    with the option to specify different items to include.
    For example, ``explain("why")`` is equivalent to ``why()``.
    """
    old_include = friendly_traceback.get_include()
    friendly_traceback.set_include(include)
    session.show_traceback_info_again()
    friendly_traceback.set_include(old_include)


def friendly_tb() -> None:
    """Shows the a simplified Python traceback,
    which includes the hint/suggestion if available.
    """
    explain("friendly_tb")


def hint() -> None:
    """Shows hint/suggestion if available."""
    explain("hint")


def history() -> None:
    """Prints the list of error messages recorded so far."""
    if not session.saved_info:
        session.write_err(_("Nothing to show: no exception recorded.") + "\n")
        return
    for info in session.saved_info:
        message = session.formatter(info, include="message").replace("\n", "")
        session.write_err(message)


def python_tb() -> None:
    """Shows the Python traceback, excluding files from friendly
    itself.
    """
    explain("python_tb")


def set_prompt(prompt: Optional[str] = None) -> None:
    """Sets the default prompt to use in the console.

    If the prompt argument is ">>>" or "python",
    then the standard Python prompt will be used.
    Note that the prompt argument will be stripped and is case-insensitive.

    If any other argument is given, then the iPython style prompt will be used.
    Setting this has also an effect on how the "friendly traceback" filename
    are shown for code blocks.
    """
    session.ipython_prompt = True
    if prompt is None:
        return
    try:
        prompt = prompt.strip().casefold()
        if prompt in [">>>", "python"]:
            session.ipython_prompt = False
    except Exception:  # noqa
        pass


def what(
    exception: Union[Type[BaseException], str, bytes, types.CodeType, None] = None,
    pre: bool = False,
) -> None:
    """If known, shows the generic explanation about a given exception.

    If the ``pre`` argument is set to ``True``, the output is
    formatted in a way that is suitable for inclusion in the
    documentation.
    """
    if exception is None:
        explain("what")
        return

    if inspect.isclass(exception) and issubclass(exception, BaseException):
        result = get_generic_explanation(exception)
    else:
        try:
            exc = eval(exception)
            if inspect.isclass(exc) and issubclass(exc, BaseException):
                result = get_generic_explanation(exc)
            else:
                result = _("{exception} is not an exception.").format(
                    exception=exception
                )
        except Exception:  # noqa
            result = _("{exception} is not an exception.").format(exception=exception)

    if pre:  # for documentation # pragma: no cover
        lines = result.split("\n")
        for line in lines:
            session.write_err("    " + line + "\n")
        session.write_err("\n")
    else:
        session.write_err(result)
    return


def where() -> None:
    """Shows the information about where the exception occurred"""
    explain("where")


def why() -> None:
    """Shows the likely cause of the exception."""
    explain("why")


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

    info = session.saved_info[-1] if session.saved_info else None
    if site is None and info is not None:
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
    explain("debug_tb")


def _get_exception() -> Optional[BaseException]:  # pragma: no cover
    """Debugging tool: returns the exception instance or None if no exception
    has been raised.
    """
    if not session.saved_info:
        print("Nothing to show: no exception recorded.")
        return
    info = session.saved_info[-1]
    return info["_exc_instance"]


def _get_frame() -> Optional[types.FrameType]:  # pragma: no cover
    """This returns the frame in which the exception occurred.

    This is not intended for end-users but is useful in development.
    """
    if not session.saved_info:
        print("Nothing to show: no exception recorded.")
        return
    info = session.saved_info[-1]
    return info["_frame"]


def _get_statement() -> Optional[Statement]:  # pragma: no cover
    """This returns a 'Statement' instance obtained for SyntaxErrors and
    subclasses.  Such a Statement instance contains essentially all
    the known information about the statement where the error occurred.

    This is not intended for end-users but is useful in development.
    """
    if not session.saved_info:
        print("Nothing to show: no exception recorded.")
        return
    if isinstance(session.saved_info[-1]["_exc_instance"], SyntaxError):
        return session.friendly_info[-1].tb_data.statement
    print("No statement: not a SyntaxError.")
    return


def _get_tb_data() -> Optional[TracebackData]:  # pragma: no cover
    """This returns the TracebackData instance containing all the
    information we have obtained.

    This is not intended for end-users but is useful in development.
    """
    if not session.saved_info:
        print("Nothing to show: no exception recorded.")
        return
    info = session.saved_info[-1]
    return info["_tb_data"]


def set_debug(flag: bool = True) -> None:  # pragma: no cover
    """This sets the value of the debug flag for the current session."""
    debug_helper.DEBUG = flag
    debug_helper.SHOW_DEBUG_HELPER = flag


def _show_info() -> None:  # pragma: no cover
    """Debugging tool: shows the complete content of traceback info.

    Prints ``''`` for a given item if it is not present.
    """
    info = session.saved_info[-1] if session.saved_info else []

    for item in base_formatters.items_in_order:
        if item in info and info[item].strip():
            print(f"{item}:")
            for line in info[item].strip().split("\n"):
                print("   ", line)
            print()
        else:
            print(f"{item}: ''")

    header_printed = False
    for item in info:
        if item not in base_formatters.items_in_order:
            if not header_printed:
                print("=" * 56)
                print("The following are not meant to be shown to the end user:\n")
                header_printed = True
            print(f"{item}: {info[item]}")


basic_helpers: Dict[str, Callable[..., None]] = {
    "back": back,
    "explain": explain,
    "history": history,
    "set_lang": set_lang,
    "set_prompt": set_prompt,
    "show_paths": show_paths,
    "what": what,
    "where": where,
    "why": why,
    "www": www,
}

back.help = lambda: _("Removes the last recorded traceback item.")
explain.help = lambda: _("Shows all the information about the last traceback.")
history.help = lambda: _("Shows a list of recorded traceback messages.")
set_lang.help = lambda: _("Sets the language to be used.")
set_prompt.help = lambda: _("Sets the prompt style to be used in the console.")
show_paths.help = lambda: _("Shows the paths corresponding to synonyms used.")
what.help = lambda: _("Shows the generic meaning of a given exception")
where.help = lambda: _("Shows where an exception was raised.")
why.help = lambda: _("Shows the likely cause of the exception.")
www.help = lambda: _("Opens a web browser at a useful location.")

add_rich_repr(basic_helpers)

from typing import Callable

other_helpers: Dict[str, Callable[..., Any]] = {
    "hint": hint,
    "get_lang": get_lang,
    "python_tb": python_tb,
    "friendly_tb": friendly_tb,
    "get_include": get_include,
    "set_include": set_include,
    "set_formatter": set_formatter,
    "set_debug": set_debug,
}
hint.help = lambda: _("Suggestion sometimes added to a friendly traceback.")
python_tb.help = lambda: _("Shows a normal Python traceback.")
friendly_tb.help = lambda: _("Shows a simplified Python traceback.")
get_include.help = lambda: _(
    "Returns the current value used for items to include by default."
)
set_include.help = lambda: _(
    "Sets the items to show by default when an exception is raised."
)
get_lang.help = lambda: _("Returns the language currently used.")
set_formatter.help = lambda: _("Sets the formatter to use for display.")
set_debug.help = lambda: _("Use True (default) or False to set the debug flag.")

add_rich_repr(other_helpers)

helpers = {**basic_helpers, **other_helpers}

_debug_helpers: Dict[str, Callable[..., Any]] = {
    "_debug_tb": _debug_tb,
    "_get_frame": _get_frame,
    "_show_info": _show_info,
    "_get_tb_data": _get_tb_data,
    "_get_exception": _get_exception,
    "_get_statement": _get_statement,
}

_debug_tb.help = (
    lambda: "Shows the full traceback, including code from friendly_traceback."
)
_show_info.help = lambda: "Shows the all the items recorded in the traceback."
_get_exception.help = lambda: "Returns the exception instance."
_get_frame.help = lambda: "Returns the frame object where the exception occurred."
_get_statement.help = lambda: "Returns the statement in which a SyntaxError occurred."
_get_tb_data.help = lambda: "Return a special traceback object."

add_rich_repr(_debug_helpers)


class FriendlyHelpers:
    """Helper class which can be used in a console if one of the
    helper functions gets redefined.

    For example, we can write Friendly.explain() as equivalent to explain().
    """

    version = __version__

    __include_basic: List[str]

    def __init__(self, local_helpers: Optional[Iterable[str]] = None) -> None:
        self.__include_basic = list(basic_helpers)
        if local_helpers is not None:
            self.__include_basic.extend(local_helpers)
        self.__include_basic = sorted(self.__include_basic)  # first alphabetically
        # then by word length, as it is easier to read.
        self.include_in_rich_repr = sorted(self.__include_basic, key=len)

        self.__include_more = list(other_helpers)
        self.__include_more = sorted(self.__include_more)  # first alphabetically
        # then by word length, as it is easier to read.
        self.include_in_help = sorted(self.__include_more, key=len)
        self.__class__.__name__ = "Friendly"  # For a nicer Rich repr

        debug_helpers = sorted(list(_debug_helpers))
        self.debug_helpers = sorted(debug_helpers, key=len)

    def __dir__(self) -> List[str]:  # pragma: no cover
        """Only include useful friendly methods."""
        return self.__include_basic + list(other_helpers) + list(_debug_helpers)

    def __repr__(self) -> str:  # pragma: no cover
        """Shows a brief description in the default language of what
        each 'basic' function/method does.

        'Advanced' and debugging helper functions are not included
        in the display.
        """
        header = (
            _(
                "The following methods of the Friendly object might also "
                "be available as functions."
            )
            + "\n\n"
            + _("Basic methods:")
        )
        parts = [header + "\n\n"]
        for item in self.include_in_rich_repr:
            parts.append(item + "(): ")
            fn = getattr(Friendly, item)
            if hasattr(fn, "help"):
                parts.append(getattr(Friendly, item).help() + "\n")
            else:
                print("Warning:", item, "has no help() method.")

        more_header = _("Less commonly used methods/functions.")
        parts.append("\n" + more_header + "\n\n")
        for item in self.include_in_help:
            parts.append(item + "(): ")
            fn = getattr(Friendly, item)
            if hasattr(fn, "help"):
                parts.append(getattr(Friendly, item).help() + "\n")
            else:
                print("Warning:", item, "has no help() method.")

        if debug_helper.SHOW_DEBUG_HELPER:
            more_header = "Debugging methods (English only by design)."
            parts.append("\n" + more_header + "\n\n")
            for item in self.debug_helpers:
                parts.append(f"Friendly.{item}(): ")
                fn = getattr(Friendly, item)
                if hasattr(fn, "help"):
                    parts.append(getattr(Friendly, item).help() + "\n")
                else:
                    print("Warning:", item, "has no help() method.")
        return "".join(parts)


for helper in _debug_helpers:
    setattr(FriendlyHelpers, helper, staticmethod(_debug_helpers[helper]))
for helper in helpers:
    setattr(FriendlyHelpers, helper, staticmethod(helpers[helper]))

Friendly = FriendlyHelpers()
helpers["Friendly"] = Friendly
__all__ = list(helpers.keys())
