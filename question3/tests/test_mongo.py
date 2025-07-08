import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import tempfile
from unittest.mock import Mock, patch
from src.load_to_db import MongoLoader


def test_mongo_loader_init():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        pd.DataFrame(
            {"post_id": ["123"], "text": ["test"], "images": ["img.jpg"]}
        ).to_csv(f.name, index=False)

        with patch("src.load_to_db.MongoClient"):
            loader = MongoLoader("test_collection", f.name)
            assert loader._collection_name == "test_collection"
            assert len(loader._df) == 1


def test_transform_row_to_post_model():
    with patch("src.load_to_db.MongoClient"):
        loader = MongoLoader("test", "dummy.csv")
        row = {"post_id": "123", "text": "test", "images": "img.jpg"}
        result = loader._transform_row_to_post_model(row)
        assert result["post_id"] == "123"


def test_load_row_to_db_success():
    mock_collection = Mock()
    with patch("src.load_to_db.MongoClient"):
        loader = MongoLoader("test", "dummy.csv")
        loader._collection = mock_collection

        row = {"post_id": "123", "text": "test", "images": "img.jpg"}
        loader._load_row_to_db(row)
        mock_collection.insert_one.assert_called_once()


def test_load_row_to_db_exception():
    mock_collection = Mock()
    mock_collection.insert_one.side_effect = Exception("Insert failed")

    with patch("src.load_to_db.MongoClient"):
        with patch("src.load_to_db.logger"):
            loader = MongoLoader("test", "dummy.csv")
            loader._collection = mock_collection

            row = {"post_id": "123", "text": "test", "images": "img.jpg"}
            loader._load_row_to_db(row)


def test_load_calls_insert_for_each_row():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        pd.DataFrame(
            {"post_id": ["1", "2"], "text": ["test1", "test2"], "images": ["", ""]}
        ).to_csv(f.name, index=False)

        mock_collection = Mock()
        with patch("src.load_to_db.MongoClient"):
            loader = MongoLoader("test", f.name)
            loader._collection = mock_collection
            loader.load()

            assert mock_collection.insert_one.call_count == 2
