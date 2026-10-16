from typing import Callable

import inspect
import re
import unicodedata
from types import FrameType
from typing import Any, Optional, Tuple
from .. import debug_helper, info_variables, token_utils, utils
from ..ft_gettext import current_lang
from ..message_parser import get_parser
from ..tb_data import TracebackData
from ..typing_info import CauseInfo

convert_type: Callable[[str], str]
parser: RuntimeMessageParser


def get_iterable(code: str, frame: FrameType) -> Tuple[Any, Optional[str]]: ...


@parser._add
def not_enough_values_to_unpack(message: str, tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def too_many_values_to_unpack(message: str, tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def invalid_literal_for_int(message: str, _tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def base_for_int(message: str, tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def date_month_must_be_between_1_and_12(message: str, _tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def could_not_convert_to_float(message: str, _tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def slots_conflicts_with_class_variable(message: str, _tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def pow_third_arg_cannot_be_zero(message: str, _tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def unrecognized_message(_message: str, tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def time_strftime_incorrect_format(message: str, _tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def list_remove_x_not_in_list(message: str, tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def generic_explanation_already_exist(message: str, _tb_data: TracebackData) -> CauseInfo: ...
