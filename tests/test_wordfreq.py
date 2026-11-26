"""Unit and CLI tests for the wordfreq package."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from wordfreq.cli import count_words, format_table, main

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_count_words_basic_ranking() -> None:
    text = "Apple banana apple, cherry! Banana apple."
    assert count_words(text) == [("apple", 3), ("banana", 2), ("cherry", 1)]


def test_format_table_tsv() -> None:
    assert format_table([("apple", 3), ("banana", 2)]) == "apple\t3\nbanana\t2"


def test_cli_top_and_min_len(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("to be or not to be that is the question", encoding="utf-8")
    rc = main([str(sample), "--min-len", "3", "--top", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().splitlines() == ["not\t1", "question\t1"]


# --- count_words: tie-breaking and case handling -------------------------------


def test_count_words_ties_broken_alphabetically() -> None:
    assert count_words("b a c a b c") == [("a", 2), ("b", 2), ("c", 2)]


def test_count_words_higher_count_beats_alphabetical_order() -> None:
    assert count_words("dog cat dog cat bird") == [("cat", 2), ("dog", 2), ("bird", 1)]


def test_count_words_lowercases_by_default() -> None:
    assert count_words("Hello HELLO hello") == [("hello", 3)]


def test_count_words_ignore_case_false_preserves_case() -> None:
    assert count_words("Hello HELLO hello", ignore_case=False) == [
        ("HELLO", 1),
        ("Hello", 1),
        ("hello", 1),
    ]


def test_count_words_ignore_case_false_counts_exact_matches() -> None:
    assert count_words("Apple apple APPLE apple", ignore_case=False) == [
        ("apple", 2),
        ("APPLE", 1),
        ("Apple", 1),
    ]


# --- count_words: tokenisation, filtering and slicing --------------------------


def test_count_words_token_pattern_is_ascii_alphanumeric() -> None:
    # Underscores, hyphens, apostrophes and non-ASCII letters all split tokens.
    counts = dict(count_words("snake_case-word don't 2024 naïve"))
    assert counts == {
        "2024": 1,
        "case": 1,
        "don": 1,
        "na": 1,
        "snake": 1,
        "t": 1,
        "ve": 1,
        "word": 1,
    }


def test_count_words_min_len_filters_short_words() -> None:
    assert count_words("a bb ccc a bb", min_len=2) == [("bb", 2), ("ccc", 1)]


def test_count_words_top_limits_results() -> None:
    text = "one two two three three three"
    assert count_words(text, top=1) == [("three", 3)]
    assert count_words(text, top=2) == [("three", 3), ("two", 2)]


def test_count_words_top_zero_returns_empty() -> None:
    assert count_words("one two", top=0) == []


def test_count_words_top_none_returns_all() -> None:
    assert count_words("one two three", top=None) == [
        ("one", 1),
        ("three", 1),
        ("two", 1),
    ]


def test_count_words_empty_text_returns_empty() -> None:
    assert count_words("") == []
    assert count_words("!!! ... ???") == []


# --- count_words: argument validation ------------------------------------------


@pytest.mark.parametrize("min_len", [0, -1])
def test_count_words_rejects_min_len_below_one(min_len: int) -> None:
    with pytest.raises(ValueError, match="min_len must be >= 1"):
        count_words("text", min_len=min_len)


def test_count_words_rejects_negative_top() -> None:
    with pytest.raises(ValueError, match="top must be >= 0"):
        count_words("text", top=-1)


# --- format_table ---------------------------------------------------------------


def test_format_table_empty_returns_empty_string() -> None:
    assert format_table([]) == ""


# --- main: stdin input and output formats --------------------------------------


def test_cli_defaults_to_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("b a a\n"))
    assert main([]) == 0
    assert capsys.readouterr().out == "a\t2\nb\t1\n"


def test_cli_dash_path_reads_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("b a a\n"))
    assert main(["-"]) == 0
    assert capsys.readouterr().out == "a\t2\nb\t1\n"


def test_cli_lowercases_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("Apple apple APPLE apple"))
    assert main([]) == 0
    assert capsys.readouterr().out == "apple\t4\n"


def test_cli_case_sensitive_preserves_case(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("Apple apple APPLE apple"))
    assert main(["--case-sensitive"]) == 0
    assert capsys.readouterr().out == "apple\t2\nAPPLE\t1\nApple\t1\n"


def test_cli_tsv_ends_with_single_newline(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("one two\n"))
    assert main([]) == 0
    out = capsys.readouterr().out
    assert out == "one\t1\ntwo\t1\n"
    assert out.endswith("\n")
    assert not out.endswith("\n\n")


def test_cli_empty_tsv_prints_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("!!! ???"))
    assert main([]) == 0
    assert capsys.readouterr().out == ""


def test_cli_top_zero_tsv_prints_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("one two"))
    assert main(["--top", "0"]) == 0
    assert capsys.readouterr().out == ""


def test_cli_json_output_ends_with_newline(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("b a a"))
    assert main(["--json"]) == 0
    out = capsys.readouterr().out
    assert out.endswith("\n")
    assert not out.endswith("\n\n")
    assert json.loads(out) == [{"word": "a", "count": 2}, {"word": "b", "count": 1}]


def test_cli_json_empty_input_prints_empty_array(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    assert main(["--json"]) == 0
    assert capsys.readouterr().out == "[]\n"


def test_cli_json_honours_top_and_min_len(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("a bb bb ccc ccc ccc"))
    assert main(["--json", "--min-len", "2", "--top", "1"]) == 0
    assert json.loads(capsys.readouterr().out) == [{"word": "ccc", "count": 3}]


# --- main: argument validation and file errors ---------------------------------


def test_cli_rejects_min_len_below_one(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--min-len", "0"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--min-len must be >= 1" in captured.err


def test_cli_rejects_negative_top(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--top", "-1"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--top must be >= 0" in captured.err


def test_cli_rejects_non_integer_top(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--top", "abc"]) == 2
    assert capsys.readouterr().err != ""


def test_cli_rejects_unknown_flag(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--no-such-flag"]) == 2
    assert capsys.readouterr().err != ""


def test_cli_missing_file_returns_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "does-not-exist.txt"
    assert main([str(missing)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""


def test_cli_undecodable_file_returns_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.txt"
    bad.write_bytes(b"\xff\xfe\xfd")
    assert main([str(bad)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""


# --- python -m wordfreq ----------------------------------------------------------


def _run_module(*args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "wordfreq", *args],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )


def test_python_m_wordfreq_reads_stdin() -> None:
    result = _run_module(stdin="b a a\n")
    assert result.returncode == 0
    assert result.stdout == "a\t2\nb\t1\n"


def test_python_m_wordfreq_json_output() -> None:
    result = _run_module("--json", stdin="b a a\n")
    assert result.returncode == 0
    assert result.stdout.endswith("\n")
    assert json.loads(result.stdout) == [
        {"word": "a", "count": 2},
        {"word": "b", "count": 1},
    ]


def test_python_m_wordfreq_missing_file_exits_2(tmp_path: Path) -> None:
    result = _run_module(str(tmp_path / "missing.txt"))
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr != ""
