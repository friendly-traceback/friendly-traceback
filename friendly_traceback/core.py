"""core.py

The exception hook at the heart of Friendly.

You should not need to use any of the functions defined here;
they are considered to be internal functions, subject to change at any
time. If functions defined in friendly_traceback.__init__.py do not meet your needs,
please file an issue.
"""
import contextlib
import inspect
import io
import re
import sys
import traceback
import types
from itertools import dropwhile
from typing import List, Optional, Sequence, Tuple, Type

from . import debug_helper, info_generic, info_specific, info_variables
from .frame_info import FrameInfo
from .ft_gettext import current_lang
from .path_info import is_excluded_file, path_utils
from .source_cache import cache
from .syntax_errors import analyze_syntax, indentation_error, source_info
from .typing_info import _E, Info

try:
    import executing  # noqa
except ImportError:  # pragma: no cover
    pass  # ignore errors when processed by Sphinx


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
        self.message = retrieve_message(etype, value, tb)
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
            all_records = list(FrameInfo.stack_data(tb, collapse_repeated_frames=False))
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


# ====================
# The following is an example of a formatted traceback, with
# some parts identified with (partial) names used below
#
# Python exception:  [header]

# [message]
#     UnboundLocalError: local variable 'a' referenced before assignment

# [generic]
# In Python, variables that are used inside a function are known as
# local variables. Before they are used, they must be assigned a value.
# A variable that is used before it is assigned a value is assumed to
# be defined outside that function; it is known as a 'global'
# (or sometimes 'nonlocal') variable. You cannot assign a value to such
# a global variable inside a function without first indicating to
# Python that this is a global variable, otherwise you will see
# an UnboundLocalError.

# [cause_header and cause]
# Likely cause:
#     The variable that appears to cause the problem is 'abc'.
#     Try inserting the statement
#         global abc
#     as the first line inside your function.
#

# [last_call_ ...]
# Execution stopped on line 14 of file 'C:\Users...\test_unbound_local_error.py'.
#    12:
#    13:     try:
# -->14:         inner()
#
# inner: <function test_unbound_local_error.<location... >

# [exception_raised_ ...]
# Exception raised on line 11 of file 'C:\Users\...\test_unbound_local_error.py'.
#     9:     def inner():
#    10:         b = 2
# -->11:         a = a + b
#
# [6]
# b: 2


