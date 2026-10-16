import ast
import re
from typing import Dict
import pure_eval
from .. import debug_helper, info_variables
from ..ft_gettext import current_lang
from ..message_parser import get_parser
from ..tb_data import TracebackData
from ..typing_info import CauseInfo

parser: RuntimeMessageParser


@parser._add
def object_assignment_out_of_range(message: str, tb_data: TracebackData) -> CauseInfo: ...


def cannot_identify_object(obj_type: str, bad_line: str) -> Dict: ...


@parser._add
def index_out_of_range(message: str, tb_data: TracebackData) -> CauseInfo: ...
