# Acceptance criterion AC#1: count_words raises ValueError('min_len must be >= 1')
# for min_len < 1 and ValueError('top must be >= 0') for top < 0; count_words
# honors top slicing (returns at most `top` entries).

import pytest

from wordfreq.cli import count_words


SAMPLE_TEXT = "the cat and the dog and the bird"


@pytest.mark.parametrize(
    "min_len",
    [0, -1, -5],
    ids=["min_len_zero", "min_len_minus_one", "min_len_minus_five"],
)
def test_count_words_min_len_below_one_raises_value_error(min_len):
    with pytest.raises(ValueError) as excinfo:
        count_words(SAMPLE_TEXT, min_len=min_len)
    assert str(excinfo.value) == "min_len must be >= 1"


@pytest.mark.parametrize(
    "top",
    [-1, -10],
    ids=["top_minus_one", "top_minus_ten"],
)
def test_count_words_top_negative_raises_value_error(top):
    with pytest.raises(ValueError) as excinfo:
        count_words(SAMPLE_TEXT, top=top)
    assert str(excinfo.value) == "top must be >= 0"


def test_count_words_min_len_one_does_not_raise():
    result = count_words(SAMPLE_TEXT, min_len=1)
    assert result is not None


def test_count_words_top_zero_does_not_raise():
    result = count_words(SAMPLE_TEXT, top=0)
    assert result is not None


def test_count_words_top_limits_result_length():
    result = count_words(SAMPLE_TEXT, top=2)
    assert len(result) == 2


def test_count_words_top_larger_than_vocabulary_returns_all_distinct_words():
    result = count_words("alpha beta gamma", top=10)
    assert len(result) == 3
