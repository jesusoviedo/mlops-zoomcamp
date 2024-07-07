import batch
import pandas as pd
from pprint import pprint
from datetime import datetime
from deepdiff import DeepDiff

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


def test_prepare_data():
    data_actual = [
        (None, None, dt(1, 1), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
    ]

    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df = pd.DataFrame(data_actual, columns=columns)

    actual_features = batch.prepare_data(df, columns[0:2]).to_dict(orient='records')

    data_esperada = [
        ('-1', '-1', dt(1, 1), dt(1, 10), 9.0),
        ('1', '1', dt(1, 2), dt(1, 10), 8.0),
    ]

    expected_fetures = pd.DataFrame(data_esperada, columns=columns + ['duration']).to_dict(orient='records')

    diff = DeepDiff(actual_features, expected_fetures)

    print('\n\ndiff =')
    pprint(diff)
    if diff:
        print('\n\nactual =')
        pprint(actual_features)
        print('\n\nexpected =')
        pprint(expected_fetures)

    assert 'iterable_item_added' not in diff
    assert 'type_changes' not in diff
    assert 'values_changed' not in diff