"""Climatology baseline: historical median by epidemiological week."""

from __future__ import annotations

import pandas as pd

from arboviruses_series_forecasting.data.epidemiological.window import epiweek_of


def forecast_climatology(
    history: pd.DataFrame,
    *,
    origin: pd.Timestamp,
    horizons: list[int],
) -> dict[int, float]:
    """Point forecast = training-window median of the same EW.

    ``history`` columns: week_start, cases (and optionally ew).
    """
    hist = history.copy()
    hist["week_start"] = pd.to_datetime(hist["week_start"])
    if "ew" not in hist.columns:
        hist = pd.concat([hist, epiweek_of(hist["week_start"])], axis=1)

    by_ew = hist.groupby("ew")["cases"].median()
    origin = pd.Timestamp(origin)
    out: dict[int, float] = {}
    for horizon in horizons:
        target = origin + pd.Timedelta(weeks=horizon)
        ew = int(epiweek_of(pd.Series([target]))["ew"].iloc[0])
        # EW53 is rare; fall back to EW52 climatology when unseen.
        if ew not in by_ew.index:
            ew = 52 if 52 in by_ew.index else int(by_ew.index.max())
        out[horizon] = float(by_ew.loc[ew])
    return out
