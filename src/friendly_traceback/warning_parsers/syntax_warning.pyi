from ..about_warnings import WarningInfo, WarningDataParser
from ..message_parser import CauseInfo

parser: WarningDataParser

@parser._add
def object_is_not_callable(message: str, _warning_data: WarningInfo) -> CauseInfo: ...
@parser._add
def list_indices_must_be(message: str, _warning_data: WarningInfo) -> CauseInfo: ...
@parser._add
def object_is_not_subscriptable(
    message: str, _warning_data: WarningInfo
) -> CauseInfo: ...
