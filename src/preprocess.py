from __future__ import annotations

import pandas as pd
import numpy as np


def filter_player(events_df: pd.DataFrame, player_name: str) -> pd.DataFrame:
    """Filter events to a specific player."""
    df_player = events_df[events_df["player"] == player_name].copy()
    return df_player


def add_xy_from_location(df_in: pd.DataFrame) -> pd.DataFrame:
    """
    Extract x/y from StatsBomb 'location' field.
    Keeps only rows where location is list/tuple with at least 2 values.
    """
    df = df_in.copy()

    mask_loc = df["location"].apply(lambda v: isinstance(v, (list, tuple)) and len(v) >= 2)
    df = df.loc[mask_loc].copy()

    df["x"] = pd.to_numeric(df["location"].str[0], errors="coerce")
    df["y"] = pd.to_numeric(df["location"].str[1], errors="coerce")
    df = df.dropna(subset=["x", "y"])

    return df


def filter_event_types(df_in: pd.DataFrame, event_types: list[str]) -> pd.DataFrame:
    """Keep only rows whose 'type' is in event_types."""
    return df_in[df_in["type"].isin(event_types)].copy()


def split_by_half(df_in: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split events by half (period 1 and period 2), if 'period' exists.
    Returns (half1, half2). If period missing, returns (empty, empty).
    """
    if "period" not in df_in.columns:
        return df_in.iloc[0:0].copy(), df_in.iloc[0:0].copy()

    half1 = df_in[df_in["period"] == 1].copy()
    half2 = df_in[df_in["period"] == 2].copy()
    return half1, half2


def get_top_event_types(df_in: pd.DataFrame, n: int = 15) -> pd.Series:
    """Helper for debugging: top event types in a dataframe."""
    return df_in["type"].value_counts().head(n)
