import contextlib
import inspect
import io
import sys
import traceback
import types
from itertools import dropwhile
from typing import List, Optional, Tuple, Type

from stack_data import BlankLines, Options

from . import debug_helper
from .frame_info import FrameInfo
from .ft_gettext import current_lang
from .path_info import is_excluded_file
from .source_cache import cache
from .syntax_errors import source_info
from .typing_info import _E

STR_FAILED = "<exception str() failed>"  # Same as Python
_ = current_lang.translate


def convert_value_to_message(value: BaseException) -> str:
    """This converts the 'value' of an exception into a string, while
    being safe to use for custom exceptions which have been incorrectly
    defined. See https://github.com/aroberge/friendly/issues/181 for an example.
    """
    try:
        message = str(value)
    except Exception:  # noqa
        message = STR_FAILED
    return message


def retrieve_message(etype: Type[_E], value: _E, tb: types.TracebackType) -> str:
    "Safely retrieves the message, including any additional hint from Python."
    message = convert_value_to_message(value)
    if (
        message == STR_FAILED
        or sys.version_info < (3, 10)
        or etype not in (AttributeError, NameError)
    ):
        return message
    # 3.10+ hints are not directly accessible from Python.
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        sys.__excepthook__(etype, value, tb)
    full_message = err.getvalue().split("\n")[-2]
    return full_message.split(":", 1)[1].strip()


