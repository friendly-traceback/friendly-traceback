"""Getting specific information for AttributeError"""
import ast
import builtins
import re
import sys
from types import FrameType
from typing import Any, Iterable, List, Optional, Sequence

from .. import console_helpers, debug_helper, info_variables, utils
from ..ft_gettext import current_lang, please_report
from ..message_parser import get_parser
from ..path_info import path_utils
from ..tb_data import TracebackData
from ..typing_info import CauseInfo
from ..utils import get_similar_words, list_to_string
from . import stdlib_modules

parser = get_parser(AttributeError)
_ = current_lang.translate


@parser._add
def circular_import(message: str, _tb_data: TracebackData) -> CauseInfo:
    pattern = re.compile(r"partially initialized module '(.*)' has")
    match = re.search(pattern, message)
    if not match:
        return {}
    module = match.group(1)

    if module in stdlib_modules.names:
        hint = _("Did you give your program the same name as a Python module?\n")
        cause = _(
            "I suspect that you used the name `{module}.py` for your program\n"
            "and that you also wanted to import a module with the same name\n"
            "from Python's standard library.\n"
            "If so, you should use a different name for your program.\n"
        ).format(module=module)
        return {"cause": cause, "suggest": hint}

    if "circular import" in message:
        hint = _("You have a circular import.\n")
    else:  # pragma: no cover
        # I thought a version did not include the mention of circular import.
        debug_helper.log("New case to consider for circular_import.")
        hint = _("You likely have a circular import.\n")
    cause = _("Python indicated that the module `{module}` was not fully imported.\n")
    cause += _(
        "This can occur if, during the execution of the code in module `{module}`\n"
        "an attempt is made to import the same module again.\n"
    ).format(module=module)
    return {"cause": cause, "suggest": hint}


# ======= Attribute error in module =========


