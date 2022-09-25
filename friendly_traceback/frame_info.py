import os
from typing import Iterable

import stack_data
from executing import only
from stack_data import LINE_GAP, BlankLineRange, BlankLines, Formatter, Line, Options
from stack_data.utils import cached_property

from friendly_traceback import token_utils

from . import debug_helper
from .ft_gettext import current_lang
from .source_cache import cache

_ = current_lang.translate


class FriendlyFormatter(Formatter):
    def __init__(
        self,
        **kwargs,
    ):
        self.indent = "    "
        super().__init__(**kwargs)

    def format_frame_source(self, frame: stack_data.FrameInfo) -> Iterable[str]:
        for line in frame.lines:
            if isinstance(line, Line):
                yield self.format_line(line)
            elif isinstance(line, BlankLineRange):
                yield self.format_blank_lines_linenumbers(line)
            else:
                assert line is LINE_GAP
                yield self.indent + self.line_gap_string + "\n"

    def format_line(self, line: Line) -> str:
        result = self.indent
        if line.is_current:
            result += self.current_line_indicator
        else:
            result += " " * len(self.current_line_indicator)
        result += self.line_number_format_string.format(line.lineno)
        prefix = result
        result += line.render() + "\n"

        for line_range in line.executing_node_ranges:
            start = line_range.start - line.leading_indent
            end = line_range.end - line.leading_indent
            # if end <= start, we have an empty line inside a highlighted
            # block of code. In this case, we need to avoid inserting
            # an extra blank line with no markers present.
            if end > start:
                result += (
                    " " * (start + len(prefix))
                    + self.executing_node_underline * (end - start)
                    + "\n"
                )
        return result

    def format_blank_lines_linenumbers(self, blank_line):
        result = self.indent + " " * len(self.current_line_indicator)
        if blank_line.begin_lineno == blank_line.end_lineno:
            return (
                result
                + self.line_number_format_string.format(blank_line.begin_lineno)
                + "\n"
            )
        return result + "{}\n".format(self.line_number_gap_string)


