from typing import Tuple

import pandas as pd

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error

@transformer
def transform(df: pd.DataFrame, **kwargs) -> Tuple[DictVectorizer, LinearRegression]:
    # una funcion que seleccionar caracteristicas y target
    categorical = ['PULocationID', 'DOLocationID']
    target = 'duration'
    y_train = df[target].values

    # una funcion que trabaja con el vectorizador
    train_dicts = df[categorical].to_dict(orient='records')
    dictVectorizer = DictVectorizer()
    X_train = dictVectorizer.fit_transform(train_dicts)    

    # una funcion que trabaja con el modelo
    linearRegression = LinearRegression()
    linearRegression.fit(X_train, y_train)

    y_pred = linearRegression.predict(X_train)
    rmse = root_mean_squared_error(y_train, y_pred)

    print(f"rmse {rmse}")
    print(f"intercept_ {linearRegression.intercept_}")

    return dictVectorizer, linearRegression
