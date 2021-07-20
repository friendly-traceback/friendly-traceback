import pathlib
import pytest
import friendly_traceback as ft


class CustomPathLike:
    """A simple PEP 519 protocol impl, only for testing ``path_info`` functions."""

    def __fspath__(self):
        return __file__


@pytest.mark.parametrize(
    "file",
    [__file__, pathlib.Path(__file__), CustomPathLike()],
)
def test_is_excluded_file_accepts_any_pathlikes(file):
    assert not ft.path_info.is_excluded_file(file)
