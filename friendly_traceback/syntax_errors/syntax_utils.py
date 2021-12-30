# type: ignore
"""This file contains various functions used for analysis of SyntaxErrors"""

import unicodedata

from .. import debug_helper, token_utils
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


def get_previous_token_before_marker(bad_token, tokens, token_after):
    first = bad_token
    brackets = []
    prev = first
    found_first = False
    for tok in tokens:
        if tok == bad_token:
            found_first = True
        if not found_first:
            continue
        if tok.string in "([{":
            brackets.append(tok.string)
        elif tok.string in ")]}":
            if not brackets:
                return first, None  # should not happen; unmatched bracket
            bra = brackets.pop()
            if not matching_brackets(bra, tok.string):
                return first, None  # should not happen; unmatched bracket
        elif not brackets and tok == token_after:
            return first, prev
        if (
            tok.start_row != first.start_row or tok.is_comment()
        ):  # statement continue on next line
            if not brackets:
                debug_helper.log("get_previous_token_before_marker:")
                debug_helper.log("line continues but not open bracket found.")
                ket = "|"
            else:
                bra = brackets.pop()
                for ket in ")]}":
                    if matching_brackets(bra, ket):
                        break
            return first, (prev, ket)
        prev = tok

    return first, None


def highlight_before_token(bad_token, tokens, token_after):
    first, last = get_previous_token_before_marker(bad_token, tokens, token_after)
    if last is None:
        return {first.start_row: " " * (first.start_col + 1) + "^" * len(first.string)}
    elif isinstance(last, tuple):  # statement continue on next line
        last = last[0]
        marker = highlight_range(first, last)
        mark = marker[first.start_row]
        mark = mark[:-1] + "^-->"
        return {first.start_row: mark}

    return highlight_range(first, last)


def get_expression_before_token(bad_token, tokens, token_after):
    first, last = get_previous_token_before_marker(bad_token, tokens, token_after)
    if last is None:
        return None
    statement_continue = False
    if isinstance(last, tuple):  # statement continue on next line
        last, ket = last
        statement_continue = True
    new_tokens = []
    found_bad = False
    for tok in tokens:
        if tok == bad_token:
            found_bad = True
        if not found_bad:
            clone = tok.copy()
            clone.string = ""
            new_tokens.append(clone)
            continue
        if tok is last:  # == would only compare string values
            if statement_continue:
                tok = tok.copy()
                tok.string += "..." + ket
            new_tokens.append(tok)
            break
        new_tokens.append(tok)
    return token_utils.untokenize(new_tokens).strip()
