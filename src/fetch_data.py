from __future__ import annotations

import pandas as pd
from statsbombpy import sb


def fetch_team_matches(
    team: str,
    competition_id: int,
    season_id: int,
) -> pd.DataFrame:
    """Fetch matches for a competition/season and filter to those involving `team`."""
    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    matches_df = matches[(matches["home_team"] == team) | (matches["away_team"] == team)].copy()
    return matches_df


def fetch_events_for_matches(matches_df: pd.DataFrame) -> pd.DataFrame:
    """Download and concatenate StatsBomb events for all match_ids in matches_df."""
    combined = []
    for match_id in matches_df["match_id"]:
        combined.append(sb.events(match_id=match_id))
    df = pd.concat(combined, ignore_index=True)
    return df


def fetch_team_events(
    team: str,
    competition_id: int,
    season_id: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    returns (matches_df, events_df) for all matches involving `team`.
    """
    matches_df = fetch_team_matches(team, competition_id, season_id)
    events_df = fetch_events_for_matches(matches_df)
    return matches_df, events_df