@parser._add
def attribute_error_in_module(message: str, tb_data: TracebackData) -> CauseInfo:
    """Attempts to find if a module attribute or module name might have been misspelled"""
    pattern = re.compile(r"module '(.*)' has no attribute '(.*)'")
    match = re.search(pattern, message)
    if not match:
        return {}
    module = match.group(1)
    attribute = match.group(2)
    frame = tb_data.exception_frame

    try:
        mod = sys.modules[module]
    except Exception:  # noqa
        cause = _(
            "This should not happen:\n"
            "Python tells us that module `{module}` does not have an "
            "attribute named `{attribute}`.\n"
            "However, it does not appear that module `{module}` was imported.\n"
        ).format(module=module, attribute=attribute)
        if module in stdlib_modules.names:
            hint = _("Did you give your program the same name as a Python module?\n")
            cause += _(
                "I suspect that you used the name `{module}.py` for your program\n"
                "and that you also wanted to import a module with the same name\n"
                "from Python's standard library.\n"
                "If so, you should use a different name for your program.\n"
            ).format(module=module)
            return {"cause": cause, "suggest": hint}
        else:
            cause = hint = _("You likely have a circular import.\n")
            cause += _(
                "This can occur if, during the execution of the code in module `{module}`\n"
                "an attempt is made to import the same module again.\n"
            ).format(module=module)
        return {"cause": cause, "suggest": hint}

    similar_attributes = get_similar_words(attribute, dir(mod))
    if similar_attributes:
        if len(similar_attributes) == 1:
            hint = _("Did you mean `{name}`?\n").format(name=similar_attributes[0])
            cause = _(
                "Perhaps you meant to write `{module}.{correct}` "
                "instead of `{module}.{typo}`\n"
            ).format(correct=similar_attributes[0], typo=attribute, module=module)
            return {"cause": cause, "suggest": hint}

        names = list_to_string(similar_attributes)
        hint = _("Did you mean `{name}`?\n").format(name=similar_attributes[0])
        cause = _(
            "Instead of writing `{module}.{typo}`, perhaps you meant to write one of \n"
            "the following names which are attributes of module `{module}`:\n"
            "`{names}`\n"
        ).format(names=names, typo=attribute, module=module)
        return {"cause": cause, "suggest": hint}

    if module in stdlib_modules.names and hasattr(mod, "__file__"):
        mod_path = path_utils.shorten_path(mod.__file__)
        if not mod_path.startswith("PYTHON_LIB:"):
            hint = _("Did you give your program the same name as a Python module?\n")
            cause = _(
                "You imported a module named `{module}` from `{mod_path}`.\n"
                "There is also a module named `{module}` in Python's standard library.\n"
                "Perhaps you need to rename your module.\n"
            ).format(module=module, mod_path=mod_path)
            return {"cause": cause, "suggest": hint}

    imported_modules = []
    for mod_name in sys.modules:
        if mod_name in frame.f_locals:
            imported_modules.append((mod_name, frame.f_locals[mod_name]))
        elif mod_name in frame.f_globals:
            imported_modules.append((mod_name, frame.f_globals[mod_name]))

    possible_modules = [
        mod_name for mod_name, mod in imported_modules if attribute in dir(mod)
    ]

    if possible_modules:
        if len(possible_modules) == 1:
            mod_name = possible_modules[0]
            hint = _("Did you mean `{name}`?\n").format(name=mod_name)
            cause = _(
                "Perhaps you meant to use the attribute `{attribute}` of \n"
                "module `{mod_name}` instead of module `{module}`.\n"
            ).format(attribute=attribute, mod_name=mod_name, module=module)
            return {"cause": cause, "suggest": hint}

        hint = _("Did you mean one of the following modules: `{names}`?").format(
            names=list_to_string(possible_modules)
        )
        cause = _(
            "Instead of the module `{module}`, perhaps you wanted to use\n"
            "the attribute `{attribute}` of one of the following modules:\n"
            "`{names}`.\n"
        ).format(
            attribute=attribute, module=module, names=list_to_string(possible_modules)
        )
        return {"cause": cause, "suggest": hint}

    cause = _(
        "Python tells us that no object with name `{attribute}` is\n"
        "found in module `{module}`.\n"
    ).format(attribute=attribute, module=module)
    return {"cause": cause}


@parser._add
def type_object_has_no_attribute(message: str, tb_data: TracebackData) -> CauseInfo:
    """Attempts to find if a module attribute or module name might have been misspelled"""
    pattern = re.compile(r"type object '(.*)' has no attribute '(.*)'")
    match = re.search(pattern, message)
    if not match:
        return {}
    frame = tb_data.exception_frame

    return _attribute_error_in_object(match.group(1), match.group(2), tb_data, frame)


@parser._add
def attribute_error_in_object(message: str, tb_data: TracebackData) -> CauseInfo:
    pattern = re.compile(r"'(.*)' object has no attribute '(.*)'")
    match = re.search(pattern, message)
    if not match:
        return {}
    frame = tb_data.exception_frame

    if match.group(1) == "NoneType":
        return {
            "cause": _(
                "You are attempting to access the attribute `{attr}`\n"
                "for a variable whose value is `None`."
            ).format(attr=match.group(2))
        }

    return _attribute_error_in_object(match.group(1), match.group(2), tb_data, frame)


