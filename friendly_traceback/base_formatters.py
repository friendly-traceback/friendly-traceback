"""
base_formatters.py
===================

Default formatters showing all or only part of the available information.

A formatter is a function that takes two arguments:

1. a dict (named ``info`` everywhere in friendly files) containing
   all the information that can be shown to the user, as well as some
   entries that are meant to be used only internally as the full
   friendly information is obtained.

2. A second argument which is meant to convey what information should be shown.
   This second argument used to be a single integer ("verbosity level").
   It is currently recently being replaced by a single string. However,
   this might change as we experiment with various options prior to
   version 1.0

A formatter returns a single string. By default, this string will be
written to stderr; however this can be changed by the calling program.

This module currently contains 2 formatters:

* ``repl()``: This is used to print the information in a traditional console.
  The indentation of the traceback itself is chosen
  to reproduce that of a normal Python traceback.

* ``docs()``: this produces output with leading spaces so that it can be
  embedded as a code-block in a file (such as .rst). It can also be used
  to print the information in a traditional console.
"""
from typing import Dict, List, Set

from . import debug_helper
from .ft_gettext import current_lang
from .typing_info import InclusionChoice, Info

_ = current_lang.translate
# The following is the order in which the various items, if they exist
# and have been selected to be printed, would be printed.
# If you are writing a custom formatter, this should be taken as the
# authoritative list of items to consider.
items_in_order = [
    "header",  # Currently unused by this project; used by HackInScience
    "message",  # The last line of a Python traceback
    "original_python_traceback",  # <-- Friendly._debug_tb()
    "simulated_python_traceback",  # <-- python_tb()
    "shortened_traceback",  # <-- friendly_tb()
    "exception_notes_intro",  # New for Python 3.11
    "exception_notes",  # New in Python 3.11
    "suggest",  # <-- hint()
    "warning_message",
    "generic",  # <-- what()
    "parsing_error",
    "parsing_error_source",
    "cause",  # <-- why()
    "last_call_header",
    "last_call_source",
    "last_call_variables",
    "exception_raised_header",
    "exception_raised_source",
    "exception_raised_variables",
    "warning_location_header",
    "warning_source",
    "warning_variables",
    "additional_variable_warning",
]


repl_indentation = {
    "header": "single",  # no longer shown; keep for reference
    "message": "single",
    "simulated_python_traceback": "none",
    "original_python_traceback": "none",
    "shortened_traceback": "none",
    "exception_notes_intro": "none",
    "exception_notes": "none",
    "suggest": "double",
    "warning_message": "single",
    "generic": "single",
    "parsing_error": "single",
    "parsing_error_source": "none",
    "cause": "single",
    "last_call_header": "single",
    "last_call_source": "none",
    "last_call_variables": "double",
    "exception_raised_header": "single",
    "exception_raised_source": "none",
    "exception_raised_variables": "double",
    "warning_location_header": "single",
    "warning_source": "none",
    "warning_variables": "double",
    "additional_variable_warning": "single",
}


def repl(info: Info, include: InclusionChoice = "friendly_tb") -> str:
    """Default formatter, primarily for console usage.

    The only change made to the content of "info" is
    some added indentation.
    """
    if include == "message":
        return info["message"]
    if include == "detailed_tb":
        return detailed_tb(info) if "detailed_tb" in info else ""
    items_to_show = select_items(include)
    spacing = {"single": " " * 4, "double": " " * 8, "none": ""}
    result = [""]
    for item in items_to_show:
        if item in info:
            indentation = spacing[repl_indentation[item]]
            if item == "exception_notes":
                lines = []
                for note in info[item]:
                    note_lines = note.split("\n")
                    if "exception_notes_intro" in items_to_show:
                        for index, line in enumerate(note_lines):
                            if index == 0:
                                note_lines[0] = f"* {note_lines[0]}"
                            else:
                                note_lines[index] = f"  {note_lines[index]}"
                    lines.extend(note_lines)
                lines.append("\n")
            else:
                lines = info[item].split("\n")
            result.extend(indentation + line for line in lines)
    if result == [""] or not result:
        return no_result(info, include)

    return "\n".join(result)


