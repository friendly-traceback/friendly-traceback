import builtins
import re
from .. import debug_helper, info_variables
from ..ft_gettext import current_lang
from ..message_parser import get_parser
from ..tb_data import TracebackData
from ..typing_info import CauseInfo, SimilarNamesInfo

parser: RuntimeMessageParser


@parser._add
def local_variable_referenced(message: str, tb_data: TracebackData) -> CauseInfo: ...


def format_similar_names(unknown_name: str, similar: SimilarNamesInfo) -> str: ...
