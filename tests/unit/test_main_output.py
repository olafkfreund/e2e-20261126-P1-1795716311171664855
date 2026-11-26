# AC#3: main reads stdin by default (or with '-'), honors --case-sensitive,
# --top, --min-len and --json, ends non-empty TSV/JSON output with a newline
# (nothing is printed for empty TSV), and returns 0.

import io
import json
import sys

import pytest

from wordfreq.cli import main


@pytest.fixture
def feed_stdin(monkeypatch):
    def _feed(text):
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))

    return _feed


SAMPLE_TEXT = "the cat and the dog and the bird\n"


def test_main_default_args_reads_stdin_returns_zero(feed_stdin, capsys):
    feed_stdin(SAMPLE_TEXT)
    assert main([]) == 0


def test_main_dash_argument_reads_stdin_returns_zero(feed_stdin, capsys):
    feed_stdin(SAMPLE_TEXT)
    assert main(["-"]) == 0


def test_main_default_args_reads_stdin_produces_output(feed_stdin, capsys):
    feed_stdin(SAMPLE_TEXT)
    main([])
    assert capsys.readouterr().out != ""


def test_main_tsv_output_ends_with_newline(feed_stdin, capsys):
    feed_stdin(SAMPLE_TEXT)
    main([])
    assert capsys.readouterr().out.endswith("\n")


def test_main_json_output_ends_with_newline(feed_stdin, capsys):
    feed_stdin(SAMPLE_TEXT)
    main(["--json"])
    assert capsys.readouterr().out.endswith("\n")


def test_main_json_output_is_valid_json(feed_stdin, capsys):
    feed_stdin(SAMPLE_TEXT)
    main(["--json"])
    parsed = json.loads(capsys.readouterr().out)
    assert parsed is not None


def test_main_empty_tsv_output_prints_nothing(feed_stdin, capsys):
    feed_stdin("")
    main([])
    assert capsys.readouterr().out == ""


def test_main_empty_tsv_output_returns_zero(feed_stdin, capsys):
    feed_stdin("")
    assert main([]) == 0


def test_main_empty_json_output_ends_with_newline(feed_stdin, capsys):
    feed_stdin("")
    main(["--json"])
    assert capsys.readouterr().out.endswith("\n")


def test_main_case_sensitive_keeps_differently_cased_words_separate(feed_stdin, capsys):
    feed_stdin("The the THE\n")
    main(["--case-sensitive"])
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.strip()]
    assert len(lines) == 3


def test_main_default_case_folds_differently_cased_words(feed_stdin, capsys):
    feed_stdin("The the THE\n")
    main([])
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.strip()]
    assert len(lines) == 1


def test_main_top_limits_tsv_output_to_one_line(feed_stdin, capsys):
    feed_stdin(SAMPLE_TEXT)
    main(["--top", "1"])
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.strip()]
    assert len(lines) == 1


def test_main_top_limits_tsv_output_to_two_lines(feed_stdin, capsys):
    feed_stdin(SAMPLE_TEXT)
    main(["--top", "2"])
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.strip()]
    assert len(lines) == 2


def test_main_top_first_line_is_most_frequent_word(feed_stdin, capsys):
    feed_stdin(SAMPLE_TEXT)
    main(["--top", "1"])
    first_line = capsys.readouterr().out.splitlines()[0]
    assert first_line.startswith("the")


def test_main_min_len_excludes_shorter_words(feed_stdin, capsys):
    feed_stdin(SAMPLE_TEXT)
    main(["--min-len", "4"])
    words = [ln.split("\t")[0] for ln in capsys.readouterr().out.splitlines() if ln.strip()]
    assert all(len(w) >= 4 for w in words)


def test_main_min_len_keeps_words_at_threshold(feed_stdin, capsys):
    feed_stdin(SAMPLE_TEXT)
    main(["--min-len", "4"])
    words = [ln.split("\t")[0] for ln in capsys.readouterr().out.splitlines() if ln.strip()]
    assert "bird" in words


def test_main_json_honors_top_option(feed_stdin, capsys):
    feed_stdin(SAMPLE_TEXT)
    main(["--json", "--top", "1"])
    parsed = json.loads(capsys.readouterr().out)
    assert len(parsed) == 1
