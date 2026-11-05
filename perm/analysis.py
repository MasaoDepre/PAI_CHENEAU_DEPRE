"""Statistiques orbitales indépendantes de l’interface NiceGUI."""

import pandas as pd

ORBIT_COLUMN = "Class of Orbit"


def count_by_orbit(df: pd.DataFrame) -> pd.DataFrame:
    """Compte les satellites par classe d’orbite, hors valeurs manquantes.

    Renvoie les colonnes orbit et count, triées par effectif décroissant.
    """
    counts = df[ORBIT_COLUMN].dropna().value_counts()
    return counts.rename_axis("orbit").reset_index(name="count")
