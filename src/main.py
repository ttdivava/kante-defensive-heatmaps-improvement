from __future__ import annotations

import argparse
from src.fetch_data import fetch_team_events
from src.preprocess import (
    filter_player,
    add_xy_from_location,
    filter_event_types,
    split_by_half,
)
from src.plots import make_all_maps


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate defensive and on-ball heatmaps for a player using StatsBomb event data."
    )

    parser.add_argument("--team", type=str, required=True,
                        help="Team name as used by StatsBomb (e.g., 'Leicester City').")
    parser.add_argument("--player", type=str, required=True,
                        help="Exact player name string from StatsBomb (e.g., N''Golo Kanté).")
    parser.add_argument("--competition-id", type=int, default=2,
                        help="StatsBomb competition_id (default: 2 = Premier League).")
    parser.add_argument("--season-id", type=int, default=27,
                        help="StatsBomb season_id (default: 27 = 2015/16).")
    parser.add_argument("--out-dir", type=str, default="output/kante_maps",
                        help="Directory to save generated figures.")
    parser.add_argument("--bins-x", type=int, default=25,
                        help="Number of bins along pitch length.")
    parser.add_argument("--bins-y", type=int, default=18,
                        help="Number of bins along pitch width.")

    return parser.parse_args()


def main():
    args = parse_args()

    # Event groups
    DEFENSIVE_TYPES = ["Pressure", "Ball Recovery", "Interception", "Block", "Clearance"]
    ONBALL_TYPES = ["Pass", "Carry", "Ball Receipt*", "Dribble", "Shot"]
    BINS = (args.bins_x, args.bins_y)

    print("Fetching data...")
    matches_df, events_df = fetch_team_events(
        team=args.team,
        competition_id=args.competition_id,
        season_id=args.season_id,
    )

    print("Filtering player...")
    df_player = filter_player(events_df, args.player)
    df_player = add_xy_from_location(df_player)

    print(f"Total events for player: {len(df_player)}")

    df_def = filter_event_types(df_player, DEFENSIVE_TYPES)
    df_on = filter_event_types(df_player, ONBALL_TYPES)
    df_def_h1, df_def_h2 = split_by_half(df_def)

    subtitle_base = (
        f"{args.team} | Premier League 2015–16 | Data: StatsBomb events (statsbombpy)"
    )
    caption_base = (
        "Note: A heatmap shows WHERE actions are concentrated. "
        "Counts are not distance covered, and KDE density is smoothed (not exact counts)."
    )

    print("Generating maps...")
    saved = make_all_maps(
        df_def=df_def,
        df_on=df_on,
        df_def_h1=df_def_h1,
        df_def_h2=df_def_h2,
        out_dir=args.out_dir,
        subtitle_base=subtitle_base,
        caption_base=caption_base,
        defensive_types=DEFENSIVE_TYPES,
        onball_types=ONBALL_TYPES,
        bins=BINS,
    )

    print("\nFinished. Saved figures:")
    for key, path in saved.items():
        print(f"  {key}: {path}")


if __name__ == "__main__":
    main()
