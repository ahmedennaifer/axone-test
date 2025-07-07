from pymongo import MongoClient
import logging

from typing import TypedDict
import pandas as pd


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Post(TypedDict):
    post_id: str
    text: str
    images: str


class MongoLoader:
    def __init__(self, collection_name: str, path: str) -> None:
        self._collection_name = collection_name
        self._path = path
        self._client = MongoClient("mongodb://axone:axone@localhost:27017/")
        self._db = self._get_db()
        self._collection = self._get_collection()
        self._df: pd.DataFrame = self._get_df()  # pyright: ignore

    def _get_df(self) -> pd.DataFrame | None:
        try:
            df = pd.read_csv(self._path)
            return df
        except FileNotFoundError as e:
            logger.error(f"Error reading the df: {e}")

    def _get_db(self, name: str = "test") -> "db":  # pyright: ignore
        try:
            logger.debug("setting up db...")
            db = self._client[name]
            logger.info("Retrieved db succcessfully")
            return db
        except Exception as e:
            logger.error(f"Error retrieving the db: {e}")

    def _get_collection(self) -> "collection":  # pyright: ignore
        try:
            logger.debug("Getting collection...")
            collection = self._db[self._collection_name]
            logger.info("Retrieved db succcessfully")
            return collection
        except Exception as e:
            logger.error(f"Error retrieving the db: {e}")

    def _transform_row_to_post_model(self, row) -> Post:
        return Post(post_id=row["post_id"], text=row["text"], images=row["images"])

    def _load_row_to_db(self, row) -> None:
        post = self._transform_row_to_post_model(row)
        try:
            self._collection.insert_one(post)
            logger.info(f"inserted {post['post_id']} in the db")
        except Exception as e:
            logger.error(f"Error writing to db: {e}")

    def load(self):
        logger.info("Starting loading...")
        for _, row in self._df.iterrows():
            try:
                logger.debug("Inserting row..")
                self._load_row_to_db(row)
            except Exception as e:
                logger.error(f"Error laoding from iter: {e}")


if __name__ == "__main__":
    ml = MongoLoader("test", "data/clean.csv")
    ml.load()
