from typing import Literal
from _typeshed import Incomplete

from .. import debug_helper, token_utils
from ..source_cache import cache
from .syntax_utils import matching_brackets

MEANINGLESS_TOKEN = token_utils.tokenize(" ")[0]

LINE_NUMBER: Literal["       {:%d}| "] = "       {:%d}| "
MARKED_LINE_NUMBER: Literal["    -->{:%d}| "] = "    -->{:%d}| "
LINE_GAP: Literal["       (...)"] = "       (...)"

class Statement:
    all_statements: Incomplete
    bad_line: Incomplete
    bad_token: Incomplete
    bad_token_comment: Incomplete
    bad_token_index: int
    begin_brackets: Incomplete
    end_bracket: Incomplete
    end_linenumber: Incomplete
    end_offset: Incomplete
    entire_statement: Incomplete
    filename: Incomplete
    first_token: Incomplete
    formatted_partial_source: str
    fstring_error: Incomplete
    highlighted_tokens: Incomplete
    last_token: Incomplete
    linenumber: Incomplete
    location_markers: Incomplete
    message: Incomplete
    nb_tokens: int
    next_token: Incomplete
    offset: Incomplete
    original_bad_line: Incomplete
    prev_token: Incomplete
    source_lines: Incomplete
    statement_brackets: Incomplete
    statement_tokens: Incomplete
    tokens: Incomplete
    using_friendly_console: Incomplete
    value: Incomplete

    def __init__(
        self, value: Incomplete, bad_line: Incomplete, original_bad_line: Incomplete
    ) -> None: ...
    def exceptional_case(self) -> Incomplete: ...
    def get_token_info(self) -> Incomplete: ...
    def get_source_tokens(self) -> Incomplete: ...
    def assign_individual_token_values(self) -> Incomplete: ...
    def format_statement(self) -> Incomplete: ...
    def get_lines_to_show(self) -> Incomplete: ...
    def annotate_lines(self, lines: Incomplete) -> Incomplete: ...
    def create_location_markers(self) -> Incomplete: ...
    def obtain_statement(self, source_tokens: Incomplete) -> Incomplete: ...
    def remove_meaningless_tokens(self) -> Incomplete: ...

def get_lines_from_statement(
    tokens: Incomplete, linenumber: Incomplete, prev_token: Incomplete
) -> Incomplete: ...
