from _typeshed import Incomplete

from typing import SupportsInt, Union
from .. import debug_helper
from ..ft_gettext import current_lang
from ..message_parser import get_parser
from ..tb_data import TracebackData
from ..typing_info import CauseInfo

parser: RuntimeMessageParser


def expression_is_zero(expression: Union[str, bytes, SupportsInt], modulo: bool = False) -> str: ...


@parser._add
def division_by_zero(message: str, tb_data: TracebackData) -> CauseInfo: ...


def expression_includes_division_by_zero(expression: Incomplete) -> Incomplete: ...


@parser._add
def integer_division_or_modulo(message: str, tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def zero_negative_power(message: str, _tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def float_modulo(message: str, tb_data: TracebackData) -> CauseInfo: ...


@parser._add
def float_divmod(message: str, _tb_data: TracebackData) -> CauseInfo: ...
