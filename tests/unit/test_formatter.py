"""Tests of custom formatter.
"""

# test_example.py

import os
import subprocess
import sys

import pytest

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


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


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work reliably in Github Actions.")
def test_formatter_fr():
    # There appears to be some encoding-related issues when running this on Github
    result = run('fr')
    assert "Le nom semblable `pi` a été trouvé dans la portée locale." in result
