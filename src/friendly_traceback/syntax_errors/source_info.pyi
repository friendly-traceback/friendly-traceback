from typing import Literal, List, Dict, Any
from _typeshed import Incomplete

from .. import token_utils

MEANINGLESS_TOKEN = token_utils.tokenize(" ")[0]

LINE_NUMBER: Literal["       {:%d}| "] = "       {:%d}| "
MARKED_LINE_NUMBER: Literal["    -->{:%d}| "] = "    -->{:%d}| "
LINE_GAP: Literal["       (...)"] = "       (...)"

class Statement:
    all_statements: List[str]
    bad_line: str
    bad_token: token_utils.Token
    bad_token_comment: token_utils.Token
    bad_token_index: int
    begin_brackets: List
    end_bracket: str
    end_linenumber: int
    end_offset: int
    entire_statement: str
    filename: str
    first_token: token_utils.Token
    formatted_partial_source: str
    fstring_error: Incomplete
    highlighted_tokens: List | None
    last_token: token_utils.Token
    linenumber: int
    location_markers: Dict[str, Any]
    message: str
    nb_tokens: int
    next_token: token_utils.Token
    offset: int
    original_bad_line: str
    prev_token: token_utils.Token
    source_lines: List[str]
    statement_brackets: List
    statement_tokens: List[token_utils.Token]
    tokens: token_utils.Token
    using_friendly_console: bool
    value: SyntaxError

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