def detailed_tb(info: Info) -> str:  # Special case
    """Unlike the normal information from 'where()', which focus on at
    most two frames, detailed_tb() gives information for all the frames.
    It is used mostly in IPython based environment - especially with
    the 'button-based' mode in Jupyter notebooks/lab."""
    if "detailed_tb" not in info:
        return ""
    result = [""]
    spacing = {"location": " " * 4, "var_info": " " * 8}
    for location, source, var_info in info["detailed_tb"]:
        result.append(spacing["location"] + location)
        result.extend(iter(source.split("\n")))
        result.extend(spacing["var_info"] + line for line in var_info.split("\n"))
    return "\n".join(result)


def docs(
    info: Info, include: InclusionChoice = "friendly_tb"
) -> str:  # pragma: no cover
    """Formatter that produces an output that is suitable for
    insertion in a RestructuredText (.rst) code block,
    with pre-formatted indentation.

    The only change made to the content of "info" is
    some added indentation.
    """
    # We first define the indentation to appear before each item
    pre_items = dict(**repl_indentation)

    pre_items.update(
        **{
            "simulated_python_traceback": "single",
            "original_python_traceback": "single",
            "shortened_traceback": "single",
            "exception_notes_intro": "single",
            "exception_notes": "single",
        }
    )
    if include == "message":
        return info["message"]
    if include == "detailed_tb":
        return detailed_tb(info) if "detailed_tb" in info else ""
    items_to_show = select_items(include)
    spacing = {"single": " " * 4, "double": " " * 8, "none": ""}
    result = [""]
    for item in items_to_show:
        if item in info and info[item].strip():
            indentation = spacing[pre_items[item]]
            result.extend(indentation + line for line in info[item].split("\n"))
    return no_result(info, include) if result == [""] else "\n".join(result)


def no_result(info: Info, include: InclusionChoice) -> str:
    """Should normally only be called if no result is available
    from either hint() or why().
    """
    if include == "why":
        return _("I have no suggestion to offer.")

    if include == "hint":
        if "cause" in info:
            return _("I have no suggestion to offer; try `why()`.")

        return _("I have no suggestion to offer.")

    debug_helper.log(
        f"Internal error: include = {include} in base_formatters.no_result()"
    )  # pragma: no cover
    return ""


items_groups: Dict[InclusionChoice, Set[str]] = {
    "message": {"message"},  # Also included as last line of traceback
    "message_plus": {"message", "suggest"},  # for SyntaxError in IDLE
    "hint": {"suggest"},
    "what": {"generic"},
    "why": {"warnings", "cause"},
    "where": {
        "parsing_error",
        "parsing_error_source",
        "last_call_header",
        "last_call_source",
        "last_call_variables",
        "exception_raised_header",
        "exception_raised_source",
        "exception_raised_variables",
        "warning_location_header",
        "warning_source",
        "warning_variables",
        "additional_variable_warning",
    },
    "friendly_tb": {
        "shortened_traceback",
        "suggest",
        "warnings",
        "warning_message",
        "exception_notes_intro",
        "exception_notes",
    },
    "python_tb": {"simulated_python_traceback", "exception_notes"},
    "debug_tb": {"original_python_traceback", "exception_notes"},
    "detailed_tb": {"detailed_tb"},
}
items_groups["explain"] = (
    items_groups["friendly_tb"]
    .union(items_groups["what"])
    .union(items_groups["why"])
    .union(items_groups["where"])
)

items_groups["no_tb"] = set(items_groups["explain"])  # used in check_syntax()
for item_ in items_groups["friendly_tb"]:
    items_groups["no_tb"].discard(item_)


def select_items(group_name: InclusionChoice) -> List[str]:
    items = items_groups[group_name]
    return [item for item in items_in_order if item in items]
