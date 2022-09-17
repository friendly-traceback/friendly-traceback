import os
import re

from ..ft_gettext import current_lang
from ..message_parser import get_parser
from ..tb_data import TracebackData
from ..typing_info import CauseInfo
from ..utils import get_similar_words

parser = get_parser(FileNotFoundError)
_ = current_lang.translate


@parser._add
def no_such_file_or_directory(
    value: FileNotFoundError, _tb_data: TracebackData
) -> CauseInfo:
    pattern = re.compile("No such file or directory: '(.*)'")
    match = re.search(pattern, str(value))
    if match is None:
        return {}

    filepath = match.group(1)
    dir_, filename = os.path.split(filepath)
    cause = _(
        "In your program, the name of the\n"
        "file that cannot be found is `{filename}`.\n"
    ).format(filename=filename)
    if not dir_:
        dir_ = os.getcwd()
    else:
        if not os.path.isdir(dir_):
            cause += _("{directory}\nis not a valid directory.\n").format(
                directory=dir_
            )
            return {"cause": cause}
    all_files = os.listdir(dir_)
    all_similar = get_similar_words(filename, all_files)
    cause = _(
        "In your program, the name of the\n"
        "file that cannot be found is `{filename}`.\n"
    ).format(filename=filename)
    if dir_:
        cause += _(
            "It was expected to be found in the\n`{directory}` directory.\n"
        ).format(directory=dir_)
    if all_similar:
        hint = _("Did you mean `{similar}`?\n").format(similar=all_similar[0])
        if len(all_similar) == 1:
            cause += _("The file `{similar}` has a similar name.\n").format(
                similar=all_similar[0]
            )
        else:
            cause += (
                _("Perhaps you meant one of the following files with similar names:\n")
                + str(all_similar)[1:-1]
                .replace("'", "`")
                .format(all_similar=all_similar)
                + "\n"
            )
        return {"cause": cause, "suggest": hint}
    return {"cause": cause + _("I have no additional information for you.\n")}
