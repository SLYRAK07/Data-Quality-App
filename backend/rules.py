import pandas as pd


def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne les lignes qui ont au moins une valeur manquante."""
    return df[df.isnull().any(axis=1)]


def check_out_of_range(df: pd.DataFrame, column: str, min_val, max_val) -> pd.DataFrame:
    """Retourne les lignes où la colonne dépasse les limites min/max."""
    return df[(df[column] < min_val) | (df[column] > max_val)]


def check_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne les lignes qui sont des doublons exacts."""
    return df[df.duplicated(keep=False)]