class FriendlyTraceback:
    """Main class for creating a friendly traceback.

    All the information available to the end user is stored in a
    dict called "info". The various keys of that dict are documented
    in the docstrings of the relevant methods.

    To get all possible attributes set up, one needs to call
    compile_info() after initializing this class. This is done
    to allow third-party users to selectively call only one of

    * assign_cause()
    * assign_generic()
    * assign_location()

    if they so wish.

    Various functions are available when using a friendly console,
    which can show part of the information compile here.
    Among those:

    * where() shows the result of assign_location()
    * why() shows the cause, as compiled by assign_cause()
    * hint() is a shorter version of why(), sometimes available.
    * what() shows the information compiled by assign_generic()
    """

    info: Info

    def __init__(self, etype: Type[_E], value: _E, tb: types.TracebackType) -> None:
        """The basic argument are those generated after a traceback
        and obtained via::

            etype, value, tb = sys.exc_info()

        The "header" key for the info dict is assigned here."""
        try:
            self.tb_data = TracebackData(etype, value, tb)
        except Exception as e:  # pragma: no cover
            debug_helper.log("Uncaught exception in TracebackData:")
            debug_helper.handle_internal_error(e)
            raise SystemExit
        self.tb = tb
        self.suppressed = ["       ... " + _("More lines not shown.") + " ..."]
        self.info = {"header": _("Python exception:")}
        self.message = self.assign_message(etype, value, tb)  # language independent
        self.assign_tracebacks()

        # include some values for debugging purpose in an interactive session
        self.info["_exc_instance"] = value
        self.info["_frame"] = self.tb_data.exception_frame
        self.info["_tb_data"] = self.tb_data

    def assign_message(self, etype, value, tb) -> str:
        """Assigns the error message, as the attribute ``message``
        which is something like::

            NameError: name 'a' is not defined
        """
        exc_name = etype.__name__
        if hasattr(value, "msg"):
            self.info["message"] = f"{exc_name}: {value.msg}\n"
        else:
            message = retrieve_message(etype, value, tb)
            self.info["message"] = f"{exc_name}: {message}\n"
        return self.info["message"]

    def compile_info(self) -> None:
        """Compile all info that was not set in __init__."""
        self.assign_generic()
        # For SyntaxError, assigning the cause may result in better location
        # information; so we need to do this first.
        self.assign_cause()
        self.assign_location()
        # removing null values; mypy cannot figure out the type correctly here
        to_remove = [key for key in self.info if not self.info[key]]  # type: ignore
        for key in to_remove:
            del self.info[key]

    def recompile_info(self) -> None:
        """This is useful if we need to redisplay some information in a
        different language than what was originally used.
        """
        self.info["header"] = _("Python exception:")
        self.assign_tracebacks()
        self.compile_info()

    def assign_cause(self) -> None:
        """Determine the cause of an exception, which is what is returned
        by ``why()``.
        """
        try:
            if self.tb_data.filename == "<unknown>" or (
                self.tb_data.filename == "<string>"
                and self.tb_data.value.lineno != 1
                and not issubclass(self.tb_data.exception_type, SyntaxError)
            ):
                return
        except Exception:
            return

        if STR_FAILED in self.message:
            self.info["cause"] = _(
                "Warning: improperly formed exception.\n"
                "I suspect that a custom exception has been raised\n"
                "with a non-string value used as a message.\n"
                "This can occur if a `__repr__` or a `__str__` method\n"
                "raises an exception or does not return a string.\n"
            )
        elif issubclass(self.tb_data.exception_type, SyntaxError):
            self.set_cause_syntax()
        else:
            self.set_cause_runtime()

    def set_cause_runtime(self) -> None:
        """For exceptions other than SyntaxError and subclasses.
        Sets the value of the following attributes:

        * cause_header
        * cause

        and possibly:

        * suggest

        the latter being the "hint" appended to the friendly traceback.
        """
        etype = self.tb_data.exception_type
        value = self.tb_data.value

        cause = info_specific.get_likely_cause(
            etype, value, self.tb_data.exception_frame, self.tb_data
        )  # [3]
        self.info.update(**cause)

    def set_cause_syntax(self) -> None:
        """For SyntaxError and subclasses. Sets the value of the following
        attributes:

        * cause_header
        * cause

        and possibly:

        * suggest

        the latter being the "hint" appended to the friendly traceback.
        """
        etype = self.tb_data.exception_type
        value = self.tb_data.value

        if self.tb_data.filename == "<unknown>":
            return

        if "encoding problem" in str(self.tb_data.value):
            self.info["cause"] = _("The encoding of the file was not valid.\n")
            return

        if etype.__name__ == "IndentationError":
            self.info["cause"] = indentation_error.set_cause_indentation_error(
                value, self.tb_data.statement
            )
            return

        if etype.__name__ == "TabError":
            return

        cause = analyze_syntax.set_cause_syntax(value, self.tb_data)
        self.info.update(**cause)

    def assign_generic(self) -> None:
        """Assigns the generic information about a given error. This is
        the answer to ``what()`` as in "What is a NameError?"

        Sets the value of the following attribute:

        * generic
        """
        self.info["generic"] = info_generic.get_generic_explanation(
            self.tb_data.exception_type
        )

    def assign_location(self) -> None:
        """This sets the values of the answers to 'where()', that is
        the information about the location of the exception.

        To determine which attributes will be set, consult the docstring
        of the following methods.

        For SyntaxError and subclasses: self.locate_parsing_error()

        For other types of exceptions, self.locate_exception_raised(),
        and possibly self.locate_last_call().
        """
        if issubclass(self.tb_data.exception_type, SyntaxError):
            self.locate_parsing_error()
            return

        records = self.tb_data.records
        if not records:  # pragma: no cover
            if issubclass(self.tb_data.exception_type, MemoryError):
                return
            debug_helper.log("No record in assign_location().")
            return

        self.locate_exception_raised(records[-1])
        self.info["detailed_tb"] = self.get_detailed_stack_info(records)
        if len(records) > 1:
            _ignore, partial_source, var_info = self.info["detailed_tb"][0]
            self.locate_last_call(records[0], partial_source, var_info)

    def locate_exception_raised(self, record: FrameInfo) -> None:
        """Sets the values of the following attributes which are
        part of a friendly

        * exception_raised_header
        * exception_raised_source
        * exception_raised_variables
        """
        from .config import session

        if self.tb_data.filename == "<stdin>":
            self.info["exception_raised_source"] = cannot_analyze_stdin()
            self.info["exception_raised_header"] = ""
            return

        partial_source = record.partial_source_with_node_range
        if partial_source["source"].strip() == "0:":
            partial_source["source"] = ""
        filename = path_utils.shorten_path(record.filename)

        unavailable = filename in ["<unknown>", "<string>"]
        if unavailable:
            self.info["exception_raised_source"] = _(
                "{filename} is not a regular Python file whose contents can be analyzed.\n"
            ).format(filename=filename)

        if session.ipython_prompt and filename.startswith("["):
            self.info["exception_raised_header"] = _(
                "Exception raised on line {linenumber} of code block {filename}.\n"
            ).format(linenumber=record.lineno, filename=filename)
        else:
            self.info["exception_raised_header"] = _(
                "Exception raised on line {linenumber} of file {filename}.\n"
            ).format(linenumber=record.lineno, filename=filename)

        if unavailable:
            return

        source = partial_source["source"]
        if source.strip() in ["-->1:", "1:"]:
            source = _(
                "{filename} is not a regular Python file whose contents can be analyzed.\n"
            ).format(filename=filename)

        self.info["exception_raised_source"] = source

        if self.tb_data.node_text:
            line = self.tb_data.node_text
        else:
            line = partial_source["line"]

        var_info = info_variables.get_var_info(line, record.frame)
        self.info["exception_raised_variables"] = var_info["var_info"]
        if "warnings" in var_info:
            self.info["warnings"] = var_info["warnings"]

    def locate_last_call(self, record: FrameInfo, partial_source, var_info) -> None:
        """Sets the values of the following attributes:

        * last_call_header
        * exception_raised_source
        * last_call_variables
        """
        filename = path_utils.shorten_path(record.filename)

        if filename and "[" in filename:
            self.info["last_call_header"] = _(
                "Execution stopped on line {linenumber} of code block {filename}.\n"
            ).format(linenumber=record.lineno, filename=filename)
        else:
            self.info["last_call_header"] = _(
                "Execution stopped on line {linenumber} of file {filename}.\n"
            ).format(linenumber=record.lineno, filename=filename)
        self.info["last_call_source"] = partial_source

        if var_info:
            self.info["last_call_variables"] = var_info

    def get_detailed_stack_info(self, records):
        # sourcery skip: use-named-expression
        if self.tb_data.filename == "<stdin>":
            return []

        detailed_tb = []
        for record in self.tb_data.records:
            filename = path_utils.shorten_path(record.filename)
            lineno = record.lineno
            if record.node_info:
                _node, _ignore, line = record.node_info
            else:
                line = record.problem_line()
            partial_source = record.partial_source_with_node_range
            var_info = info_variables.get_var_info(line, record.frame)
            if "[" in filename:
                location = _("Code block {filename}, line {line}").format(
                    filename=filename, line=lineno
                )
            else:
                location = _("File {filename}, line {line}").format(
                    filename=filename, line=lineno
                )
            detailed_tb.append(
                (location, partial_source["source"], var_info["var_info"])
            )
        return detailed_tb

    def locate_parsing_error(self) -> None:
        """Sets the values of the attributes:

        * parsing_error
        * parsing_source_error
        """
        value = self.tb_data.value
        filepath = value.filename
        not_regular_file = _(
            "The entire content of `{filename}` is not available.\n"
        ).format(filename=filepath)
        if filepath == "<unknown>":
            self.info["parsing_error"] = not_regular_file
            return

        statement = self.tb_data.statement
        statement.format_statement()
        partial_source = statement.formatted_partial_source

        short_filename = path_utils.shorten_path(filepath)

        if short_filename and "[" in short_filename:
            could_not_understand = _(
                "Python could not understand the code in the code block {filename}\n"
            ).format(filename=short_filename)
        else:
            could_not_understand = _(
                "Python could not understand the code in the file\n'{filename}'\n"
            ).format(filename=short_filename)

        if "  ^" in partial_source:
            self.info["parsing_error"] = could_not_understand + _(
                "at the location indicated.\n"
            ).format(filename=short_filename)
            if filepath in ["<string>", "<stdin>"] and self.tb_data.value.lineno != 1:
                self.info["parsing_error"] += not_regular_file
        elif filepath:  # could be None
            self.info["parsing_error"] = could_not_understand + ".\n"

        self.info["parsing_error_source"] = f"{partial_source}\n"

    def assign_tracebacks(self) -> None:
        """When required, a standard Python traceback might be required to be
        included as part of the information shown to the user.
        This function does the required formatting.

        This function defines 3 traceback:
        1. The standard Python traceback, given by Python
        2. A "simulated" Python traceback, which is essentially the same as
           the one given by Python, except that it excludes modules from this
           project.  In addition, for RecursionError, this traceback is often
           further shortened, compared with a normal Python traceback.
        3. A potentially shortened traceback, which does not include too much
           output so as not to overwhelm beginners. It also includes information
           about the code on any line mentioned.

        These are given by the attributes:

        * original_python_traceback
        * simulated_python_traceback
        * shortened_traceback
        """
        if not hasattr(self, "message"):
            self.assign_message(
                self.tb_data.exception_type, self.tb_data.value, self.tb
            )
        if isinstance(self.tb_data.formatted_tb, str):
            # for example: "Traceback not available from IDLE" ...
            tb = self.info["message"]
            if self.tb_data.formatted_tb:
                tb = self.info["message"] + "\n" + self.tb_data.formatted_tb + "\n"
            self.info["simulated_python_traceback"] = tb
            self.info["shortened_traceback"] = tb
            self.info["original_python_traceback"] = tb
            return

        # full_tb includes code from friendly-traceback itself
        full_tb = [line.rstrip() for line in self.tb_data.formatted_tb]
        python_tb = self.create_traceback(self.tb_data.python_records)
        tb = self.create_traceback(self.tb_data.records)
        shortened_tb = self.shorten(tb)

        header = "Traceback (most recent call last):"  # not included in records
        if full_tb[0].startswith(header) and self.tb_data.filename is not None:
            if not issubclass(self.tb_data.exception_type, SyntaxError):
                shortened_tb.insert(0, header)
                python_tb.insert(0, header)
            else:
                # The special "Traceback ..." header is not normally shown when
                # a SyntaxError occurs at an interactive prompt.
                # In this case, the filename will normally be of the form "<...>"
                # or we will have changed "File" to be "Code block"
                for line in shortened_tb:
                    if line.startswith("  File") and "<" not in line:
                        # We have a true file in the traceback
                        shortened_tb.insert(0, header)
                        python_tb.insert(0, header)
                        break

        if "RecursionError" in full_tb[-1]:
            if len(shortened_tb) > 12:
                shortened_tb = shortened_tb[0:5] + self.suppressed + shortened_tb[-5:]
            if len(python_tb) > 12:
                python_tb = python_tb[0:5] + self.suppressed + python_tb[-5:]

        exc = self.tb_data.value
        chain_info = ""
        short_chain_info = ""
        if exc.__cause__ or exc.__context__:
            chain_info = process_exception_chain(self.tb_data.exception_type, exc)
            parts = chain_info.split("\n\n")
            # suppress line
            temp = []
            for part in parts:
                part = "\n".join(self.shorten(part.split("\n")))
                temp.append(part)
            short_chain_info = "\n\n".join(temp)

        self.info["simulated_python_traceback"] = (
            chain_info + "\n".join(python_tb) + "\n"
        )
        self.info["shortened_traceback"] = (
            short_chain_info + "\n".join(shortened_tb) + "\n"
        )
        self.info["original_python_traceback"] = chain_info + "\n".join(full_tb) + "\n"
        # The following is needed for some determining the cause in at
        # least one case.
        # skipcq: PYL-W0201
        self.tb_data.simulated_python_traceback = "\n".join(python_tb) + "\n"

    def shorten(self, tb: Sequence[str]) -> List[str]:
        """Shortens a traceback (as list of lines)
        by removing lines if it exceeds a certain length
        and by using short synonyms for some common directories."""
        from .config import session

        shortened_tb = tb[0:2] + self.suppressed + tb[-5:] if len(tb) > 12 else tb[:]
        pattern = re.compile(r'^  File "(.*)", ')  # noqa
        temp = []
        for line in shortened_tb:
            match = re.search(pattern, line)
            if match:
                filename = match.group(1)
                short_filename = path_utils.shorten_path(filename)
                line = line.replace(filename, short_filename)
                if (
                    session.ipython_prompt
                    and short_filename[0] == "["
                    and short_filename[-1] == "]"
                ):
                    line = line.replace("  File", "  Code block")
                    line = line.replace('"[', "[").replace(']"', "]")
                    parts = line.split(",")
                    line = ",".join(parts[:2])
            temp.append(line)
        return temp

    def create_traceback(self, records: List[FrameInfo]) -> List[str]:
        """Using records that exclude code from certain files,
        creates a list from which a standard-looking traceback can
        be created.
        """
        result = []
        for record in records:
            partial_source = record.partial_source  # noqa
            result.append(
                '  File "{}", line {}, in {}'.format(
                    record.filename, record.lineno, record.code.co_name
                )
            )
            bad_line = partial_source["line"]
            if bad_line is not None:
                result.append("    {}".format(bad_line.strip()))

        if issubclass(self.tb_data.exception_type, SyntaxError):
            value = self.tb_data.value
            offset = value.offset
            filename = value.filename
            lines = cache.get_source_lines(filename)
            result.append('  File "{}", line {}'.format(filename, value.lineno))
            _line = value.text
            if _line is None:
                try:
                    _line = lines[value.lineno - 1]
                except Exception:  # noqa
                    pass
            if _line is not None:
                if filename == "<fstring>" and lines == ["\n"]:
                    # Before Python 3.9, the traceback included a fake
                    # file for f-strings which only included parts of
                    # the f-string content.
                    cache.add(filename, _line)
                _line = _line.rstrip()
                bad_line = _line.strip()
                if bad_line:
                    # Note end_lineno and end_offset are new in Python 3.10
                    # However, we ensured prior to reaching this point that
                    # they would be defined for other Python versions
                    if (
                        value.end_lineno is not None
                        and value.end_lineno != value.lineno
                        or value.end_offset is not None
                        and value.end_offset < 1
                    ):
                        nb_carets = len(bad_line) - offset + 1
                        continuation = "-->"
                    else:
                        nb_carets = value.end_offset - offset if value.end_offset else 1
                        continuation = ""
                    offset = offset - (len(_line) - len(bad_line))  # removing indent
                    # In some IndentationError cases, and possibly others,
                    # Python's computed offset would show the ^ just before the first token
                    if offset < 1:
                        offset = 1
                        nb_carets = 1
                        continuation = ""
                    result.append("    {}".format(bad_line))
                    result.append(" " * (3 + offset) + "^" * nb_carets + continuation)
        result.append(self.info["message"].strip())
        return result


