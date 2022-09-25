"""This module will expand later."""
import sys
import warnings
from importlib import import_module
from typing import List, Type

import executing

from .config import session
from .ft_gettext import current_lang, internal_error
from .info_generic import get_generic_explanation
from .path_info import path_utils
from .typing_info import _E, CauseInfo, Parser

_ = current_lang.translate
_warnings_seen = {}

_run_with_pytest = False
if "pytest" in sys.modules:
    _run_with_pytest = True


class WarningInfo:
    def __init__(self, info):
        self.info = info


def saw_warning_before(category, message, filename, lineno):
    """Records a warning if it has not been seen at the exact location
    and returns True; returns False otherwise.
    """
    # Note: unlike show_warning whose API is dictated by Python,
    # we order the argument in some grouping that seems more logical
    # for the recorded structure
    if category in _warnings_seen:
        if message in _warnings_seen[category]:
            if filename in _warnings_seen[category][message]:
                if lineno in _warnings_seen[category][message][filename]:
                    return True
                _warnings_seen[category][message][filename].append(lineno)
            else:
                _warnings_seen[category][message][filename] = [lineno]
        else:
            _warnings_seen[category][message] = {}
            _warnings_seen[category][message][filename] = [lineno]
    else:
        _warnings_seen[category] = {}
        _warnings_seen[category][message] = {}
        _warnings_seen[category][message][filename] = [lineno]
    return False


def show_warning(message, category, filename, lineno, file=None, line=None):
    if saw_warning_before(category.__name__, str(message), filename, lineno):
        # Avoid showing the same warning if it occurs in a loop, or in
        # other way in which a given instruction that give rise to a warning
        # is repeated
        return
    message = str(message)
    info = {}
    info["message"] = f"{category.__name__}: {message}\n"
    info["generic"] = get_generic_explanation(category)
    short_filename = path_utils.shorten_path(filename)
    if "[" in short_filename:
        location = _("Code block {filename}, line {line}").format(
            filename=short_filename, line=lineno
        )
    else:
        location = _("File {filename}, line {line}").format(
            filename=short_filename, line=lineno
        )
    info["last_call_header"] = f"{category.__name__}: " + location
    info["detailed_tb"] = info["last_call_source"] = get_source(filename, lineno)
    info.update(**get_warning_cause(category, message))
    warning_info = WarningInfo(info)
    if not _run_with_pytest:
        session.recorded_tracebacks.append(warning_info)
    elif "cause" in info:
        # We know how to explain this; we do not print while running tests
        return
    session.write_err(f"`{category.__name__}`: {message}\n")


def get_source(filename: str, lineno: int):
    new_lines = []
    try:
        source = executing.Source.for_filename(filename)
        statement = source.statements_at_line(lineno).pop()
        lines = source.lines[statement.lineno - 1 : statement.end_lineno]
        for number, line in enumerate(lines, start=statement.lineno):
            if number == lineno:
                new_lines.append(f"    -->{number}| {line}")
            else:
                new_lines.append(f"       {number}| {line}")
        return "\n".join(new_lines)
    except Exception:
        return _("        <'source unavailable'>")


warnings.showwarning = show_warning

INCLUDED_PARSERS = {
    SyntaxWarning: "syntax_warning",
}
WARNING_MESSAGE_PARSERS = {}


class WarningMessageParser:
    """This class is used to create objects that collect message parsers."""

    def __init__(self) -> None:
        self.parsers: List[Parser] = []
        self.core_parsers: List[Parser] = []
        self.custom_parsers: List[Parser] = []

    def _add(self, func: Parser) -> None:
        """This method is meant to be used only within friendly-traceback.
        It is used as a decorator to add a message parser to a list that is
        automatically updated.
        """
        self.parsers.append(func)
        self.core_parsers.append(func)

    def add(self, func: Parser) -> None:
        """This method is meant to be used by projects that extend
        friendly-traceback. It is used as a decorator to add a message parser
        to a list that is automatically updated.

            @instance.add
            def some_message_parser(message, traceback_data):
                ....
        """
        self.custom_parsers.append(func)
        self.parsers = self.custom_parsers + self.core_parsers


def get_warning_parser(warning_type: Type[_E]) -> WarningMessageParser:
    if warning_type not in WARNING_MESSAGE_PARSERS:
        WARNING_MESSAGE_PARSERS[warning_type] = WarningMessageParser()
        if warning_type in INCLUDED_PARSERS:
            base_path = "friendly_traceback.warning_parsers."
            import_module(base_path + INCLUDED_PARSERS[warning_type])
    return WARNING_MESSAGE_PARSERS[warning_type]


def get_warning_cause(
    warning_type,
    message: str,
) -> CauseInfo:
    """Attempts to get the likely cause of an exception."""
    try:
        return get_cause(warning_type, message)
    except Exception as e:  # noqa # pragma: no cover
        session.write_err("Exception raised")
        session.write_err(str(e))
        session.write_err(internal_error(e))
        return {}


def get_cause(
    warning_type,
    message: str,
) -> CauseInfo:
    """For a given exception type, cycle through the known message parsers,
    looking for one that can find a cause of the exception."""
    message_parser = get_warning_parser(warning_type)

    for parser in message_parser.parsers:
        # This could be simpler if we could use the walrus operator
        cause = parser(message)
        if cause:
            return cause
    return {}
