from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

sentiment_pipeline = pipeline("sentiment-analysis")


class TextInput(BaseModel):
    text: str


@app.post("/predict")
def predict(input: TextInput):
    try:
        result = sentiment_pipeline(input.text)[0]
        label = result["label"].lower()
        return {"sentiment": label}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
