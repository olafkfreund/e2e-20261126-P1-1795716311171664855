# Criterion (AC#2): format_table formats rows as word\tcount separated by \n
# and returns '' for empty input.
import pytest

from wordfreq.cli import format_table


def test_format_table_single_row_returns_word_tab_count():
    assert format_table([("apple", 3)]) == "apple\t3"


def test_format_table_multiple_rows_joined_by_newline():
    rows = [("apple", 3), ("banana", 2), ("cherry", 1)]
    assert format_table(rows) == "apple\t3\nbanana\t2\ncherry\t1"


@pytest.mark.parametrize(
    "rows,expected",
    [
        ([("the", 10)], "the\t10"),
        ([("a", 1), ("b", 1)], "a\t1\nb\t1"),
        ([("word", 0)], "word\t0"),
    ],
    ids=["single-high-count", "two-equal-counts", "zero-count"],
)
def test_format_table_rows_render_word_tab_count(rows, expected):
    assert format_table(rows) == expected


def test_format_table_empty_input_returns_empty_string():
    assert format_table([]) == ""
