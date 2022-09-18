from importlib import import_module
from typing import List, Type

from . import debug_helper
from .ft_gettext import internal_error, no_information, unknown_case
from .tb_data import TracebackData  # for type checking only
from .typing_info import _E, CauseInfo, Parser

INCLUDED_PARSERS = {
    AttributeError: "attribute_error",
    FileNotFoundError: "file_not_found_error",
}
RUNTIME_MESSAGE_PARSERS = {}


def init_parser(exception_type: Type[_E]) -> None:
    if exception_type in RUNTIME_MESSAGE_PARSERS:
        return
    elif exception_type in INCLUDED_PARSERS:
        get_parser(exception_type)


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
        to a list that is automatically updated.

            @instance.add
            def some_message_parser(message, traceback_data):
                ....
        """
        self.custom_parsers.append(func)
        self.parsers = self.custom_parsers + self.core_parsers


def get_parser(exception_type: Type[_E]) -> RuntimeMessageParser:
    if exception_type not in RUNTIME_MESSAGE_PARSERS:
        RUNTIME_MESSAGE_PARSERS[exception_type] = RuntimeMessageParser()
        if exception_type in INCLUDED_PARSERS:
            base_path = "friendly_traceback.runtime_errors."
            import_module(base_path + INCLUDED_PARSERS[exception_type])

    return RUNTIME_MESSAGE_PARSERS[exception_type]


def get_cause(
    exception_type,
    message: str,
    tb_data: TracebackData,
) -> CauseInfo:
    """Called from info_specific.py where, depending on error type,
    the value could be converted into a message by calling str().
    """
    try:
        return _get_cause(exception_type, message, tb_data)
    except Exception as e:  # noqa # pragma: no cover
        debug_helper.log_2(str(message))
        return {"cause": internal_error(e), "suggest": internal_error(e)}


def _get_cause(
    exception_type,
    message: str,
    tb_data: TracebackData,
) -> CauseInfo:
    """Cycle through the parsers, looking for one that can find a cause."""
    message_parser = get_parser(exception_type)
    for current_parser in message_parser.parsers:
        # This could be simpler if we could use the walrus operator
        cause = current_parser(message, tb_data)
        if cause:
            return cause
    debug_helper.log_2(str(message))
    return {"cause": no_information(), "suggest": unknown_case()}
