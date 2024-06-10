from utils_trip_data.load_data import read_data
from pandas import DataFrame

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader


@data_loader
def ingest_files(**kwargs) -> DataFrame:

    anho = kwargs['anho']
    mes_ini = kwargs['mes_ini']
    mes_fin_excluyendo = kwargs['mes_fin_excluyendo']
    trip_data = read_data.read(anho, mes_ini, mes_fin_excluyendo)
    
    print(f"rows -> {trip_data.shape[0]}")

    return trip_data