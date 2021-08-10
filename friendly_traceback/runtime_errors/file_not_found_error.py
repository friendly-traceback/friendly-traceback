import re
from types import FrameType

from ..core import TracebackData
from ..ft_gettext import current_lang
from ..typing import CauseInfo
from ..utils import RuntimeMessageParser

parser = RuntimeMessageParser()


@parser.add
def module_not_found(
    value: OSError, frame: FrameType, tb_data: TracebackData
) -> CauseInfo:
    _ = current_lang.translate
    pattern = re.compile("No module named '(.*)'")
    match = re.search(pattern, str(value))
    if match is None:
        return {}

    filename = match.group(1)
    return {
        "cause": _(
            "In your program, the name of the\n"
            "file that cannot be found is `{filename}`.\n"
        ).format(filename=filename)
    }


@parser.add
def no_such_file_or_directory(
    value: OSError, frame: FrameType, tb_data: TracebackData
) -> CauseInfo:
    _ = current_lang.translate
    pattern = re.compile("No such file or directory: '(.*)'")
    match = re.search(pattern, str(value))
    if match is None:
        return {}

    filename = match.group(1)
    return {
        "cause": _(
            "In your program, the name of the\n"
            "file that cannot be found is `{filename}`.\n"
        ).format(filename=filename)
    }
