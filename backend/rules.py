import pandas as pd
def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne les lignes qui ont au moins une valeur manquante."""
    return df[df.isnull().any(axis=1)]
def check_out_of_range(df: pd.DataFrame, column: str, min_val, max_val) -> pd.DataFrame:
    """Retourne les lignes ou la colonne depasse les limites min/max."""
    return df[(df[column] < min_val) | (df[column] > max_val)]
def check_duplicates(df: pd.DataFrame, ignore_columns: list = None) -> pd.DataFrame:
    """Retourne les lignes qui sont des doublons, en ignorant certaines colonnes (ex: id)."""
    if ignore_columns:
        subset = [col for col in df.columns if col not in ignore_columns]
    else:
        subset = df.columns
    return df[df.duplicated(subset=subset, keep=False)]
def check_multiple_ranges(df: pd.DataFrame, range_configs: list) -> dict:
    """
    Applique plusieurs controles de seuil en meme temps.
    range_configs : liste de dicts {"column": str, "min": float, "max": float}
    Retourne un dict {colonne: DataFrame des lignes hors seuil}
    """
    results = {}
    for config in range_configs:
        col = config.get("column")
        if col and col in df.columns:
            results[col] = check_out_of_range(df, col, config["min"], config["max"])
    return results
def check_frozen_values(df: pd.DataFrame, ignore_columns: list = None) -> list:
    """
    Detecte les colonnes dont toutes les valeurs non-nulles sont identiques
    (variance nulle) - souvent signe d'un champ mal rempli ou d'une erreur d'export.
    Retourne une liste de dicts {column, valeur_figee, nombre_lignes}.
    """
    ignore_columns = ignore_columns or []
    frozen = []
    for col in df.columns:
        if col in ignore_columns:
            continue
        non_null = df[col].dropna()
        if len(non_null) == 0:
            continue
        if non_null.nunique() == 1:
            frozen.append({
                "column": col,
                "valeur_figee": str(non_null.iloc[0]),
                "nombre_lignes": int(len(non_null)),
            })
    return frozen