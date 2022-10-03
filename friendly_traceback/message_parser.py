"""This module contains the necessary class and functions needed to
help finding the cause (specific information aka answer to ``why()``)
of an exception. Most of the content should be considered to be private.

It does contain one function (``get_parser``)
which is intended to be part of the public API, but needs to be
imported from this module instead of simply from ``friendly_traceback``.
"""


from importlib import import_module
from typing import List, Type

from . import debug_helper
from .ft_gettext import internal_error, no_information, unknown_case
from .tb_data import TracebackData  # for type checking only
from .typing_info import _E, CauseInfo, Parser

INCLUDED_PARSERS = {
    AttributeError: "attribute_error",
    FileNotFoundError: "file_not_found_error",
    ImportError: "import_error",
    IndexError: "index_error",
    KeyError: "key_error",
    ModuleNotFoundError: "module_not_found_error",
    NameError: "name_error",
    OSError: "os_error",
    RuntimeError: "runtime_error",
    TypeError: "type_error",
    UnboundLocalError: "unbound_local_error",
    ValueError: "value_error",
    ZeroDivisionError: "zero_division_error",
}
RUNTIME_MESSAGE_PARSERS = {}


class RuntimeMessageParser:
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
            def some_message_parser(message, traceback_data):
                ....
        """
        self.custom_parsers.append(func)
        self.parsers = self.custom_parsers + self.core_parsers


def get_parser(exception_type: Type[_E]) -> RuntimeMessageParser:
    """Gets a 'parser' to find the cause for a given exception.
    Usage::

        parser = get_parser(SomeSpecificError)

        @parser.add
        def some_meaningful_name(message: str,
                                 tb_data: TracebackData) -> dict:
            if not handled_by_this_function(message):
                return {}  # let other parsers deal with it

            ...
    """
    if exception_type not in RUNTIME_MESSAGE_PARSERS:
        RUNTIME_MESSAGE_PARSERS[exception_type] = RuntimeMessageParser()
        if exception_type in INCLUDED_PARSERS:
            base_path = "friendly_traceback.runtime_errors."
            import_module(base_path + INCLUDED_PARSERS[exception_type])
    return RUNTIME_MESSAGE_PARSERS[exception_type]


def get_likely_cause(
    exception_type,
    message: str,
    tb_data: TracebackData,
) -> CauseInfo:
    """Attempts to get the likely cause of an exception."""
    try:
        return get_cause(exception_type, message, tb_data)
    except Exception as e:  # noqa # pragma: no cover
        debug_helper.log(message)
        return {"cause": internal_error(e), "suggest": internal_error(e)}


def get_cause(
    exception_type,
    message: str,
    tb_data: TracebackData,
) -> CauseInfo:
    """For a given exception type, cycle through the known message parsers,
    looking for one that can find a cause of the exception."""
    message_parser = get_parser(exception_type)

    for parser in message_parser.parsers:
        # This could be simpler if we could use the walrus operator
        cause = parser(message, tb_data)
        if cause:
            return cause

    # Special case where a connection attempt failed when using
    # socket, or urllib, urllib3, etc.
    try:
        if issubclass(exception_type, OSError):
            os_error_parser = get_parser(OSError)
            for parser in os_error_parser.parsers:
                cause = parser(message, tb_data)
                if cause:
                    return cause
                else:
                    return {"cause": no_information(), "suggest": unknown_case()}
    except Exception:  # noqa  # pragma: no cover
        pass

    if not message_parser.parsers:
        return {}

    debug_helper.log(str(message))
    return {"cause": no_information(), "suggest": unknown_case()}
