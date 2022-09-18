import re

from .. import info_variables, token_utils
from ..ft_gettext import current_lang
from ..message_parser import get_parser
from ..tb_data import TracebackData  # for type checking only
from ..typing_info import CauseInfo  # for type checking only

parser = get_parser(RuntimeError)
_ = current_lang.translate


@parser._add
def container_changed_size_during_iteration(
    message: str, tb_data: TracebackData
) -> CauseInfo:
    pattern = re.compile(r"(.*) changed size during iteration")
    match = re.search(pattern, message)
    if not match:
        return {}
    container_name = match.group(1).lower()
    frame = tb_data.exception_frame
    if container_name.startswith("dict"):
        container_name = "dict"
        obj_type = dict
    elif container_name == "set":
        obj_type = set
    else:
        return {}
    container_type = info_variables.convert_type(container_name)

    objects = info_variables.get_all_objects(tb_data.bad_line, frame)
    names = []
    for name, obj in objects["name, obj"]:
        if isinstance(obj, obj_type):
            names.append(name)

    tokens = token_utils.tokenize(tb_data.bad_line)
    loop_keywords = []
    for tok in tokens:
        if tok.string in {"for", "while"}:
            loop_keywords.append(tok.string)

    loop_keywords = set(loop_keywords)
    if len(loop_keywords) == 1:
        for_while = "for" if "for" in loop_keywords else "while"
    else:
        for_while = "for/while"

    if len(names) == 1:
        cause = _(
            "While you were iterating over the items of `{name}` ({container_type})\n"
            "in a `{for_while}` loop, you either tried to add or remove items from it.\n"
            "Suggestion: start by making a copy of `{name}` and iterate over the items\n"
            "of that copy if you want to change `{name}` inside a loop.\n"
            "You might want to do this as follows:\n\n"
            "    my_{name} = {name}.copy()\n"
            "    for item in my_{name}:\n"
            "        # Change {name}\n"
        ).format(name=names[0], container_type=container_type, for_while=for_while)
    else:
        cause = _(
            "While you were iterating over the items of a container ({container_type})\n"
            "in a `{for_while}` loop, you either tried to add or remove items from it.\n"
            "Suggestion: start by making a copy of the container and iterate over the items\n"
            "of that copy if you want to change that container inside a loop.\n"
        ).format(container_type=container_type, for_while=for_while)

    return {"cause": cause}
