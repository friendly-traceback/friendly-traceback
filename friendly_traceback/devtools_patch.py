"""Python devtools (https://github.com/samuelcolvin/python-devtools)
is a great debugging aid. However, it is restricted to be called
within a function at a precise frame depth.

I have filed an issue [1] hoping that this could be made adjustable.
In the meantime, this is meant as a workaround.

Note that devtools is not a required dependency; trying to import this
module can result in an ImportError.
"""
import sys
from types import FrameType
from typing import Optional

from devtools.debug import Debug, DebugOutput


class PatchedDebug(Debug):
    def __init__(
        self,
        *,
        additional_frame_depth: int = 0,
        warnings: "Optional[bool]" = None,
        highlight: "Optional[bool]" = None
    ):
        self.additional_frame_depth = additional_frame_depth
        super().__init__(warnings=warnings, highlight=highlight)

    def _process(self, args, kwargs) -> DebugOutput:
        """
        BEWARE: this must be called from a function exactly 2 levels below the top of the stack.
        """
        # HELP: any errors other than ValueError from _getframe? If so please submit an issue
        try:
            call_frame: "FrameType" = sys._getframe(2 + self.additional_frame_depth)
        except ValueError:
            # "If [ValueError] is deeper than the call stack, ValueError is raised"
            return self.output_class(
                filename="<unknown>",
                lineno=0,
                frame="",
                arguments=list(self._args_inspection_failed(args, kwargs)),
                warning=self._show_warnings
                and "error parsing code, call stack too shallow",
            )

        function = call_frame.f_code.co_name

        from pathlib import Path

        path = Path(call_frame.f_code.co_filename)
        if path.is_absolute():
            # make the path relative
            cwd = Path(".").resolve()
            try:
                path = path.relative_to(cwd)
            except ValueError:
                # happens if filename path is not within CWD
                pass

        lineno = call_frame.f_lineno
        warning = None

        import executing

        source = executing.Source.for_frame(call_frame)
        if not source.text:
            warning = "no code context for debug call, code inspection impossible"
            arguments = list(self._args_inspection_failed(args, kwargs))
        else:
            ex = source.executing(call_frame)
            function = ex.code_qualname()
            if not ex.node:
                warning = "executing failed to find the calling node"
                arguments = list(self._args_inspection_failed(args, kwargs))
            else:
                arguments = list(self._process_args(ex, args, kwargs))

        return self.output_class(
            filename=str(path),
            lineno=lineno,
            frame=function,
            arguments=arguments,
            warning=self._show_warnings and warning,
        )
