import pandas as pd
from utils_trip_data.prepare_data import data_transformation

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer


@transformer
def read_dataframe(datfra:pd.DataFrame, **kwargs) -> pd.DataFrame:

    datfra = data_transformation.create_target_duration(datfra)
    datfra = data_transformation.clean_data(datfra, kwargs['categoricas'].split(","))
    
    print(f"rows -> {datfra.shape[0]}")

    return datfra