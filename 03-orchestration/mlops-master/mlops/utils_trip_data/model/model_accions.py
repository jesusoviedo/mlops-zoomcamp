import pandas as pd
import numpy as np
from typing import List,Tuple, Dict
from scipy.sparse._csr import csr_matrix
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error

def select_feature_and_target(trip_data: pd.DataFrame, 
categorical_feature: List[str], target: str) -> Tuple[pd.DataFrame, np.ndarray]:
    X = trip_data[categorical_feature]
    y = trip_data[target].values

    return X, y


def feature_engineering(trip_data: pd.DataFrame) -> Tuple[csr_matrix, DictVectorizer]:
    dictVectorizer = DictVectorizer()

    feat_eng_trip_data = trip_data.to_dict(orient='records')
    X = dictVectorizer.fit_transform(feat_eng_trip_data)

    return X, dictVectorizer


def train_predict_model(X: csr_matrix, y: np.ndarray) -> Tuple[np.ndarray, LinearRegression]:
    linearRegression = LinearRegression()
    linearRegression.fit(X, y)

    y_pred = linearRegression.predict(X)

    return y_pred, linearRegression


def metrics_calculate(train: np.ndarray, pred: np.ndarray) -> Dict[str, float]:
    metrics= dict()
    metrics["rmse"] = root_mean_squared_error(train, pred)

    return metrics