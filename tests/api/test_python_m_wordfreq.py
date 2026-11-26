# AC#4: pytest -q passes across tests/test_wordfreq.py (includes python -m wordfreq end-to-end)
# Criterion under test: `python -m wordfreq` run as a subprocess reads stdin, prints TSV,
# and exits 2 with stderr on a missing file.

import subprocess
import sys
from pathlib import Path

import pytest

import wordfreq


@pytest.fixture
def run_wordfreq():
    """Return a helper that runs `python -m wordfreq` as a subprocess."""
    # Run from the directory that contains the `wordfreq` package so the
    # module resolves whether or not the package is installed.
    package_root = Path(wordfreq.__file__).resolve().parent.parent

    def _run(args=(), stdin_text=None):
        return subprocess.run(
            [sys.executable, "-m", "wordfreq", *args],
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=package_root,
        )

    return _run


def test_python_m_wordfreq_stdin_input_prints_tsv_output(run_wordfreq):
    result = run_wordfreq(stdin_text="the quick brown fox the lazy dog the\n")

    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert lines, "expected TSV output on stdout"
    assert all("\t" in line for line in lines)


def test_python_m_wordfreq_missing_file_exits_code_2(run_wordfreq, tmp_path):
    missing = tmp_path / "does_not_exist.txt"

    result = run_wordfreq(args=[str(missing)])

    assert result.returncode == 2


def test_python_m_wordfreq_missing_file_writes_stderr(run_wordfreq, tmp_path):
    missing = tmp_path / "does_not_exist.txt"

    result = run_wordfreq(args=[str(missing)])

    assert result.stderr.strip() != ""
