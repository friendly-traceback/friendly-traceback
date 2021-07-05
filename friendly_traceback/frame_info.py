import os

import stack_data
from executing import only
from stack_data import Line
from stack_data.utils import cached_property

from friendly_traceback import token_utils
from . import debug_helper
from .ft_gettext import current_lang


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
        _ = current_lang.translate

        file_not_found = _("Problem: source of `{filename}` is not available\n").format(
            filename=self.filename
        )
        source = line = ""

        if self.lines:
            source, line = self._highlighted_source(with_node_range)
        elif self.filename and os.path.abspath(self.filename):
            if self.filename == "<stdin>":
                pass
                # Using a normal Python REPL - source unavailable.
                # An appropriate error message will have been given via
                # cannot_analyze_stdin
            else:
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

        return {"source": source, "line": line}

    @cached_property
    def highlighted_source(self):
        return self._highlighted_source(with_node_range=False)

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

        # The weird index arithmetic below is based on the information returned
        # by Python's inspect.getinnerframes()
        new_lines = []
        problem_line = ""
        nb_digits = len(str(lines[-1].lineno))
        no_mark = "       {:%d}: " % nb_digits
        with_mark = "    -->{:%d}: " % nb_digits

        text_range_mark = None
        if with_node_range and self.node_info and self.node_info[1]:
            begin, end = self.node_info[1]
            text_range_mark = " " * (8 + nb_digits + begin + 1) + "^" * (end - begin)

        marked = False
        for line_obj in lines:
            if line_obj.is_current:
                num = with_mark.format(line_obj.lineno)
                problem_line = line_obj.text
                new_lines.append(num + problem_line.rstrip())
                if text_range_mark is not None:
                    new_lines.append(text_range_mark)
                marked = True
            elif marked:
                if not line_obj.text.strip():  # do not add empty line if last line
                    break
                num = no_mark.format(line_obj.lineno)
                new_lines.append(num + line_obj.text.rstrip())
            else:
                num = no_mark.format(line_obj.lineno)
                new_lines.append(num + line_obj.text.rstrip())
        return "\n".join(new_lines), problem_line

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
        # If the node spans the entire line, we do not bother to indicate
        # its specific location.
        #
        # Sometimes, a node will span multiple lines. For example,
        # line 22 shown above might have been written as:
        #
        #    print(a[
        #            50], b[0])
        #
        # If that is the case, we rewrite the node as a single line.

        # To start, we transform logical line (or parts thereof) into
        # something that fits on a single physical line.
        # \n could be a valid newline token or a character within
        # a string; we only want to replace newline tokens.
        if not node_text:
            return

        node_range = None
        if "\n" in node_text:
            tokens = token_utils.tokenize(node_text)
            tokens = [tok for tok in tokens if tok != "\n"]
            node_text = "".join(tok.string for tok in tokens)
        bad_line = self.current_line.text
        bad_code = token_utils.strip_comment(bad_line)
        if (
            node_text
            and node_text in bad_line
            and node_text.strip() != bad_code.strip()
        ):
            begin = bad_line.find(node_text)
            end = begin + len(node_text)
            node_range = begin, end
        return node, node_range, node_text

    @cached_property
    def current_line(self):
        return only(
            line for line in self.lines if isinstance(line, Line) and line.is_current
        )
