from typing import Any, Dict, Tuple, Union
from friendly_traceback.base_formatters import InclusionChoice

def check_syntax(
    *,
    source: str | None = None,
    filename: str = "Fake_filename",
    path: str | None = None,
    include: InclusionChoice | None = None,
    lang: str | None = None,
) -> Union[bool, Tuple[Any, str]]: ...
def exec_code(
    *,
    source: str | None = None,
    path: str | None = None,
    include: InclusionChoice | None = None,
    lang: str | None = None,
) -> Dict: ...
