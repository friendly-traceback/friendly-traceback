# type: ignore
"""This file contains various functions used for analysis of SyntaxErrors"""

import unicodedata

from ..ft_gettext import current_lang

_ = current_lang.translate


def matching_brackets(bra, ket):
    return (
        (bra == "(" and ket == ")")
        or (bra == "[" and ket == "]")
        or (bra == "{" and ket == "}")
    )


def name_bracket(bracket):
    names = {
        "(": _("parenthesis `(`"),
        ")": _("parenthesis `)`"),
        "[": _("square bracket `[`"),
        "]": _("square bracket `]`"),
        "{": _("curly bracket `{`"),
        "}": _("curly bracket `}`"),
    }
    return names[str(bracket)]  # bracket could be a Token or a str


# fmt: off
# The following has been taken from https://unicode-table.com/en/sets/quotation-marks/
bad_quotation_marks = [
    "«", "»",
    "‹", "›",
    "„", "“",
    "‟", "”",
    "❝", "❞",
    "❮", "❯",
    "⹂", "〝",
    "〞", "＂",
    "‚", "’", "‛", "‘",
    "❛", "❜",
    "❟",
]
# fmt: on


def identify_bad_quote_char(char, line):
    if char not in bad_quotation_marks:
        return

    char_name = unicodedata.name(char, "unknown")

    hint = _("Did you mean to use a normal quote character, `'` or `\"`?\n")
    cause = _(
        "I suspect that you used a fancy unicode quotation mark\n"
        "whose name is {name}\n"
        "instead of a normal single or double quote for a string."
        "\n"
    ).format(name=char_name)
    count = 0
    for character in line:
        if character in bad_quotation_marks:
            count += 1

    # In the absence of a matching quote, in some cases, perhaps another
    # character was intended.
    if count == 1:
        if char in ["‹", "❮"]:
            cause += _("Or perhaps, you meant to write a less than sign, `<`.\n")
        elif char in ["›", "❯"]:
            cause += _("Or perhaps, you meant to write a greater than sign, `>`.\n")
        elif char in ["‚", "❟"]:
            cause += _("Or perhaps, you meant to write a comma.\n")

    return {"cause": cause, "suggest": hint}


def identify_bad_math_symbol(char, line):
    """Similar to identify_bad_unicode_character except that it is analyzed when
    we see an 'invalid decimal literal' message."""
    if char not in bad_quotation_marks:
        return

    char_name = unicodedata.name(char, "unknown")

    cause = _(
        "I suspect that you used a fancy unicode quotation mark\n"
        "whose name is {name}.\n"
        "\n"
    ).format(name=char_name)
    count = 0
    for character in line:
        if character in bad_quotation_marks:
            count += 1

    # In the absence of a matching quote, in some cases, perhaps another
    # character was intended.
    if count == 1:
        hint = None
        if char in ["‹", "❮"]:
            cause += _("Perhaps, you meant to write a less than sign, `<`.\n")
            hint = _("Did you mean to write a less than sign, `<`?\n")
        elif char in ["›", "❯"]:
            cause += _("Perhaps, you meant to write a greater than sign, `>`.\n")
            hint = _("Did you mean to write a greater than sign, `>`?\n")
        elif char in ["‚", "❟"]:
            cause += _("Perhaps, you meant to write a comma.\n")
            hint = _("Did you mean to write a comma?\n")
        if hint:
            return {"cause": cause, "suggest": hint}

    return {}


def identify_unicode_fraction(char):
    char_name = unicodedata.name(char, "unknown")
    if "FRACTION" not in char_name:
        return
    if char_name == "FRACTION SLASH":
        hint = "Did you mean to use the division operator, `/`?\n"
        cause = _(
            "I suspect that you used the unicode character known as\n"
            "'FRACTION SLASH', which looks similar to\n"
            "but is different from the division operator `/`.\n"
        )
        return {"cause": cause, "suggest": hint}

    hint = _("Did you use a unicode fraction?\n")
    cause = _(
        "I suspect that you used the unicode character `{char}`"
        "meant to represent a fraction.\n"
        "The name of this unicode character is {name}.\n"
    ).format(char=char, name=char_name)

    if not char_name.startswith("VULGAR FRACTION "):
        return {"cause": cause, "suggest": hint}

    short_name = char_name.replace("VULGAR FRACTION ", "")
    num, denom = short_name.split(" ")
    for index, word in enumerate(
        ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"]
    ):
        if num == word:
            num = index
            break
    else:
        return {"cause": cause, "suggest": hint}

    possible_choices = (
        ("HALF", 2),
        ("THIRD", 3),
        ("QUARTER", 4),
        ("FIFTH", 5),
        ("SIXTH", 6),
        ("SEVENTH", 7),
        ("EIGHTH", 8),
        ("NINTH", 9),
        ("TENTH", 10),
    )
    for string, denominator in possible_choices:
        if string in denom:
            break
    else:
        return {"cause": cause, "suggest": hint}

    hint = _("Did you mean `{num}/{denom}`?\n").format(num=num, denom=denominator)
    cause = _(
        "You used the unicode character {char} which is known as\n"
        "{name}\n"
        "I suspect that you meant to write the fraction `{num}/{denom}` instead.\n"
    ).format(num=num, denom=denominator, char=char, name=char_name)
    return {"cause": cause, "suggest": hint}


def highlight_single_token(token):
    """Restrict the highlighting with ^ to a single token.

    This is done to maintain consistency between Python versions.
    """
    return {token.start_row: " " * (token.start_col + 1) + "^" * len(token.string)}


def highlight_two_tokens(first, second, first_marker="^", second_marker="^"):
    """Restrict the highlighting with ^ to two individual tokens.

    This is done to maintain consistency between Python versions.
    """
    if first.start_row == second.start_row:
        mark = (
            " " * (first.start_col + 1)
            + first_marker * len(first.string)
            + " " * (second.start_col - first.end_col)
            + second_marker * len(second.string)
        )
        return {first.start_row: mark}
    mark_1 = " " * (first.start_col + 1) + first_marker * len(first.string)
    mark_2 = " " * (second.start_col + 1) + second_marker * len(second.string)
    return {first.start_row: mark_1, second.start_row: mark_2}


def highlight_range(first, last):
    """Highlight multiple tokens with ^, from first to last."""
    mark = " " * (first.start_col + 1) + "^" * (last.end_col - first.start_col)
    return {first.start_row: mark}