class TracebackData:
    """Raw traceback info obtained from Python.

    Instances of this class are intended to include all the relevant
    information about an exception so that a FriendlyTraceback object
    can be created.
    """

    def __init__(self, etype: Type[_E], value: _E, tb: types.TracebackType) -> None:
        """This object is initialized with the standard values for a
        traceback::

            etype, value, tb = sys.exc_info()
        """
        cache.remove("<fstring>")
        self.exception_type = etype
        self.exception_name = etype.__name__
        self.value = value
        self.message = str(value)
        self.full_message = retrieve_message(etype, value, tb)
        self.formatted_tb = traceback.format_exception(etype, value, tb)
        self.records = self.get_records(tb)
        self.python_records = self.get_records(tb, python_excluded=False)

        # The following three attributes get their correct values in get_source_info()
        self.bad_line = "\n"
        self.original_bad_line = "\n"
        self.filename = ""
        self.exception_frame = None
        self.program_stopped_frame = None
        self.program_stopped_bad_line = "\n"
        self.get_source_info()

        # The following attributes get their correct values in self.locate_error()
        self.node = None
        self.node_text = ""
        self.node_range: Optional[Tuple[int, int]] = None
        self.program_stopped_node_range = None

        if issubclass(etype, SyntaxError):
            self.statement: Optional[source_info.Statement] = source_info.Statement(
                self.value, self.bad_line
            )
            # Removing extra ending spaces for potentially shorter displays later on

            def remove_space(text: str) -> str:
                if text.rstrip():
                    if text.endswith("\n"):
                        return text.rstrip() + "\n"
                    return text.rstrip()
                return text

            self.statement.entire_statement = remove_space(
                self.statement.entire_statement
            )
            self.statement.bad_line = remove_space(self.statement.bad_line)
        else:
            self.statement = None
            self.locate_error()

    def get_records(
        self, tb: types.TracebackType, python_excluded: bool = True
    ) -> List[FrameInfo]:
        """Get the traceback frame history, excluding those originating
        from our own code that are included either at the beginning or
        at the end of the traceback.
        """
        try:
            all_records = list(
                FrameInfo.stack_data(
                    tb,
                    Options(blank_lines=BlankLines.SINGLE),
                    collapse_repeated_frames=False,
                )
            )
            records = list(
                dropwhile(
                    lambda record: is_excluded_file(
                        record.filename, python_excluded=python_excluded
                    ),
                    all_records,
                )
            )
            records.reverse()
            records = list(
                dropwhile(
                    lambda record: is_excluded_file(
                        record.filename, python_excluded=python_excluded
                    ),
                    records,
                )
            )
            records.reverse()
            if records or issubclass(self.exception_type, (SyntaxError, MemoryError)):
                return records
        except AssertionError:  # from stack_data
            # problems may arise when SyntaxErrors are raise
            # from a normal console like the one used in Mu.
            all_records = inspect.getinnerframes(tb, cache.context)
            records = list(
                dropwhile(
                    lambda record: is_excluded_file(
                        record.filename, python_excluded=python_excluded
                    ),
                    all_records,
                )
            )
            records.reverse()
            records = list(
                dropwhile(
                    lambda record: is_excluded_file(
                        record.filename, python_excluded=python_excluded
                    ),
                    records,
                )
            )
            records.reverse()
            if records or issubclass(self.exception_type, (SyntaxError, MemoryError)):
                return records
        # If all the records are removed, it likely means that all the error
        # is in our own code - or that of the user who chose to exclude
        # some files. If so, we make sure to have something to analyze
        # and help identify the problem.
        return all_records  # pragma: no cover

    def get_source_info(self) -> None:
        """Retrieves the file name and the line of code where the exception
        was raised.
        """
        if issubclass(self.exception_type, SyntaxError):
            self.filename = self.value.filename
            # Python 3.10 introduced new arguments. For simplicity,
            # we give them some default values for other Python versions
            # so that we can use these elsewhere without having to perform
            # additional checks.
            if not hasattr(self.value, "end_offset"):
                self.value.end_offset = (
                    self.value.offset + 1 if self.value.offset else 0
                )
                self.value.end_lineno = self.value.lineno

            # Normally, when an error occurs entirely on a given line,
            # the end offset should be at least one more than the offset.
            # However, as noted in issue #34, that might not always be the case.
            # To show the location of the error, we do need to have
            # offset and end_offset be different.
            if (
                self.value.end_lineno == self.value.lineno
                and self.value.end_offset == self.value.offset
            ):
                self.value.end_offset += 1

            if self.value.text is not None:
                self.bad_line = self.value.text  # typically includes "\n"
                self.original_bad_line = self.bad_line
                return

            # this can happen with editors_helpers.check_syntax()
            try:
                self.bad_line = cache.get_source_lines(self.filename)[
                    self.value.lineno - 1
                ]
            except Exception:  # noqa
                self.bad_line = "\n"
            return

        if self.records:
            record = self.records[-1]
            self.exception_frame = record.frame
            self.filename = record.filename
            line = record.problem_line()
            self.original_bad_line = line
            self.bad_line = line.strip()  # strip() is fix for 3.11
            # protecting against https://github.com/alexmojaki/stack_data/issues/13
            if not self.bad_line:
                try:
                    lines = cache.get_source_lines(record.filename)
                    self.bad_line = lines[record.lineno - 1]
                except Exception:  # noqa
                    debug_helper.log("Could not get bad_line")

            if len(self.records) > 1:
                record = self.records[0]
                line = record.problem_line()
                self.program_stopped_frame = record.frame
                self.program_stopped_bad_line = line.rstrip()
            else:
                self.program_stopped_bad_line = self.bad_line
                self.program_stopped_frame = self.exception_frame
            return

        if issubclass(self.exception_type, MemoryError):
            self.bad_line = "<not available>"
            return

        # We should never reach this stage.
        def _log_error() -> None:  # pragma: no cover
            debug_helper.log("Internal error in TracebackData.get_source_info.")
            debug_helper.log("No records found.")
            debug_helper.log("self.exception_type:" + str(self.exception_type))
            debug_helper.log("self.value:" + str(self.value))
            debug_helper.log_error()

        _log_error()  # pragma: no cover

    def locate_error(self) -> None:
        """Attempts to narrow down the location of the error so that,
        if possible, the problem code is highlighted with ^^^^."""
        if not self.records:  # pragma: no cover
            if issubclass(self.exception_type, MemoryError):
                return
            debug_helper.log("No records in locate_error().")
            return

        node_info = self.records[-1].node_info  # noqa
        if node_info:
            self.node, _ignore, self.node_text = node_info
            if self.node_text.strip():
                # Replacing the line that caused the exception by the text
                # of the 'node' facilitates the process of identifying the cause.
                self.bad_line = self.node_text.strip()  # strip() is fix for 3.11beta

        # Also attempt to restrict the information about where the program
        # stopped to the strict minimum so that we don't show irrelevant
        # values of names
        if self.records[0].node_info and self.records[0].node_info != node_info:
            node, _ignore, node_text = self.records[0].node_info
            if node_text.strip():
                self.program_stopped_bad_line = node_text
