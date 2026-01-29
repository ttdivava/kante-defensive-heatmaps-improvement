from __future__ import annotations

import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from mplsoccer import Pitch


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def base_pitch(figsize=(11, 7)):
    pitch = Pitch(
        pitch_type="statsbomb",
        pitch_color="white",
        line_color="grey",
        line_zorder=2,
    )
    fig, ax = pitch.draw(figsize=figsize)
    return pitch, fig, ax


def add_header_footer(fig, ax, title: str, subtitle: str, caption: str) -> None:
    ax.set_title(title, fontsize=16, fontweight="bold", pad=25)
    fig.text(0.125, 0.91, subtitle, fontsize=10, wrap=True)
    fig.text(0.125, 0.02, caption, fontsize=9, wrap=True)


def save_fig(fig, out_dir: str, filename: str) -> str:
    ensure_dir(out_dir)
    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    return path


def plot_binned_count_heatmap(pitch, fig, ax, df_xy, bins=(25, 18), cmap="Blues",
                              cbar_label="Count per zone"):
    bin_stat = pitch.bin_statistic(df_xy["x"], df_xy["y"], statistic="count", bins=bins)
    hm = pitch.heatmap(bin_stat, ax=ax, cmap=cmap)
    cbar = fig.colorbar(hm, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label(cbar_label, fontsize=11, fontweight="bold")
    return hm


def plot_kde_density(pitch, fig, ax, df_xy, levels=60, thresh=0, cmap="Blues",
                     cbar_label="Relative intensity (KDE)"):
    pitch.kdeplot(
        df_xy["x"], df_xy["y"],
        fill=True, levels=levels, thresh=thresh, cmap=cmap, ax=ax
    )
    if len(ax.collections) == 0:
        raise RuntimeError("No KDE collections created. df_xy may be empty or too small.")

    mappable = ax.collections[-1]
    cbar = fig.colorbar(mappable, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label(cbar_label, fontsize=11, fontweight="bold")

    # Optional: format KDE colorbar as 0–100% relative intensity
    cbar_min = mappable.norm.vmin
    cbar_max = mappable.norm.vmax

    def intensity_formatter(x, pos):
        if cbar_max > cbar_min:
            intensity = ((x - cbar_min) / (cbar_max - cbar_min)) * 100
            return f"{intensity:.0f}%"
        return f"{x:.1e}"

    cbar.ax.yaxis.set_major_formatter(FuncFormatter(intensity_formatter))
    return mappable


def plot_points(pitch, fig, ax, df_xy, alpha=0.25, size=10):
    pitch.scatter(df_xy["x"], df_xy["y"], s=size, alpha=alpha, ax=ax)


def make_all_maps(
    df_def,
    df_on,
    df_def_h1,
    df_def_h2,
    out_dir: str,
    subtitle_base: str,
    caption_base: str,
    defensive_types: list[str],
    onball_types: list[str],
    bins=(25, 18),
):
    """
    Generates and saves A–E maps (count, on-ball count, KDE density, half splits, raw points).
    Returns dict of {figure_key: saved_path}.
    """
    ensure_dir(out_dir)
    saved = {}

    # A: Defensive count heatmap
    pitch, fig, ax = base_pitch()
    plot_binned_count_heatmap(pitch, fig, ax, df_def, bins=bins, cbar_label="Defensive actions per zone (count)")
    add_header_footer(
        fig, ax,
        title="Figure A — Defensive actions (count heatmap)",
        subtitle=subtitle_base + f" | Events: {', '.join(defensive_types)}",
        caption=caption_base + " Metric here is COUNT per zone."
    )
    saved["A"] = save_fig(fig, out_dir, "A_defensive_count_heatmap.png")
    plt.close(fig)

    # B: On-ball count heatmap
    pitch, fig, ax = base_pitch()
    plot_binned_count_heatmap(pitch, fig, ax, df_on, bins=bins, cbar_label="On-ball actions per zone (count)")
    add_header_footer(
        fig, ax,
        title="Figure B — On-ball involvement (count heatmap)",
        subtitle=subtitle_base + f" | Events: {', '.join(onball_types)}",
        caption=caption_base + " Metric here is COUNT per zone."
    )
    saved["B"] = save_fig(fig, out_dir, "B_onball_count_heatmap.png")
    plt.close(fig)

    # C: KDE density (defensive)
    pitch, fig, ax = base_pitch(figsize=(12, 8))
    plot_kde_density(pitch, fig, ax, df_def, cbar_label="Relative intensity (0% low → 100% high)")

    # Optional axis labels (your version)
    ax.set_xlabel("Field Width (0–120)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Field Length (0–80)", fontsize=12, fontweight="bold")
    ax.tick_params(axis="both", which="major", labelsize=10, colors="black")

    add_header_footer(
        fig, ax,
        title="Figure C — Defensive action density (KDE heatmap)",
        subtitle=subtitle_base + f" | Events: {', '.join(defensive_types)}",
        caption=(caption_base +
                 " Metric: KDE smoothing reveals concentration zones. Darker areas = higher density.")
    )
    fig.subplots_adjust(bottom=0.14, top=0.87, left=0.12, right=0.95)
    saved["C"] = save_fig(fig, out_dir, "C_defensive_kde_density.png")
    plt.close(fig)

    # D1/D2: Split by half (if provided and non-empty)
    if df_def_h1 is not None and len(df_def_h1) > 0:
        pitch, fig, ax = base_pitch()
        plot_binned_count_heatmap(pitch, fig, ax, df_def_h1, bins=bins, cbar_label="Defensive actions per zone (count)")
        add_header_footer(
            fig, ax,
            title="Figure D1 — Defensive actions (1st half)",
            subtitle=subtitle_base + f" | Events: {', '.join(defensive_types)}",
            caption=caption_base + " This figure shows only FIRST HALF events."
        )
        saved["D1"] = save_fig(fig, out_dir, "D1_defensive_half1_count.png")
        plt.close(fig)

    if df_def_h2 is not None and len(df_def_h2) > 0:
        pitch, fig, ax = base_pitch()
        plot_binned_count_heatmap(pitch, fig, ax, df_def_h2, bins=bins, cbar_label="Defensive actions per zone (count)")
        add_header_footer(
            fig, ax,
            title="Figure D2 — Defensive actions (2nd half)",
            subtitle=subtitle_base + f" | Events: {', '.join(defensive_types)}",
            caption=caption_base + " This figure shows only SECOND HALF events."
        )
        saved["D2"] = save_fig(fig, out_dir, "D2_defensive_half2_count.png")
        plt.close(fig)

    # E: Raw points
    pitch, fig, ax = base_pitch()
    plot_points(pitch, fig, ax, df_def)
    add_header_footer(
        fig, ax,
        title="Figure E — Defensive actions (raw points)",
        subtitle=subtitle_base + f" | Events: {', '.join(defensive_types)}",
        caption=caption_base + " Each dot is a single event; no smoothing."
    )
    saved["E"] = save_fig(fig, out_dir, "E_defensive_raw_points.png")
    plt.close(fig)

    return saved