@parser._add
def object_attribute_is_read_only(message: str, tb_data: TracebackData) -> CauseInfo:
    pattern = r"'(.*)' object attribute '(.*)' is read-only"
    match = re.search(pattern, message)
    if match is None:
        return {}
    obj_type = match.group(1)
    attribute = match.group(2)
    frame = tb_data.exception_frame

    obj = info_variables.get_object_from_name(obj_type, frame)
    if not hasattr(obj, "__slots__"):
        cause = _(
            "The value of attribute `{attribute}` of objects of type `{obj_type}`\n"
            "cannot be changed.\n"
            "I have no further information.\n"
        ).format(attribute=attribute, obj_type=obj_type)
        return {"cause": cause}

    slots = getattr(obj, "__slots__")
    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    for obj_name, instance in all_objects:
        try:
            if isinstance(instance, obj) or instance == obj:
                break
        except Exception:  # noqa
            continue
    else:
        obj_name = obj_type

    if len(slots) == 0:
        cause = _(
            "Object `{name}` uses an empty `__slots__` to prevent the modification\n"
            "of any of its attributes.\n"
        ).format(name=obj_name, attribute=attribute)
        return {"cause": cause}

    cause = _(
        "Object `{name}` uses `__slots__` to specify which attributes can\n"
        "be changed. The value of attribute `{name}.{attribute}` cannot be changed.\n"
    ).format(name=obj_name, attribute=attribute)
    if len(slots) == 1:
        cause += (
            "The only attribute of `{name}` whose value can be changed is"
            "`{attribute}`.\n"
        ).format(name=obj_name, attribute=slots[0])
    elif len(slots) < 10:
        cause += (
            "The only attributes of `{name}` whose value can be changed are:\n"
            "`{attributes}`.\n"
        ).format(name=obj_name, attributes=utils.list_to_string(slots))
    return {"cause": cause}


def _attribute_error_in_object(
    obj_type: str, attribute: str, tb_data: TracebackData, frame: FrameType
) -> CauseInfo:
    """Attempts to find if object attribute might have been misspelled"""
    if obj_type == "builtin_function_or_method":
        obj_name = tb_data.bad_line.replace("." + attribute, "")
        # Confirm we have the right one
        if obj_name in dir(builtins):
            cause = _(
                "`{obj_name}` is a function. Perhaps you meant to write\n"
                "`{obj_name}({attribute})`\n"
            ).format(obj_name=obj_name, attribute=attribute)
            hint = _("Did you mean `{obj_name}({attribute})`?\n").format(
                obj_name=obj_name, attribute=attribute
            )
            return {"cause": cause, "suggest": hint}

        cause = _(
            "`{obj_name}` is a Python built-in function or method\n"
            "which does not have an attribute named `{attribute}.`\n"
        ).format(obj_name=obj_name, attribute=attribute)
        return {"cause": cause}

    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    obj = info_variables.get_object_from_name(obj_type, frame)

    if obj is None:  # object could be an instance of obj_type
        # this is to fix issue #212
        for obj_name, _obj in all_objects:
            t = str(type(_obj))
            if (
                t.endswith(f".{obj_type}'>") or t.endswith(f"'{obj_type}'>")
            ) and not hasattr(_obj, attribute):
                instance = _obj
                break
        else:
            cause = _(
                "An object of type `{obj_type}` has no attribute named `{attr}`.\n"
                "Unfortunately I cannot find such an object on the line where\n"
                "the problem occurs.\n"
            ).format(obj_type=obj_type, attr=attribute)
            return {"cause": cause + please_report()}
    else:
        for obj_name, instance in all_objects:
            try:
                if isinstance(instance, obj) or instance == obj:
                    break
            except TypeError:
                pass
        else:
            possible_objects = []
            for obj_name, _obj in all_objects:
                t = str(type(_obj))
                if (
                    (t.endswith(f".{obj_type}'>") or t.endswith(f"'{obj_type}'>"))
                    and not hasattr(_obj, attribute)
                ) or (
                    obj_name == "Friendly"
                    and isinstance(_obj, console_helpers.FriendlyHelpers)
                ):
                    possible_objects.append((obj_name, _obj))

            if not possible_objects:
                debug_helper.log(f"bad_line= {tb_data.bad_line}")
                cause = _(
                    "An object of type `{obj_type}` has no attribute named `{attr}`.\n\n"
                    "I cannot give additional information:\n"
                    "I found one object of this type in the current scope\n"
                    "but it does not appear to be the object causing the problem.\n"
                ).format(obj_type=obj_type, attr=attribute)
                return {"cause": cause + please_report()}
            elif len(possible_objects) > 1:
                names = ", ".join(name for name, _obj in possible_objects)
                cause = _(
                    "An object of type `{obj_type}` has no attribute named `{attr}`.\n\n"
                    "The following objects might be the cause of the problem: \n"
                    "{names}.\n"
                ).format(obj_type=obj_type, attr=attribute, names=names)
                return {"cause": cause}

            obj_name, instance = possible_objects[0]

    possible_cause = tuple_by_accident(instance, obj_name, attribute)
    if possible_cause:
        return possible_cause

    known_attributes = dir(instance)

    # Example: this.len -> len(this)
    known_builtin = perhaps_builtin(attribute, known_attributes)
    if known_builtin:
        return use_builtin_function(obj_name, attribute, known_builtin)

    if attribute == "join":
        join = perhaps_join(obj)
        if join:
            return use_str_join(obj_name, tb_data)

    # Example: both "this" and "that" are known objects
    # this.that -> this, that
    if attribute in frame.f_globals or attribute in frame.f_locals:
        return missing_comma(obj_name, attribute)

    known_synonyms = perhaps_synonym(attribute, known_attributes)
    if known_synonyms:
        return use_synonym(obj_name, attribute, known_synonyms)

    # noqa Example: list.apend -> list.append
    similar = get_similar_words(attribute, known_attributes)
    if similar:
        return handle_attribute_typo(obj_name, attribute, similar)

    # We have not been able to find a useful suggestion
    cause = _("The object `{obj}` has no attribute named `{attr}`.\n").format(
        obj=obj_name, attr=attribute
    )
    if hasattr(obj, "__slots__"):
        cause += _(
            "Note that object `{obj}` uses `__slots__` which prevents\n"
            "the creation of new attributes.\n"
        ).format(obj=obj_name)
    known_attributes = [a for a in known_attributes if "__" not in a]
    if len(known_attributes) > 10:
        known_attributes = known_attributes[:9] + ["..."]
    if known_attributes:
        cause += _(
            "The following are some of its known attributes:\n`{names}`."
        ).format(names=", ".join(known_attributes))
    return {"cause": cause}


