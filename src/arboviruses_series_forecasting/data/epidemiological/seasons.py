"""Dengue-season labels (EW41 → EW40) for held-out evaluation."""

from __future__ import annotations

import pandas as pd

from arboviruses_series_forecasting.data.epidemiological.window import (
    epiweek_of,
    sunday_of_epiweek,
)


def season_end_year(
    ew_year: pd.Series | int,
    ew: pd.Series | int,
    *,
    season_start: int = 41,
) -> pd.Series | int:
    """Label a week by the year in which its dengue season ends.

    Season EW41 of Y → EW40 of Y+1 is labeled ``Y+1``.
    """
    if isinstance(ew_year, int) and isinstance(ew, int):
        return ew_year + 1 if ew >= season_start else ew_year

    ew_year_s = pd.Series(ew_year)
    ew_s = pd.Series(ew)
    return pd.Series(
        [
            int(year) + 1 if int(week) >= season_start else int(year)
            for year, week in zip(ew_year_s, ew_s)
        ],
        index=ew_year_s.index,
    )


def add_season_end_year(
    panel: pd.DataFrame,
    *,
    season_start: int = 41,
) -> pd.DataFrame:
    out = panel.copy()
    if "ew_year" not in out.columns or "ew" not in out.columns:
        out = pd.concat([out, epiweek_of(out["week_start"])], axis=1)
    out["season_end_year"] = season_end_year(
        out["ew_year"], out["ew"], season_start=season_start
    )
    return out


def complete_season_end_years(
    panel: pd.DataFrame,
    *,
    season_start: int = 41,
    season_end: int = 40,
) -> list[int]:
    """Season end-years for which the panel covers EW41..(EW40 of next year)."""
    panel = add_season_end_year(panel, season_start=season_start)
    complete: list[int] = []
    for end_year in sorted(panel["season_end_year"].unique()):
        start = sunday_of_epiweek(int(end_year) - 1, season_start)
        end = sunday_of_epiweek(int(end_year), season_end)
        weeks = panel.loc[
            (panel["week_start"] >= start) & (panel["week_start"] <= end),
            "week_start",
        ].nunique()
        expected = int((end - start).days // 7) + 1
        if weeks >= expected:
            complete.append(int(end_year))
    return complete


def held_out_season_end_years(
    panel: pd.DataFrame,
    *,
    n_seasons: int = 2,
    season_start: int = 41,
    season_end: int = 40,
) -> list[int]:
    complete = complete_season_end_years(
        panel, season_start=season_start, season_end=season_end
    )
    if len(complete) < n_seasons:
        raise ValueError(
            f"Need {n_seasons} complete seasons, found {len(complete)}: {complete}"
        )
    return complete[-n_seasons:]
