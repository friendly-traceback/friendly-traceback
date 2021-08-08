"""Only identifying failed connection to a server for now."""
from types import FrameType

from ..core import TracebackData
from ..ft_gettext import current_lang, no_information
from ..typing import CauseInfo


def get_cause(_value: OSError, _frame: FrameType, tb_data: TracebackData) -> CauseInfo:

    tb = "\n".join(tb_data.formatted_tb)
    if (
        "socket.gaierror" in tb
        or "urllib.error" in tb
        or "urllib3.exception" in tb
        or "requests.exception" in tb
    ):
        return handle_connection_error()
    return {"cause": no_information()}


def handle_connection_error() -> CauseInfo:
    _ = current_lang.translate
    cause = _(
        "I suspect that you are trying to connect to a server and\n"
        "that a connection cannot be made.\n\n"
        "If that is the case, check for typos in the URL\n"
        "and check your internet connectivity.\n"
    )
    return {"cause": cause}
