# AC#3: returns 2 with non-empty stderr on invalid arguments or missing files.
# Subtask main-invalid-args-exit-2: main returns 2 with non-empty stderr for
# invalid --top/--min-len, unknown flags, and missing files.

import pytest

from wordfreq.cli import main


@pytest.mark.parametrize(
    "argv",
    [
        ["--top", "abc"],
        ["--top", "-5"],
        ["--min-len", "abc"],
        ["--min-len", "-1"],
    ],
    ids=[
        "top-non-integer",
        "top-negative",
        "min-len-non-integer",
        "min-len-negative",
    ],
)
def test_main_invalid_numeric_option_returns_exit_2(argv, capsys):
    exit_code = main(argv)

    assert exit_code == 2


@pytest.mark.parametrize(
    "argv",
    [
        ["--top", "abc"],
        ["--top", "-5"],
        ["--min-len", "abc"],
        ["--min-len", "-1"],
    ],
    ids=[
        "top-non-integer",
        "top-negative",
        "min-len-non-integer",
        "min-len-negative",
    ],
)
def test_main_invalid_numeric_option_writes_stderr(argv, capsys):
    main(argv)

    captured = capsys.readouterr()

    assert captured.err != ""


def test_main_unknown_flag_returns_exit_2(capsys):
    exit_code = main(["--no-such-flag"])

    assert exit_code == 2


def test_main_unknown_flag_writes_stderr(capsys):
    main(["--no-such-flag"])

    captured = capsys.readouterr()

    assert captured.err != ""


def test_main_missing_file_returns_exit_2(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"

    exit_code = main([str(missing)])

    assert exit_code == 2


def test_main_missing_file_writes_stderr(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"

    main([str(missing)])

    captured = capsys.readouterr()

    assert captured.err != ""
