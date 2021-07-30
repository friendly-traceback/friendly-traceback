"""This file contains various functions used for analysis of SyntaxErrors"""

from ..ft_gettext import current_lang


def matching_brackets(bra, ket):
    return (
        (bra == "(" and ket == ")")
        or (bra == "[" and ket == "]")
        or (bra == "{" and ket == "}")
    )


def name_bracket(bracket):
    _ = current_lang.translate
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
    _ = current_lang.translate
    if char not in bad_quotation_marks:
        return

    hint = _("Did you mean to use a normal quote character, `'` or `\"`?\n")
    cause = _(
        "I suspect that you used a fancy unicode quotation mark\n"
        "instead of a normal single or double quote for a string."
        "\n"
    )
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
