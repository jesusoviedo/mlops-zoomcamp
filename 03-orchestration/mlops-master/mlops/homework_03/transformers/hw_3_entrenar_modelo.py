import pandas as pd
from typing import Tuple
from utils_trip_data.model import model_accions
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer


@transformer
def transform(datfra: pd.DataFrame, **kwargs) -> Tuple[DictVectorizer, LinearRegression]:
    X_train, y_train = model_accions.select_feature_and_target(datfra, 
                                                        kwargs['categoricas'].split(","), 
                                                        kwargs['target'])
    
    X_train, dictVectorizer = model_accions.feature_engineering(X_train)
    y_pred, linearRegression = model_accions.train_predict_model(X_train, y_train)
    
    #metrics = model_accions.metrics_calculate(y_train, y_pred)

    #print(f"metrics -> {metrics}")
    print(f"intercept_ -> {linearRegression.intercept_}")

    return dictVectorizer, linearRegression