def process_exception_chain(etype: Type[_E], value: _E) -> str:
    """Obtains info about exceptions raised while treating other exceptions."""
    seen = set()
    lines = []

    direct_cause = (
        "The above exception was the direct cause of the following exception:"
    )
    another_exception = (
        "During handling of the above exception, another exception occurred:"
    )

    def chain_exc(typ: Type[_E], exc: _E, tb: Optional[types.TracebackType]) -> None:
        """Recursive function that insert the contents of 'lines' above."""
        seen.add(id(exc))
        context = exc.__context__
        cause = exc.__cause__
        if cause is not None and id(cause) not in seen:
            chain_exc(type(cause), cause, cause.__traceback__)
            lines.append(f"\n    {direct_cause}\n\n")
        elif (
            context is not None
            and not exc.__suppress_context__
            and id(context) not in seen
        ):
            chain_exc(type(context), context, context.__traceback__)
            lines.append(f"\n    {another_exception}\n\n")
        if tb:
            tbe = traceback.extract_tb(tb)
            lines.append("Traceback (most recent call last):\n")
            for line in traceback.format_list(tbe):
                lines.append(line)
            for line in traceback.format_exception_only(typ, exc):
                lines.append(line)

    chain_exc(etype, value, None)
    return "".join(lines)


def cannot_analyze_stdin() -> str:  # pragma: no cover
    """Typical case: friendly is imported in an ordinary Python
    interpreter (REPL), and the user does not activate the friendly
    console.
    """
    from .config import session

    message = _(
        "Unfortunately, no additional information is available:\n"
        "the content of file '<stdin>' is not accessible.\n"
    )
    if session.suggest_console:
        print(session.suggest_console)
        session.suggest_console = ""
    return message
