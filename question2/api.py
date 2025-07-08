from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from transformers import pipeline
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = FastAPI()


class Pipeline:
    def __init__(self, category: str, model: str) -> None:
        self._category = category
        self._model = model
        self.pipe = self._get_pipeline()

    def _get_pipeline(self) -> pipeline:
        try:
            logger.debug(f"Setting {self._category} pipeline for model: {self._model} ")
            pipe = pipeline(self._category, model=self._model)
            return pipe
        except Exception as e:
            logging.error(f"Error setting up pipeline: {e}")
            return None


class TextInput(BaseModel):
    text: str


def get_pipe(
    category="sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
) -> pipeline:
    p = Pipeline(category, model)
    return p.pipe


@app.post("/predict")
def predict(input: TextInput, pipeline=Depends(get_pipe)):
    try:
        logger.debug(f"Inferencing for input: {input}...")
        result = pipeline(input.text)[0]
        label = result["label"].lower()
        logger.debug(f"Got Label: {label} for input: {input}")
        return {"sentiment": label}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
