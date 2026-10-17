from typing import Callable

import types
from typing import Any, List, Optional, Tuple, Type, TypedDict
from .. import debug_helper, info_variables, token_utils, utils
from ..ft_gettext import current_lang, no_information, please_report
from ..message_parser import RuntimeMessageParser
from ..tb_data import TracebackData

class CauseInfo(TypedDict, total=False):
    cause: str
    suggest: str

convert_type: Callable[[str], str]
parser: RuntimeMessageParser

@parser._add
def cant_mod_complex_number(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def cant_take_floor_or_mod_of_complex_number(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def unsupported_type_for_divmod(
    message: type[str], _tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def getattr_or_hasattr_attribute_name_must_be_string(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def parse_can_only_concatenate(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def parse_must_be_str(message: type[str], tb_data: TracebackData) -> CauseInfo: ...
@parser._add
def parse_unsupported_operand_type(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def parse_order_comparison(message: type[str], tb_data: TracebackData) -> CauseInfo: ...
@parser._add
def bad_operand_type_for_unary(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def does_not_support_item_assignment(
    message: type[str], _tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def exception_derived_from_base_exception(
    message: type[str], _tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def catch_class_derived_from_base_exception(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def incorrect_nb_positional_arguments(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def missing_positional_arguments(
    message: type[str], _tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def x_is_not_callable(message: type[str], tb_data: TracebackData) -> CauseInfo: ...
def forgot_to_convert_name_to_int(name: str) -> Tuple[str, str]: ...
@parser._add
def cannot_multiply_by_str(message: type[str], tb_data: TracebackData) -> CauseInfo: ...
def find_possible_integers(
    object_of_type: Type[Any], frame: types.FrameType, line: str
) -> List[str]: ...
@parser._add
def object_cannot_be_interpreted_as_an_integer(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def indices_must_be_integers_or_slices(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def slice_indices_must_be_integers_or_none(
    message: type[str], _tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def unhashable_type(message: type[str], _tb_data: TracebackData) -> CauseInfo: ...
@parser._add
def object_is_not_subscriptable(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def argument_of_object_is_not_iterable(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def object_is_not_iterable(
    message: type[str], _tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def cannot_unpack_non_iterable(
    message: type[str], _tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def cannot_convert_dictionary_update_sequence(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def builtin_callable_has_no_len(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def function_has_no_len(message: type[str], tb_data: TracebackData) -> CauseInfo: ...
@parser._add
def vars_arg_must_have_dict(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def function_got_multiple_argument(
    message: type[str], tb_data: TracebackData
) -> CauseInfo: ...
@parser._add
def generator_has_no_len(message: type[str], tb_data: TracebackData) -> CauseInfo: ...
@parser._add
def module_(message: type[str], tb_data: TracebackData) -> CauseInfo: ...
@parser._add
def assigned_to_type_hint(message: type[str], tb_data: TracebackData) -> CauseInfo: ...
