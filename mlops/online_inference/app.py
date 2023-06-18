from typing import Dict

from fastapi import FastAPI
from src.constants import MODEL_PATH
from src.prediction_model import PredictionModel
from src.prediction_row import DataRow

app = FastAPI()
model = PredictionModel(MODEL_PATH)


@app.post('/predict')
def post_prediction(data_model: DataRow) -> Dict[str, str]:
    return {'prediction': model.predict(data_model.dict())}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8090)