class FrameInfo(stack_data.FrameInfo):
    @cached_property
    def partial_source(self):
        return self._partial_source(with_node_range=False)

    @cached_property
    def partial_source_with_node_range(self):
        return self._partial_source(with_node_range=True)

    def _partial_source(self, with_node_range: bool):
        """Gets the part of the source where an exception occurred,
        formatted in a pre-determined way, as well as the content
        of the specific line where the exception occurred.
        """
        file_not_found = _("Problem: source of `{filename}` is not available\n").format(
            filename=self.filename
        )
        source = ""

        if not self.lines and self.filename:
            # protecting against https://github.com/alexmojaki/stack_data/issues/13
            try:
                lineno = self.lineno
                s_lines = cache.get_source_lines(self.filename)
                self.lines = []  # noqa
                with_node_range = False
                linenumber = max(lineno - 2, 0)
                for line in s_lines[linenumber : lineno + 1]:
                    self.lines.append(FakeLineObject(line, linenumber, lineno))
                    linenumber += 1
            except Exception as e:  # noqa
                debug_helper.log_error(e)

        if self.lines:
            source = self._highlighted_source(with_node_range)
        elif self.filename and os.path.abspath(self.filename):
            if self.filename not in ["<stdin>", "<string>"]:
                # When filename is "<stdin>", "<string>",
                # using a normal Python REPL - source unavailable.
                # An appropriate error message will have been given via
                # cannot_analyze_stdin
                source = file_not_found
                debug_helper.log("Problem in get_partial_source().")
                debug_helper.log(file_not_found)
        elif not self.filename:  # pragma: no cover
            source = file_not_found
            debug_helper.log("Problem in get_partial_source().")
            debug_helper.log(file_not_found)
        else:  # pragma: no cover
            debug_helper.log("Problem in get_partial_source().")
            debug_helper.log("Should not have reached this option")
            debug_helper.log_error()

        if not source.endswith("\n"):
            source += "\n"

        return source

    @cached_property
    def highlighted_source(self):
        return self._highlighted_source(with_node_range=False)

    def problem_line(self):
        if not self.lines:
            return ""
        for line_obj in self.lines:
            if line_obj is stack_data.LINE_GAP:
                continue
            elif isinstance(line_obj, stack_data.BlankLineRange):
                continue
            elif line_obj.is_current:
                return str(line_obj.text)
        return ""

    def _highlighted_source(self, with_node_range: bool):
        """Extracts a few relevant lines from a file content given as a list
        of lines, adding line number information and identifying
        a particular line.

        When dealing with a ``SyntaxError`` or its subclasses, offset is an
        integer normally used by Python to indicate the position of
        the error with a ``^``, like::

            if True
                  ^

        which, in this case, points to a missing colon. We use the same
        representation in this case.
        """
        lines = self.lines

        if not lines:
            return "", ""

        nb_digits = len(str(lines[-1].lineno))
        lineno_fmt_string = "{:%d}| " % nb_digits  # noqa
        line_gap_string = " " * nb_digits + "(...)"
        line_number_gap_string = " " * (nb_digits - 1) + ":"

        try:
            new_lines = [
                line
                for line in FriendlyFormatter(
                    options=Options(blank_lines=BlankLines.SINGLE),
                    line_number_format_string=lineno_fmt_string,
                    line_gap_string=line_gap_string,
                    line_number_gap_string=line_number_gap_string,
                ).format_frame_source(self)
            ]

            return "".join(new_lines)
        except Exception:
            return "<NO SOURCE>"

    @cached_property
    def node_info(self):
        """Finds the 'node', that is the exact part of a line of code
        that is related to the cause of the problem.
        """
        try:
            ex = self.executing
            node = ex.node
            node_text = ex.text()
        except Exception as e:  # pragma: no cover
            debug_helper.log("Exception raised in TracebackData.use_executing.")
            debug_helper.log(str(e))
            return
        # If we can find the precise location (node) on a line of code
        # causing the exception, we note this location
        # so that we can indicate it later with ^^^^^, something like:
        #
        #    20:     b = tuple(range(50))
        #    21:     try:
        # -->22:         print(a[50], b[0])
        #                      ^^^^^
        #    23:     except Exception as e:
        #
        # Sometimes, a node will span multiple lines. For example,
        # line 22 shown above might have been written as:
        #
        #    print(a[
        #            50], b[0])
        #
        # If that is the case, we rewrite the node as a single line.
        special_case = False
        if not node_text:
            node_text = self.handle_special_cases()
            special_case = True
            if not node_text:
                # Highlight the entire line
                try:
                    tokens = token_utils.tokenize(self.current_line.text)
                    tokens = token_utils.remove_meaningless_tokens(tokens)
                    return (
                        None,
                        (tokens[0].start_col, tokens[-1].end_col),
                        self.current_line.text,
                    )
                except Exception:
                    return None

        node_range = None
        bad_line = self.current_line.text
        if node_text and node_text in bad_line:
            begin = bad_line.find(node_text)
            end = begin + len(node_text)
            node_range = begin, end
        if special_case:  # use the entire bad_line to determine the cause
            # use node_range to highlight.
            return node, node_range, bad_line
        return node, node_range, node_text

    @cached_property
    def current_line(self):
        return only(
            line for line in self.lines if isinstance(line, Line) and line.is_current
        )

    def handle_special_cases(self):
        """Hack to try to identify a problematic text when node_text is None.

        We just use the information to highlight where in a statement
        the error is located.
        """
        try:
            exec(self.current_line.text)
        except Exception as exc:
            saved_exc = exc
        else:
            return ""

        if not hasattr(saved_exc, "msg"):
            return ""
        message = saved_exc.msg
        if message.startswith("cannot import name '"):
            return message.split("'")[1]
        elif message.startswith("No module named '"):
            return message.split("'")[1]

        return ""


class FakeLineObject:
    """Class reproducing the minimum attributes for formatting lines"""

    def __init__(self, line, linenumber, lineno):
        self.text = line
        self.lineno = linenumber + 1
        self.is_current = linenumber == lineno - 1

    def __repr__(self):
        return f"lineno: {self.lineno}; current: {self.is_current}; {self.text}"
