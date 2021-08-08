"""This module is intended to add help attributes to various functions.

Note that it might be moved to friendly instead staying in this repository."""
from typing import Any, Callable, Dict

from friendly_traceback import debug_helper
from friendly_traceback.ft_gettext import current_lang

_ = current_lang.translate

short_description = {
    "back": lambda: _("Removes the last recorded traceback item."),
    "explain": lambda: _("Shows all the information about the last traceback."),
    "history": lambda: _("Shows a list of recorded traceback messages."),
    "set_lang": lambda: _("Sets the language to be used."),
    "set_prompt": lambda: _("Sets the prompt style to be used in the console."),
    "show_paths": lambda: _("Shows the paths corresponding to synonyms used."),
    "what": lambda: _("Shows the generic meaning of a given exception"),
    "where": lambda: _("Shows where an exception was raised."),
    "why": lambda: _("Shows the likely cause of the exception."),
    "www": lambda: _("Opens a web browser at a useful location."),
}


def add_help_attribute(functions: Dict[str, Callable[..., Any]]) -> None:
    """Given a dict whose content is of the form
    {function_name_string: function_obj}
    it adds customs `help` and  `__rich__repr` attributes for all such
    function objects.
    """
    for name in functions:
        if name not in short_description:
            debug_helper.log(f"Missing description for {name}.")
            continue
        func = functions[name]
        setattr(func, "help", short_description[name])  # noqa
        setattr(func, "__rich_repr__", lambda func=func: (func.help(),))  # noqa


def add_rich_repr(functions: Dict[str, Callable[..., Any]]) -> None:
    """Given a dict whose content is of the form
    {function_name_string: function_obj}
    it adds a custom __rich__repr attribute for all such
    function objects that have a help method.
    """
    for name in functions:
        func = functions[name]
        if hasattr(func, "help"):
            setattr(func, "__rich_repr__", lambda func=func: (func.help(),))  # noqa
