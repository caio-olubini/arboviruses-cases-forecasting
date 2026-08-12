"""Seasonal naive baseline: ŷ_{t+h} = y_{t+h-52}."""

from __future__ import annotations

import pandas as pd

SEASONAL_PERIOD = 52


def forecast_seasonal_naive(
    history: pd.Series,
    *,
    horizons: list[int],
    period: int = SEASONAL_PERIOD,
) -> dict[int, float]:
    """Point forecasts from a history indexed by week_start (ascending).

    ``history`` must include the origin week (last index) and enough past
    seasonal lags for each horizon.
    """
    if history.empty:
        raise ValueError("history is empty")

    values = history.astype(float)
    origin = values.index.max()
    out: dict[int, float] = {}
    for horizon in horizons:
        seasonal_week = origin + pd.Timedelta(weeks=horizon - period)
        if seasonal_week not in values.index:
            raise KeyError(
                f"seasonal naive needs lag-{period} at horizon {horizon}: "
                f"missing {seasonal_week.date()}"
            )
        out[horizon] = float(values.loc[seasonal_week])
    return out
