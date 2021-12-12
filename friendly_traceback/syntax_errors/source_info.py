# type: ignore
"""Contains a class that compiles and stores all the information that
is relevant to the analysis of SyntaxErrors.
"""

from .. import debug_helper, token_utils
from ..source_cache import cache
from .syntax_utils import matching_brackets

# During the analysis for finding the cause of the error, we typically examine
# a "bad token" identified by Python as the cause of the error and often
# look at its two neighbours. If the bad token is the first one in a statement
# it does not have a token preceding it; if it is the last one, it does not
# have a token following it. By assigning a meaningless token value to these
# neighbours, the code for the analysis can be greatly simplified as we do
# not have to verify the existence of these neighbours.
MEANINGLESS_TOKEN = token_utils.tokenize(" ")[0]


class Statement:
    """Instances of this class contain all relevant information required
    for the various functions that attempt to determine the cause of
    SyntaxError.

    One main idea is to retrieve a "complete statement" where the
    exception is raised. By "complete statement", we mean the smallest
    number of consecutive lines of code that contains the line where
    the exception was raised and includes matching pairs of brackets,
    (), [], {}. If a problem arises due to non-matching pairs of brackets,
    this information is available (variables begin_brackets or end_bracket).

    A complete statement is saved as a list of tokens (statement_tokens)
    from which it could be reconstructed using an untokenize function.

    From this list of tokens, a secondary list is obtained (tokens) by
    removing all space-like and comment tokens, which are the only
    meaningful tokens needed to do the analysis.

    To simplify the code doing the error analysis itself, we precompute various
    parameters (e.g. does the statement fits on a single line, how many
    meaningful tokens are included, what are the first and last tokens
    on that statement, etc.) which are needed for some functions.
    """

    def __init__(self, value, bad_line):
        # The basic information given by a SyntaxError
        self.filename = value.filename
        self.linenumber = value.lineno
        self.message = value.msg
        self.offset = value.offset

        # Python 3.10 introduced new attributes for 'value'.
        # We already have taken care of assigning some default values
        # to it in core.py.
        self.end_offset = value.end_offset
        self.end_linenumber = value.end_lineno

        if self.end_offset is None or self.offset is None:
            self.highlighted_tokens = None
        elif self.end_offset - self.offset == 1:
            self.highlighted_tokens = None
        else:
            self.highlighted_tokens = []

        # From the traceback, we were previously able ot obtain the line
        # of code identified by Python as being problematic.
        self.bad_line = bad_line  # previously obtained from the traceback
        # skipcq: PTC-W0052
        self.entire_statement = bad_line  # temporary assignment

        # The following will be obtained using offset and bad_line
        self.bad_token = None
        self.bad_token_index = 0
        self.prev_token = None  # meaningful token preceding bad token
        self.next_token = None  # meaningful token following bad token

        # SyntaxError produced inside f-strings occasionally require a special treatment
        self.fstring_error = self.filename == "<fstring>" or "f-string" in self.message

        self.all_statements = []  # useful to determine what lines to include in
        # the contextual display

        # statement_tokens includes all tokens, including newlines, etc., needed
        self.statement_tokens = []  # for proper reconstruction of multiline statements
        self.tokens = []  # meaningful tokens, used for error analysis; see docstring
        self.nb_tokens = 0  # number of meaningful tokens
        self.formatted_partial_source = ""
        self.source_lines = []  # lines of code for the source

        self.statement_brackets = []  # keep track of ([{ anywhere in a statement
        self.begin_brackets = []  # unclosed ([{  before bad token
        self.end_bracket = None  # single unmatched )]}

        self.first_token = None
        self.last_token = None

        # When using the friendly console (repl), SyntaxError might prevent
        # closing all brackets to complete a statement. Knowing this can be
        # useful during the error analysis.
        self.using_friendly_console = False
        if self.filename is not None:
            self.using_friendly_console = self.filename.startswith("<friendly")
        elif not self.exceptional_case():  # pragma: no cover
            debug_helper.log("filename is None in source_info.Statement")
            debug_helper.log("Add this as a new test.")

        self.get_token_info()

    def exceptional_case(self):
        """Returns True if a case that is known to not have all the required information
        available, such as filename or linenumber."""
        return (
            "too many statically nested blocks" in self.message
            or "encoding problem" in self.message
        )

    def get_token_info(self):
        """Obtain all the relevant information about the tokens in
        the file, with particular emphasis on the tokens belonging
        to the statement where the error is located.
        """
        if self.linenumber is not None:
            source_tokens = self.get_source_tokens()
            # self.all_statements and self.statement_tokens are set in the following
            self.obtain_statement(source_tokens)
            self.tokens = self.remove_meaningless_tokens()
            current_statement_index = len(self.all_statements) - 1
            if not self.tokens:
                while current_statement_index > 0:
                    self.statement_tokens = self.all_statements[current_statement_index]
                    current_statement_index -= 1
                    self.tokens = self.remove_meaningless_tokens()
                    if self.tokens:
                        break
                else:
                    self.tokens = [token_utils.tokenize("Internal_error")[0]]

            self.entire_statement = token_utils.untokenize(self.statement_tokens)
            if (
                self.filename.startswith("<friendly-console")
                and self.statement_brackets
                and not self.end_bracket
            ):  # pragma: no cover
                # We got an error flagged before we had the chance to close
                # brackets. Unclosed brackets should not be a problem on their
                # own in a console session - so, we make sure to close
                # the brackets in order to be able to find the true cause
                # of the error
                add_token = ""
                brackets = self.statement_brackets.copy()
                while brackets:
                    bracket = brackets.pop()
                    if bracket == "(":
                        add_token += ")"
                    elif bracket == "[":
                        add_token += "]"
                    else:
                        add_token += "}"

                if self.tokens[0].string in [
                    "class",
                    "def",
                    "if",
                    "elif",
                    "while",
                    "for",
                    "except",
                    "with",
                ]:
                    add_token += ":"

                last_token = self.tokens[-1]
                last_token = last_token.copy()
                last_token.start_row += 1
                last_token.string = last_token.line = add_token
                self.tokens.append(last_token)

        elif not self.exceptional_case():  # pragma: no cover
            debug_helper.log("linenumber is None in source_info.Statement")
            debug_helper.log("Add this as new test case")

        if self.tokens:
            self.assign_individual_token_values()
        elif not self.exceptional_case():  # pragma: no cover
            debug_helper.log("No meaningful tokens in source_info.Statement")

    def get_source_tokens(self):
        """Returns a list containing all the tokens from the source."""
        source = ""
        if "f-string: invalid syntax" in self.message:
            source = self.bad_line
            try:
                exec(self.bad_line)
            except SyntaxError as e:
                self.offset = e.offset
                self.linenumber = 1
        if not source.strip():
            self.source_lines = cache.get_source_lines(self.filename)
            source = "".join(self.source_lines)
            if not source.strip():
                source = self.bad_line or "\n"
        return token_utils.tokenize(source)

    def assign_individual_token_values(self):
        """Assign values of previous and next to bad token and other
        related values.
        """
        self.nb_tokens = len(self.tokens)
        if self.nb_tokens >= 1:
            self.first_token = self.tokens[0]
            self.last_token = self.tokens[-1]

            if self.bad_token is None:
                self.bad_token = self.last_token
                self.bad_token_index = self.nb_tokens - 1
                if self.bad_token_index == 0:
                    self.prev_token = MEANINGLESS_TOKEN
                else:
                    self.prev_token = self.tokens[self.bad_token_index - 1]

            if self.bad_token_index == 0:
                self.prev_token = MEANINGLESS_TOKEN
            elif self.prev_token is None:  # pragma: no cover
                debug_helper.log("This case should be added as new test.")
                self.prev_token = self.tokens[self.bad_token_index - 1]

        if self.last_token != self.bad_token:
            self.next_token = self.tokens[self.bad_token_index + 1]
        else:
            self.next_token = MEANINGLESS_TOKEN

    def format_statement(self):
        """Format the statement identified as causing the problem and possibly
        a couple of preceding statements, showing the line number and token identified.
        """
        # Some errors, like "Too many statistically nested blocs" prevent
        # Python from making a source available.
        if not self.statement_tokens:
            self.formatted_partial_source = ""
            return

        # In some IndentationError cases, and possibly others,
        # Python shows the ^ just before the first token
        # Note that start_row from tokenize and self.offset differ in their origins.
        offset_col = self.tokens[-1].start_col
        if self.offset == offset_col:
            self.offset += 1
            self.end_offset += 1

        lines = self.get_lines_to_show()
        self.annotate_lines(lines)

    def get_lines_to_show(self):
        """Restricts the lines of code to be included when showing the location
        of the error.
        """
        last_linenumber_included = -1
        lines = []
        prev_token = self.all_statements[0][0]
        end_docstring = False
        for statement in self.all_statements:
            # TODO: simplify this to use first and last token to determine if statement
            # should be kept.
            for token in statement:
                current_linenumber = token.start_row
                current_line = token.line.rstrip()
                if lines and prev_token.end_row == current_linenumber:
                    continue
                if self.linenumber < current_linenumber and token == statement[0]:
                    break
                if self.linenumber - current_linenumber < 5:
                    if end_docstring == current_line:
                        end_docstring = False
                        continue
                    if "\n" in current_line:
                        text = current_line.split("\n")  # handle docstring
                        for line in text:
                            lines.append((current_linenumber, line))
                            current_linenumber += 1
                        end_docstring = text[-1]
                        current_linenumber -= 1
                    else:
                        lines.append((current_linenumber, current_line))
                    last_linenumber_included = current_linenumber
                else:
                    if "\n" in current_line:
                        text = current_line.split("\n")
                        end_docstring = text[-1]
                prev_token = token

        if self.linenumber > last_linenumber_included:
            # The problem line was an empty line
            lines.append((last_linenumber_included + 1, ""))
        return lines

    def annotate_lines(self, lines):
        """Adds the caret marks used to show the location of the error"""
        new_lines = []
        nb_digits = len(str(self.linenumber))
        no_mark = "       {:%d}: " % nb_digits
        with_mark = "    -->{:%d}: " % nb_digits
        leading_spaces = " " * (8 + nb_digits)

        self.create_location_markers()

        for i, line in lines:
            if i in self.location_markers:
                num = with_mark.format(i)
                new_lines.append(num + line)
                new_lines.append(leading_spaces + self.location_markers[i])
            else:
                num = no_mark.format(i)
                new_lines.append(num + line)

        self.formatted_partial_source = "\n".join(new_lines)

    def create_location_markers(self):
        # In some cases, the location markers are determined while analysing
        # the statement to find the cause.
        if hasattr(self, "location_markers"):
            return

        # We go with the information obtained by Python.
        nb_carets = 1  # Python default
        if self.end_offset is not None and self.end_offset > self.offset:
            nb_carets = self.end_offset - self.offset
        # However, note that end_offset might not have been set up by
        # cPython but earlier by us to correspond to the default
        # used by Python; if that is the case, it is
        # simply set to 1 more than offset.
        if nb_carets == 1:
            nb_carets = len(self.bad_token.string)
            # In some cases/python version, the end of the token was
            # used to signal the location of the error.
            self.offset = self.bad_token.start_col + 1
        offset_mark = " " * (self.offset) + "^" * nb_carets
        self.location_markers = {self.linenumber: offset_mark}

    def obtain_statement(self, source_tokens):
        """This method scans the source searching for the statement that
        caused the problem. Most often, it will be a single line of code.
        However, it might occasionally be a multiline statement that
        includes code surrounded by some brackets spanning multiple lines.

        It will set the following:

        - self.statement_tokens: a list of all the tokens in the problem statement
        - self.bad_token: the token identified as causing the problem based on offset.
        - self.statement_brackets: a list of open brackets '([{' not yet closed
        - self.begin_brackets: a list of open brackets '([{' in a statement
          before the bad token.
        - self.end_bracket: an unmatched closing bracket ')]}' signaling an error
        - self.all_statements: list of all individual identified statements up to
          and including the problem statement.
        """

        previous_row = -1
        previous_token = None
        continuation_line = False
        # Some tokens cannot occur within brackets; if they are indicated as being
        # the offending token, it might be because we have an unclosed bracket.
        should_begin_statement = [
            "async",
            "await",
            "class",
            "def",
            "return",
            "elif",
            "import",
            "try",
            "except",
            "finally",
            "with",
            "while",
            "yield",
        ]

        for token in source_tokens:
            if (
                token.start_row > self.linenumber
                and not continuation_line
                and not self.statement_brackets
            ):
                break

            # is this a new statement?
            # Valid statements will have matching brackets (), {}, [].
            # A new statement will typically start on a new line and will be
            # preceded by valid statements.

            # An initial version was based on the assumption that any semi-colon
            # would be used correctly and would indicate the end of a statement;
            # however, I am guessing that it more likely indicates
            # a typo, and that the user wanted to write a comma or a colon, so I
            # do not treat them in any special way.
            if token.start_row > previous_row:
                if previous_token is not None:
                    continuation_line = previous_token.line.endswith("\\\n")
                if token.start_row <= self.linenumber and not self.statement_brackets:
                    if self.statement_tokens:
                        self.all_statements.append(self.statement_tokens[:])
                    self.statement_tokens = []
                    self.begin_brackets = []
                previous_row = token.start_row

            self.statement_tokens.append(token)
            # The offset seems to be different depending on Python versions,
            # sometimes matching the beginning of a token, sometimes the end.
            # Furthermore, the end of a token (end_col) might be equal to
            # the beginning of the next (start_col).
            # Additionally, for Python 3.10, multiple tokens can be highlighted
            # if they are on the same line.
            if self.highlighted_tokens:  # not None and not empty list
                if (
                    self.linenumber == token.start_row
                    and self.end_offset is not None
                    and (
                        self.offset < token.end_col < self.end_offset
                        or self.end_offset == 0
                    )
                    and token.string.strip()
                ):
                    self.highlighted_tokens.append(token)
            elif (
                token.start_row == self.linenumber
                and token.start_col <= self.offset <= token.end_col
                and self.bad_token is None
                and token.string.strip()
            ):
                self.bad_token = token
                if self.bad_token.is_comment():
                    self.bad_token = self.prev_token
                if self.highlighted_tokens is not None:
                    self.highlighted_tokens.append(self.bad_token)
            elif (
                token.string.strip()
                and not token.is_comment()
                and self.bad_token is None
            ):
                self.prev_token = token

            previous_token = token

            if (
                self.bad_token in should_begin_statement
                and self.bad_token != self.statement_tokens[0]
                and self.statement_brackets
            ):
                break  # we almost certainly have an unclosed bracket
            # Note: '' in 'any string' == True
            # careful to not accidentally include null strings as brackets
            if not token.string or token.string not in "()[]}{":
                continue

            if token.string in "([{":
                self.statement_brackets.append(token.string)
                if self.bad_token is None or self.bad_token is token:
                    self.begin_brackets.append(token)
            elif token.string in ")]}":
                self.end_bracket = token
                if not self.statement_brackets:
                    break

                open_bracket = self.statement_brackets.pop()
                if not matching_brackets(open_bracket, token.string):
                    self.statement_brackets.append(open_bracket)
                    break
                if self.begin_brackets and self.bad_token is None:
                    self.begin_brackets.pop()
                self.end_bracket = None

        if self.statement_tokens:  # Protecting against EOF while parsing
            last_line = token_utils.untokenize(self.statement_tokens)
            if last_line.strip():
                self.all_statements.append(self.statement_tokens)
            elif self.all_statements:
                self.statement_tokens = self.all_statements[-1]

    def remove_meaningless_tokens(self):
        """Given a list of tokens, remove all space-like tokens and comments;
        also assign the index value of the bad token.
        """
        index = 0
        tokens = []
        for tok in self.statement_tokens:
            if not tok.string.strip() or tok.is_comment():
                continue
            tokens.append(tok)
            if tok is self.bad_token:
                self.bad_token_index = index
            index += 1
        return tokens
