"""Getting specific information for IndexError"""

import ast
import re
from types import FrameType

import pure_eval

from .. import debug_helper, info_variables, utils
from ..core import TracebackData
from ..ft_gettext import current_lang
from ..typing_info import CauseInfo

parser = utils.RuntimeMessageParser()
_ = current_lang.translate


@parser.add
def object_assignment_out_of_range(
    message: str, frame: FrameType, tb_data: TracebackData
) -> CauseInfo:
    pattern = re.compile(r"(.*) assignment index out of range")
    match = re.search(pattern, message)
    if not match:
        return {}

    obj_type = match.group(1)
    # first, try to identify object
    left_hand_side = tb_data.bad_line.split("=")[0].strip()
    all_objects = info_variables.get_all_objects(left_hand_side, frame)
    for name, sequence in all_objects["name, obj"]:
        truncated = left_hand_side.replace(name, "", 1).strip()
        if truncated.startswith("[") and truncated.endswith("]"):
            break
    else:  # pragma: no cover
        cause = _(
            "You have tried to assign a value to an item of an object\n"
            "of type `{obj_type}` which I cannot identify.\n"
            "The index you gave was not an allowed value.\n"
        ).format(obj_type=obj_type)
        return {"cause": cause}

    index = truncated[1:-1]
    length = len(sequence)

    cause = _(
        "You have tried to assign a value to index `{index}` of `{name}`,\n"
        "{obj_type} of length `{length}`.\n"
    ).format(
        index=index,
        name=name,
        length=length,
        obj_type=info_variables.convert_type(obj_type),
    )

    if length != 0:
        cause += _(
            "The valid index values of `{name}` are integers ranging from\n"
            "`{min}` to `{max}`.\n"
        ).format(name=name, min=-length, max=length - 1)
        if index == length:
            hint = _(
                "Remember: the first item of {obj_type} is not at index 1 but at index 0.\n"
            ).format(obj_type=info_variables.convert_type(obj_type))
            return {"cause": cause, "suggest": hint}
    else:
        hint = _("`{name}` contains no item.\n").format(name=name)
        cause = _(
            "You have tried to assign a value to index `{index}` of `{name}`,\n"
            "{obj_type} which contains no item.\n"
        ).format(index=index, name=name, obj_type=info_variables.convert_type(obj_type))
        return {"cause": cause, "suggest": hint}

    return {"cause": cause}


def cannot_identify_object(obj_type, bad_line):
    message = f"Cannot identify `{obj_type}` object. line: {bad_line}"
    debug_helper.log(message)
    cause = _(
        "You have tried to get an item of an object\n"
        "of type `{obj_type}` which I cannot identify.\n"
        "The index you gave was not an allowed value.\n"
    ).format(obj_type=obj_type)
    return {"cause": cause}


@parser.add
def index_out_of_range(
    message: str, frame: FrameType, tb_data: TracebackData
) -> CauseInfo:
    pattern = re.compile(r"(.*) index out of range")
    match = re.search(pattern, message)
    if not match:
        return {}

    obj_type = match.group(1)
    # first, try to identify object
    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)
    for name, sequence in all_objects["name, obj"]:
        truncated = tb_data.bad_line.replace(name, "", 1).strip()
        if truncated.startswith("[") and truncated.endswith("]"):
            break
    else:  # pragma: no cover
        return cannot_identify_object(obj_type, tb_data.bad_line)

    try:
        node = tb_data.node
    except Exception:  # noqa # pragma: no cover
        return cannot_identify_object(obj_type, tb_data.bad_line)

    if not (node and isinstance(node, ast.Subscript)):  # pragma: no cover
        return cannot_identify_object(obj_type, tb_data.bad_line)

    length = len(sequence)
    evaluator = pure_eval.Evaluator.from_frame(frame)
    # The information that we want may differ for different Python versions
    try:
        index = evaluator[node.slice.value]  # noqa
    except Exception:  # noqa
        try:
            index = evaluator[node.slice]
        except Exception:  # noqa  # pragma: no cover
            debug_helper.log("Unknown index: new case to consider.")
            cause = _(
                "You have tried to get an item from `{name}`,\n"
                "{obj_type} of length `{length}`, by using a value for the index\n"
                "that I cannot determine but which is not allowed.\n"
            ).format(
                name=name, length=length, obj_type=info_variables.convert_type(obj_type)
            )
            return {"cause": cause}

    cause = _(
        "You have tried to get the item with index `{index}` of `{name}`,\n"
        "{obj_type} of length `{length}`.\n"
    ).format(
        index=index,
        name=name,
        length=length,
        obj_type=info_variables.convert_type(obj_type),
    )

    if length != 0:
        cause += _(
            "The valid index values of `{name}` are integers ranging from\n"
            "`{min}` to `{max}`.\n"
        ).format(name=name, min=-length, max=length - 1)
        if index == length:
            hint = _(
                "Remember: the first item of {obj_type} is not at index 1 but at index 0.\n"
            ).format(obj_type=info_variables.convert_type(obj_type))
            return {"cause": cause, "suggest": hint}
    else:
        hint = _("`{name}` contains no item.\n").format(name=name)
        cause = _(
            "You have tried to get the item with index `{index}` of `{name}`,\n"
            "{obj_type} which contains no item.\n"
        ).format(index=index, name=name, obj_type=info_variables.convert_type(obj_type))
        return {"cause": cause, "suggest": hint}

    return {"cause": cause}
