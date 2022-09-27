"""This module will expand later."""
import inspect
import sys
import warnings
from importlib import import_module
from typing import List, Type

import executing
from stack_data import BlankLines, Formatter, Options

from .config import session
from .frame_info import FriendlyFormatter
from .ft_gettext import current_lang, internal_error
from .info_generic import get_generic_explanation
from .info_variables import get_var_info
from .path_info import path_utils
from .typing_info import _E, CauseInfo, Parser

_ = current_lang.translate
_warnings_seen = {}

_run_with_pytest = False
if "pytest" in sys.modules:
    _run_with_pytest = True


class MyFormatter(Formatter):
    def format_frame(self, frame):
        yield from super().format_frame(frame)


class WarningInfo:
    def __init__(self, message, category, filename, lineno, frame=None, lines=None):
        self.message = str(message)
        self.category = category
        self.filename = filename
        self.lineno = lineno
        self.begin_lineno = lineno
        self.frame = frame
        self.info = {}
        self.info["warning message"] = f"{category.__name__}: {message}\n"
        self.info["message"] = self.info["warning message"]

        if frame is not None:
            source = self.format_source()
            self.info["warning source"] = source
            self.problem_line = executing.Source.executing(frame).text()
            var_info = get_var_info(self.problem_line, frame)
            self.info["warning variables"] = var_info["var_info"]
            if "additional variable warning" in var_info:
                self.info["additional variable warning"] = var_info[
                    "additional variable warning"
                ]
        else:
            self.problem_line = "".join(lines if lines is not None else [])
        self.recompile_info()

    def recompile_info(self):
        self.info["lang"] = session.lang
        self.info["generic"] = get_generic_explanation(self.category)
        short_filename = path_utils.shorten_path(self.filename)
        if "[" in short_filename:
            location = _(
                "Warning issued on line `{line}` of code block {filename}."
            ).format(filename=short_filename, line=self.lineno)
        else:
            location = _(
                "Warning issued on line `{line}` of file '{filename}'."
            ).format(filename=short_filename, line=self.lineno)
        self.info["warning location header"] = location

        self.info.update(**get_warning_cause(self.category, self.message))

    def format_source(self):
        nb_digits = len(str(self.lineno))
        lineno_fmt_string = "{:%d}| " % nb_digits  # noqa
        line_gap_string = " " * nb_digits + "(...)"
        line_number_gap_string = " " * (nb_digits - 1) + ":"

        formatter = FriendlyFormatter(
            options=Options(blank_lines=BlankLines.SINGLE, before=2),
            line_number_format_string=lineno_fmt_string,
            line_gap_string=line_gap_string,
            line_number_gap_string=line_number_gap_string,
        )
        formatted = formatter.format_frame(self.frame)
        return "".join(list(formatted)[1:])


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
    if filename == "<>":  # internal to IPython
        return
    if saw_warning_before(category.__name__, str(message), filename, lineno):
        # Avoid showing the same warning if it occurs in a loop, or in
        # other way in which a given instruction that give rise to a warning
        # is repeated
        return

    for outer_frame in inspect.getouterframes(inspect.currentframe()):
        if outer_frame.filename == filename and outer_frame.lineno == lineno:
            warning_info = WarningInfo(
                message,
                category,
                filename,
                lineno,
                frame=outer_frame.frame,
                lines=outer_frame.code_context,
            )
            break
    else:
        warning_info = WarningInfo(message, category, filename, lineno)

    message = str(message)

    if not _run_with_pytest:
        session.recorded_tracebacks.append(warning_info)
    elif "cause" in warning_info.info:
        # We know how to explain this; we do not print while running tests
        return
    session.write_err(f"`{category.__name__}`: {message}\n")


def enable_warnings():
    warnings.simplefilter("always")
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