def handle_attribute_typo(
    obj_name: str, attribute: str, similar: Sequence[str]
) -> CauseInfo:
    """Takes care of misspelling of existing attribute of object whose
    name could be identified.
    """
    cause = _("The object `{obj_name}` has no attribute named `{attribute}`.\n").format(
        obj_name=obj_name, attribute=attribute
    )
    if len(similar) == 1:
        hint = _("Did you mean `{name}`?\n").format(name=similar[0])
        cause += _(
            "Perhaps you meant to write `{obj}.{correct}` "
            "instead of `{obj}.{typo}`\n"
        ).format(correct=similar[0], typo=attribute, obj=obj_name)
    else:
        names = list_to_string(similar)
        hint = _("Did you mean one of the following: `{names}`?\n").format(names=names)
        cause += _(
            "Instead of writing `{obj}.{typo}`, perhaps you meant to write one of \n"
            "the following names which are attributes of object `{obj}`:\n"
            "`{names}`\n"
        ).format(names=names, typo=attribute, obj=obj_name)
    return {"cause": cause, "suggest": hint}


def perhaps_builtin(attribute: str, known_attributes: Iterable[str]) -> Optional[str]:
    if attribute in ["min", "max", "sorted", "reversed", "sum"]:
        return attribute
    elif (
        attribute in ["len", "length", "lenght", "size"]  # noqa
        and "__len__" in known_attributes
    ):
        return "len"
    return None


