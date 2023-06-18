import pickle

import pandas as pd
from sklearn.pipeline import Pipeline

from .prediction_row import DataRow


class PredictionModel:
    def __init__(self, path: str) -> None:
        with open(path, 'rb') as f:
            self.model: Pipeline = pickle.load(f)

    def predict(self, prediction_row: DataRow) -> str:
        return self.model.predict(
            pd.DataFrame(data=[pd.Series(prediction_row)])
        )[0]
