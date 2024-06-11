from typing import List
import pandas as pd


def create_target_duration(trip_data: pd.DataFrame) -> pd.DataFrame:
    trip_data.tpep_dropoff_datetime = pd.to_datetime(trip_data.tpep_dropoff_datetime)
    trip_data.tpep_pickup_datetime = pd.to_datetime(trip_data.tpep_pickup_datetime)

    trip_data['duration'] = trip_data.tpep_dropoff_datetime - trip_data.tpep_pickup_datetime
    trip_data.duration = trip_data.duration.dt.total_seconds() / 60

    return trip_data


def clean_data(trip_data: pd.DataFrame, categorical_feature: List[str]) -> pd.DataFrame:
    trip_data = trip_data[(trip_data.duration >= 1) & (trip_data.duration <= 60)]
    trip_data[categorical_feature] = trip_data[categorical_feature].astype(str)

    return trip_data 