def tuple_by_accident(obj: Any, obj_name: str, attribute: str) -> CauseInfo:
    if not (isinstance(obj, tuple) and len(obj) == 1):
        return {}

    true_obj = obj[0]
    if hasattr(true_obj, attribute):
        hint = _("Did you write a comma by mistake?\n")
        cause = _(
            "`{obj_name}` is a tuple that contains a single item\n"
            "which does have `'{attribute}'` as an attribute.\n"
            "Perhaps you added a trailing comma by mistake at the end of the line\n"
            "where you defined `{obj_name}`.\n"
        ).format(obj_name=obj_name, attribute=attribute)
        return {"cause": cause, "suggest": hint}

    return {}


def use_str_join(obj_name: str, tb_data: TracebackData) -> CauseInfo:
    str_content = repr("...")
    hint = _("Did you mean `{str_content}.join({obj_name})`?\n")
    cause = _(
        "The object `{obj_name}` has no attribute named `join`.\n"
        "Perhaps you wanted something like `{str_content}.join({obj_name})`.\n"
    )
    parts = tb_data.original_bad_line.split(tb_data.bad_line)
    if len(parts) >= 2 and parts[1].strip().startswith("("):
        index = parts[1].find(")")
        if index != -1:
            content = parts[1][1:index].strip()
            try:
                content = ast.literal_eval(content)
            except Exception:  # noqa
                content = None  # type: ignore
            if isinstance(content, str):
                str_content = repr(content)
    hint = hint.format(obj_name=obj_name, str_content=str_content)
    cause = cause.format(obj_name=obj_name, str_content=str_content)
    return {"cause": cause, "suggest": hint}


def use_builtin_function(
    obj_name: str, attribute: str, known_builtin: str
) -> CauseInfo:
    hint = _("Did you mean `{known_builtin}({obj_name})`?\n").format(
        known_builtin=known_builtin, obj_name=obj_name
    )
    cause = _(
        "The object `{obj_name}` has no attribute named `{attribute}`.\n"
        "Perhaps you can use the Python builtin function `{known_builtin}` instead:\n"
        "`{known_builtin}({obj_name})`."
    ).format(known_builtin=known_builtin, obj_name=obj_name, attribute=attribute)
    return {"cause": cause, "suggest": hint}


def perhaps_join(obj: Any) -> bool:
    if hasattr(obj, "__iter__") or (
        hasattr(obj, "__getitem__") and hasattr(obj, "__len__")
    ):
        return True
    return False


def perhaps_synonym(
    attribute: str, known_attributes: Iterable[str]
) -> Optional[List[str]]:
    synonyms = [
        ["add", "append", "extend", "insert", "push", "update", "union"],
        ["remove", "discard", "pop"],
    ]
    for syn_list in synonyms:
        if attribute in syn_list:
            return [attr for attr in syn_list if attr in known_attributes]
    return None


def use_synonym(obj_name: str, attribute: str, synonyms: Sequence[str]) -> CauseInfo:
    hint = _("Did you mean `{attr}`?\n").format(attr=synonyms[0])
    cause = _("The object `{name}` has no attribute named `{attribute}`.\n").format(
        name=obj_name, attribute=attribute
    )
    if len(synonyms) == 1:
        cause += _(
            "However, `{attr}` is an attribute of `{name}` with a similar meaning.\n"
        ).format(name=obj_name, attr=synonyms[0])
    else:
        cause += _(
            "However, `{name}` has the following attributes with similar meanings:\n"
            "`{attributes}`.\n"
        ).format(name=obj_name, attributes=list_to_string(synonyms))

    return {"cause": cause, "suggest": hint}


def missing_comma(first: str, second: str) -> CauseInfo:
    hint = _("Did you mean to separate object names by a comma?\n")

    cause = _(
        "`{second}` is not an attribute of `{first}`.\n"
        "However, both `{first}` and `{second}` are known objects.\n"
        "Perhaps you wrote a period to separate these two objects, \n"
        "instead of using a comma.\n"
    ).format(first=first, second=second)

    return {"cause": cause, "suggest": hint}
