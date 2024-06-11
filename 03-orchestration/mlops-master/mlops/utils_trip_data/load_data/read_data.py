import requests
import pandas as pd
from typing import List
from io import BytesIO


def read(anho:int , mes_ini:int, mes_fin_excluyendo:int) -> pd.DataFrame:

    dfs: List[pd.DataFrame] = []

    for year, months in [(anho, (mes_ini, mes_fin_excluyendo))]:
        for i in range(*months):
            host = "https://d37ci6vzurychx.cloudfront.net"
            response = requests.get(f"{host}/trip-data/yellow_tripdata_{year}-{i:02d}.parquet")

            if response.status_code != 200:
                raise Exception(response.text)

            df = pd.read_parquet(BytesIO(response.content))
            dfs.append(df)

    return pd.concat(dfs)