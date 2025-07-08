import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.transform import clean_text, is_duplicate, remove_duplicates
from unittest.mock import patch, mock_open


def test_clean_text_removes_see_more():
    text = "This is a post See more content here"
    result = clean_text(text)
    assert result == "This is a post content here"


def test_clean_text_removes_translation():
    text = "Bonjour · Translated from French"
    result = clean_text(text)
    assert result == "Bonjour"


def test_clean_text_normalizes_spaces():
    text = "Text   with    lots   of   spaces"
    result = clean_text(text)
    assert result == "Text with lots of spaces"


def test_is_duplicate_exact_same():
    assert is_duplicate("Hello world", "Hello world") is True


def test_is_duplicate_with_ui_elements():
    assert is_duplicate("Hello world See more", "Hello world") is True


def test_is_duplicate_different_texts():
    assert is_duplicate("Hello world", "Goodbye world") is False


def test_remove_duplicates_filters_duplicates():
    test_data = [
        {"post_id": "1", "text": "First post", "images": ""},
        {"post_id": "2", "text": "Second post", "images": ""},
        {"post_id": "3", "text": "First post", "images": ""},
    ]

    with patch("builtins.open", mock_open()):
        with patch("csv.DictReader", return_value=test_data):
            with patch("csv.DictWriter") as mock_writer:
                mock_writer_instance = mock_writer.return_value
                remove_duplicates()

                written_rows = mock_writer_instance.writerows.call_args[0][0]
                assert len(written_rows) == 2
