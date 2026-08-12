import pandas as pd
from backend.rules import check_missing_values, check_out_of_range, check_duplicates


def test_missing_values():
    df = pd.DataFrame({"a": [1, None, 3]})
    result = check_missing_values(df)
    assert len(result) == 1


def test_out_of_range():
    df = pd.DataFrame({"age": [25, 150, 30]})
    result = check_out_of_range(df, "age", 0, 120)
    assert len(result) == 1


def test_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2]})
    result = check_duplicates(df)
    assert len(result) == 2