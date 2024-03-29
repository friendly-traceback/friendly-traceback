# type: ignore
"""analyze_syntax.py

Collection of functions useful attempting to determine the
cause of a SyntaxError and providing a somewhat detailed explanation.

In an ideal world, one would write a custom parser for Python, extending
the existing one with enhanced error messages about where in the parsing
process a SyntaxError occurred, what kind of token was expected, etc.,
and use that information to give feedback to users.

Unfortunately, we do not live in such a world.

Friendly-traceback uses some ad-hoc heuristics to analyze the information
given by Python or the code itself and makes an attempt at guessing
as often as possible what went wrong while trying to avoid giving
incorrect information.
"""

from friendly_traceback.ft_gettext import current_lang, internal_error, unknown_case

from .. import debug_helper
from . import message_analyzer, statement_analyzer

_ = current_lang.translate


def unknown_cause():
    return _(
        "Currently, I cannot guess the likely cause of this error.\n"
        "Try to examine closely the line indicated as well as the line\n"
        "immediately above to see if you can identify some misspelled\n"
        "word, or missing symbols, like (, ), [, ], :, etc.\n"
        "\n"
        "Unless your code uses type annotations, which are beyond our scope,\n"
        "if you think that this is something which should be handled\n"
        "by friendly, please report this case to\n"
        "https://github.com/friendly-traceback/friendly-traceback/issues\n"
        "\n"
    )


def set_cause_syntax(value, tb_data):
    """Gets the likely cause of a given exception based on some information
    specific to a given exception.
    """
    try:
        return find_syntax_error_cause(value, tb_data)
    except Exception as e:  # pragma: no cover
        debug_helper.log_error(e)
        return {"cause": internal_error(e)}


def find_syntax_error_cause(value, tb_data):
    """Attempts to find the cause of a SyntaxError"""
    message = value.msg
    statement = tb_data.statement

    # If Python includes a descriptive enough message, we rely
    # on the information that it provides. We know that sometimes
    # this might give the wrong diagnostic but one of our objectives
    # is to explain in simpler language what Python means when it
    # raises a particular exception.

    if "invalid syntax" not in message:
        cause = message_analyzer.analyze_message(message, statement)
        if cause:
            return cause

        cause = statement_analyzer.analyze_statement(statement)
        if message == "expected ':'":  # Python 3.10:
            new_cause = _(
                "Python told us that it expected a colon at the position indicated.\n"
                "However, adding a colon or replacing something else by a colon\n"
                "would not fix the problem.\n"
            )
            if cause:
                cause["cause"] = new_cause + cause["cause"]
            else:
                cause = {"cause": new_cause}
            return cause

        if not cause:  # pragma: no cover
            return {"cause": unknown_cause(), "suggest": unknown_case()}

        notice = _(  # pragma: no cover
            "Python gave us the following informative message\n"
            "about the possible cause of the error:\n\n"
            "    {message}\n\n"
            "However, I do not recognize this information and I have\n"
            "to guess what caused the problem, but I might be wrong.\n\n"
        ).format(message=message)
        debug_helper.log("This message is not known: " + message)
        filename = statement.filename
        if "\\tests\\" in filename:
            filename = "tests" + filename.split("tests")[1]
        debug_helper.log(f"   file: {filename}")
        cause["cause"] = notice + cause["cause"]  # pragma: no cover
        return cause  # pragma: no cover

    cause = statement_analyzer.analyze_statement(statement)
    if cause:
        return cause

    return {"cause": unknown_cause(), "suggest": unknown_case()}
