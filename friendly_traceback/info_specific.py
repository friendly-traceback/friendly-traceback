"""info_specific.py

Attempts to provide some specific information about the likely cause
of a given exception.
"""
from types import FrameType
from typing import TYPE_CHECKING, Callable, Dict, Type

from . import debug_helper
from .ft_gettext import current_lang, internal_error
from .typing_info import _E, CauseInfo, Explain

if TYPE_CHECKING:
    from .core import TracebackData

from . import message_parser

get_cause: Dict[Type[BaseException], Explain[BaseException]] = {}
_ = current_lang.translate


def get_likely_cause(
    etype: Type[_E], value: str, frame: FrameType, tb_data: "TracebackData"
) -> CauseInfo:
    """Gets the likely cause of a given exception based on some information
    specific to a given exception.
    """
    try:
        if etype in get_cause:
            return get_cause[etype](value, frame, tb_data)
    except Exception as e:  # noqa  # pragma: no cover
        debug_helper.log("Exception caught in get_likely_cause().")
        debug_helper.log_error(e)
        return {"cause": internal_error(e)}

    message_parser.init_parser(etype)

    # We could have parsers for exception defined by third-parties
    if etype in message_parser.RUNTIME_MESSAGE_PARSERS:
        return message_parser.get_cause(etype, value, tb_data)

    try:
        # see if it could be the result of using socket, or urllib, urllib3, etc.
        if issubclass(etype, OSError):
            return get_cause[OSError](value, frame, tb_data)
    except Exception:  # noqa  # pragma: no cover
        pass

    return {}


def register(error_name: Type[_E]) -> Callable[[Explain[_E]], None]:
    """Decorator used to record as available an explanation for a given exception"""

    def add_exception(function: Explain[_E]) -> None:
        get_cause[error_name] = function

    return add_exception


@register(OSError)
def _os_error(value: OSError, frame: FrameType, tb_data: "TracebackData") -> CauseInfo:

    from .runtime_errors import os_error

    return os_error.parser.get_cause(value, frame, tb_data)


@register(ValueError)
def _value_error(
    value: ValueError, frame: FrameType, tb_data: "TracebackData"
) -> CauseInfo:
    from .runtime_errors import value_error

    return value_error.parser.get_cause(str(value), frame, tb_data)


@register(UnboundLocalError)
def _unbound_local_error(
    value: UnboundLocalError, frame: FrameType, tb_data: "TracebackData"
) -> CauseInfo:
    from .runtime_errors import unbound_local_error

    return unbound_local_error.parser.get_cause(str(value), frame, tb_data)


@register(ZeroDivisionError)
def _zero_division_error(
    value: ZeroDivisionError, frame: FrameType, tb_data: "TracebackData"
) -> CauseInfo:
    from .runtime_errors import zero_division_error

    return zero_division_error.parser.get_cause(str(value), frame, tb_data)
