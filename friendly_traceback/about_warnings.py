"""This module includes all relevant classes and functions so that
friendly-traceback can give help with warnings.

It contains one function (``enable_warnings``) which is part of the API,
and one (``get_warning_parser``) which is the only other function in this module
which is intended to be part of the public API. However, while the latter
can be imported using ``from friendly_traceback import enable_warnings``,
``get_warning_parser`` needs to be imported from this module.
"""
import inspect
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
_RUNNING_TESTS = False
IGNORE_WARNINGS = set()


def enable_warnings(testing: bool = False) -> None:
    """Used to enable all warnings, with 'always' being used as the
    parameter for warnings.simplefilter.

    While friendly_traceback, used by many third-party packages, does not
    automatically handle warnings by default, friendly, which is meant to
    be used by end-users instead of other packages/libraries, does call
    enable_warnings by default.
    """
    # Note: enable_warnings is imported by friendly_traceback.__init__
    # so that it is part of the public API.
    global _RUNNING_TESTS
    _RUNNING_TESTS = testing
    warnings.simplefilter("always")
    warnings.showwarning = show_warning


class MyFormatter(Formatter):
    def format_frame(self, frame):
        yield from super().format_frame(frame)


class WarningInfo:
    def __init__(
        self, warning_instance, warning_type, filename, lineno, frame=None, lines=None
    ):
        self.warning_instance = warning_instance
        self.message = str(warning_instance)
        self.warning_type = warning_type
        self.filename = filename
        self.lineno = lineno
        self.begin_lineno = lineno
        self.lines = lines
        self.frame = frame
        self.info = {"warning_message": f"{warning_type.__name__}: {self.message}\n"}
        self.info["message"] = self.info["warning_message"]

        if frame is not None:
            source = self.format_source()
            self.info["warning_source"] = source
            self.problem_statement = executing.Source.executing(frame).text()
            var_info = get_var_info(self.problem_statement, frame)
            self.info["warning_variables"] = var_info["var_info"]
            if "additional_variable_warning" in var_info:
                self.info["additional_variable_warning"] = var_info[
                    "additional_variable_warning"
                ]
        else:
            self.info["warning_source"] = self.get_source_frame_missing()
        self.recompile_info()

    def recompile_info(self):
        self.info["lang"] = session.lang
        self.info["generic"] = get_generic_explanation(self.warning_type)
        short_filename = path_utils.shorten_path(self.filename)
        if "[" in short_filename:
            location = _(
                "Warning issued on line `{line}` of code block {filename}."
            ).format(filename=short_filename, line=self.lineno)
        else:
            location = _(
                "Warning issued on line `{line}` of file '{filename}'."
            ).format(filename=short_filename, line=self.lineno)
        self.info["warning_location_header"] = location + "\n"

        self.info.update(**get_warning_cause(self.warning_type, self.message, self))

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

    def get_source_frame_missing(self):
        new_lines = []
        try:
            source = executing.Source.for_filename(self.filename)
            statement = source.statements_at_line(self.lineno).pop()
            lines = source.lines[statement.lineno - 1 : statement.end_lineno]
            for number, line in enumerate(lines, start=statement.lineno):
                if number == self.lineno:
                    new_lines.append(f"    -->{number}| {line}")
                else:
                    new_lines.append(f"       {number}| {line}")
            self.problem_statement = "".join(lines)
            return "\n".join(new_lines)
        except Exception:
            self.problem_statement = None
            # self.lines comes from Python; it should correspond to a single logical line
            # but is sometimes seemingly split in two parts.
            self.problem_statement = "".join(
                self.lines if self.lines is not None else []
            )
            return (
                f"    -->{self.lineno}| {self.problem_statement}"
                if self.problem_statement
                else _(
                    "The source is unavailable.\n"
                    "If you used `exec`, consider using `friendly_exec` instead."
                )
            )


