from friendly_traceback.utils import get_single_line_highlighting_ranges as get
from friendly_traceback.utils import create_caret_highlighted as create

def test_round_trip():
    lines = [" ^^ ^^^ ^^",  # start on space, end on ^
             " ^^ ^^^ ^ ",  # start on space, end on space
             "^^ ^^^ ^",    # start on ^, end on ^
             "^^ ^^^ ^  ",]  # start on ^, end on space

    for line in lines:
        assert line == create(get(line))
