"""Tests of custom formatter.
"""

# test_example.py

import os
import subprocess
import sys

import pytest

def run(lang):
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "friendly_traceback",
            "--formatter",
            "tests.fake_formatter.get_cause",
            "tests/name_error.py",
            "--lang",
            lang,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )
    return proc.stderr


def test_formatter_en():
    result = run('en')
    assert "The similar name `pi` was found in the local scope." in result

# The following does not work on Github when running with windows.
# import os
# IN_GITHUB_ACTIONS = bool(os.getenv("GITHUB_ACTIONS"))
# @pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work reliably in Github Actions.")
#
# I am thus the only one to run this test.

@pytest.mark.skipif("Andre" not in __file__, reason="Test does not work reliably in Github Actions.")
def test_formatter_fr():
    result = run('fr')
    assert "Le nom semblable `pi` a été trouvé dans la portée locale." in result