def saw_warning_before(warning_type, message, filename, lineno) -> bool:
    """Records a warning if it has not been seen at the exact location
    and returns True; returns False otherwise.
    """
    # Note: unlike show_warning whose API is dictated by Python,
    # we order the argument in some grouping that seems more logical
    # for the recorded structure
    if warning_type in _warnings_seen:
        if message in _warnings_seen[warning_type]:
            if filename in _warnings_seen[warning_type][message]:
                if lineno in _warnings_seen[warning_type][message][filename]:
                    return True
                _warnings_seen[warning_type][message][filename].append(lineno)
            else:
                _warnings_seen[warning_type][message][filename] = [lineno]
        else:
            _warnings_seen[warning_type][message] = {filename: [lineno]}
    else:
        _warnings_seen[warning_type] = {message: {}}
        _warnings_seen[warning_type][message][filename] = [lineno]
    return False


def show_warning(
    warning_instance, warning_type, filename, lineno, file=None, line=None
):
    for do_not_show_warning in IGNORE_WARNINGS:
        if do_not_show_warning(warning_instance, warning_type, filename, lineno):
            return

    if saw_warning_before(
        warning_type.__name__, str(warning_instance), filename, lineno
    ):
        # Avoid showing the same warning if it occurs in a loop, or in
        # other way in which a given instruction that give rise to a warning
        # is repeated
        return

    try:
        for outer_frame in inspect.getouterframes(inspect.currentframe()):
            if outer_frame.filename == filename and outer_frame.lineno == lineno:
                warning_data = WarningInfo(
                    warning_instance,
                    warning_type,
                    filename,
                    lineno,
                    frame=outer_frame.frame,
                    lines=outer_frame.code_context,
                )
                break
        else:
            warning_data = WarningInfo(warning_instance, warning_type, filename, lineno)
    except Exception:
        warning_data = WarningInfo(warning_instance, warning_type, filename, lineno)

    message = str(warning_instance)

    if not _RUNNING_TESTS:
        session.recorded_tracebacks.append(warning_data)
    elif "cause" in warning_data.info:
        # We know how to explain this; we do not print while running tests
        return
    session.write_err(f"`{warning_type.__name__}`: {message}\n")


INCLUDED_PARSERS = {
    SyntaxWarning: "syntax_warning",
}
WARNING_DATA_PARSERS = {}


class WarningDataParser:
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
        to a list that is automatically updated::

            @instance.add
            def some_warning_parsers(message, traceback_data):
                ....
        """
        self.custom_parsers.append(func)
        self.parsers = self.custom_parsers + self.core_parsers


def get_warning_parser(warning_type: Type[_E]) -> WarningDataParser:
    """Gets a 'parser' to find the cause for a given warning.

    Args:

        warning_type: a warning class.

    Usage::

        parser = get_warning_parser(SomeSpecificWarning)

        @parser.add
        def some_meaningful_name(warning_message: str,
                                 warning_data: WarningDataParser) -> dict:
            if not handled_by_this_function(warning_message):
                return {}  # let other parsers deal with it

            ...
    """
    if warning_type not in WARNING_DATA_PARSERS:
        WARNING_DATA_PARSERS[warning_type] = WarningDataParser()
        if warning_type in INCLUDED_PARSERS:
            base_path = "friendly_traceback.warning_parsers."
            import_module(base_path + INCLUDED_PARSERS[warning_type])
    return WARNING_DATA_PARSERS[warning_type]


def get_warning_cause(
    warning_type,
    message: str,
    warning_data: WarningDataParser = None,
) -> CauseInfo:
    """Attempts to get the likely cause of an exception."""
    try:
        return get_cause(warning_type, message, warning_data)
    except Exception as e:  # noqa # pragma: no cover
        session.write_err("Exception raised")
        session.write_err(str(e))
        session.write_err(internal_error(e))
        return {}


def get_cause(
    warning_type,
    message: str,
    warning_data: WarningDataParser,
) -> CauseInfo:
    """For a given exception type, cycle through the known message parsers,
    looking for one that can find a cause of the exception."""
    warning_parsers = get_warning_parser(warning_type)

    for parser in warning_parsers.parsers:
        # This could be simpler if we could use the walrus operator
        cause = parser(message, warning_data)
        if cause:
            return cause
    return {}
