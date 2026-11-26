# AC#1: count_words extracts tokens, lowercases, preserves case, filters by min_len,
# and sorts by (-count, word).
import pytest

from wordfreq.cli import count_words


def test_count_words_extracts_alphanumeric_tokens_only():
    text = "Hello, world! 123 abc_def"
    result = count_words(text)
    words = sorted(word for word, _ in result)
    assert words == sorted(["hello", "world", "123", "abc", "def"])


def test_count_words_lowercases_by_default():
    result = count_words("Apple APPLE apple")
    assert list(result) == [("apple", 3)]


def test_count_words_preserves_case_when_ignore_case_false():
    result = count_words("Apple APPLE apple", ignore_case=False)
    assert sorted(result) == sorted([("Apple", 1), ("APPLE", 1), ("apple", 1)])


@pytest.mark.parametrize(
    "min_len,expected_words",
    [
        (1, {"a", "bb", "ccc"}),
        (2, {"bb", "ccc"}),
        (3, {"ccc"}),
    ],
    ids=["min_len_1_keeps_all", "min_len_2_drops_single_char", "min_len_3_keeps_only_three_chars"],
)
def test_count_words_filters_by_min_len(min_len, expected_words):
    result = count_words("a bb ccc", min_len=min_len)
    assert {word for word, _ in result} == expected_words


def test_count_words_sorts_by_count_descending_then_word_ascending():
    result = count_words("b a b c a b")
    assert list(result) == [("b", 3), ("a", 2), ("c", 1)]


def test_count_words_ties_sorted_alphabetically_by_word():
    result = count_words("zebra apple mango")
    assert list(result) == [("apple", 1), ("mango", 1), ("zebra", 1)]
