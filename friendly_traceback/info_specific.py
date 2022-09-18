"""info_specific.py

Attempts to provide some specific information about the likely cause
of a given exception.
"""
from types import FrameType
from typing import TYPE_CHECKING, Dict, Type

from .ft_gettext import current_lang
from .typing_info import _E, CauseInfo, Explain

if TYPE_CHECKING:
    from .core import TracebackData

from . import message_parser

get_cause: Dict[Type[BaseException], Explain[BaseException]] = {}
_ = current_lang.translate


def get_likely_cause(
    etype: Type[_E], message: str, frame: FrameType, tb_data: "TracebackData"
) -> CauseInfo:
    """Gets the likely cause of a given exception based on some information
    specific to a given exception.
    """

    message_parser.init_parser(etype)

    # We could have parsers for exception defined by third-parties
    if etype in message_parser.RUNTIME_MESSAGE_PARSERS:
        return message_parser.get_cause(etype, message, tb_data)

    try:
        # see if it could be the result of using socket, or urllib, urllib3, etc.
        if issubclass(etype, OSError):
            return message_parser.get_cause(OSError, message, tb_data)
    except Exception:  # noqa  # pragma: no cover
        pass

    return {}
