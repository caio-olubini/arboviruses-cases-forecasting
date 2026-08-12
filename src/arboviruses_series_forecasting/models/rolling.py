"""Rolling-origin evaluation for UF × EW dengue baselines."""

from __future__ import annotations

import pandas as pd

from arboviruses_series_forecasting.data.epidemiological.seasons import (
    add_season_end_year,
    held_out_season_end_years,
)
from arboviruses_series_forecasting.data.epidemiological.window import epiweek_of
from arboviruses_series_forecasting.models.arima_fourier import (
    ArimaFourierSpec,
    forecast_arima_fourier,
    select_arima_fourier_spec,
)
from arboviruses_series_forecasting.models.climatology import forecast_climatology
from arboviruses_series_forecasting.models.seasonal_naive import forecast_seasonal_naive

WEEKS_PER_YEAR = 52


def training_window(
    series: pd.Series,
    *,
    origin: pd.Timestamp,
    window_years: int,
) -> pd.Series:
    """Fixed-length history ending at ``origin`` (inclusive)."""
    start = origin - pd.Timedelta(weeks=window_years * WEEKS_PER_YEAR - 1)
    window = series.loc[(series.index >= start) & (series.index <= origin)]
    expected = window_years * WEEKS_PER_YEAR
    if len(window) < expected:
        raise ValueError(
            f"training window at {origin.date()} has {len(window)} weeks, need {expected}"
        )
    return window


def held_out_weeks(
    panel: pd.DataFrame,
    *,
    n_seasons: int,
    season_start: int = 41,
    season_end: int = 40,
) -> tuple[list[int], pd.DatetimeIndex]:
    panel = add_season_end_year(panel, season_start=season_start)
    seasons = held_out_season_end_years(
        panel,
        n_seasons=n_seasons,
        season_start=season_start,
        season_end=season_end,
    )
    weeks = pd.DatetimeIndex(
        sorted(panel.loc[panel["season_end_year"].isin(seasons), "week_start"].unique())
    )
    return seasons, weeks


def _origins_and_horizons(
    held_weeks: pd.DatetimeIndex,
    horizons: list[int],
) -> dict[pd.Timestamp, list[int]]:
    """Map each origin to the horizons whose targets fall in the held-out set."""
    held = set(pd.DatetimeIndex(held_weeks))
    mapping: dict[pd.Timestamp, list[int]] = {}
    for horizon in horizons:
        for target in held_weeks:
            origin = pd.Timestamp(target) - pd.Timedelta(weeks=horizon)
            mapping.setdefault(origin, [])
            if horizon not in mapping[origin]:
                mapping[origin].append(horizon)
    # Keep only origins that need at least one horizon (all do by construction).
    return {origin: sorted(hs) for origin, hs in sorted(mapping.items()) if hs}


def run_baseline_forecasts(
    panel: pd.DataFrame,
    *,
    horizons: list[int],
    training_window_years: int = 6,
    held_out_seasons: int = 2,
    season_start: int = 41,
    season_end: int = 40,
    arima_specs: dict[str, ArimaFourierSpec] | None = None,
) -> tuple[pd.DataFrame, dict[str, ArimaFourierSpec], list[int]]:
    """Produce tidy forecasts for seasonal naive, climatology, and ARIMA+Fourier."""
    panel = panel.copy()
    panel["week_start"] = pd.to_datetime(panel["week_start"])
    if "ew" not in panel.columns:
        panel = pd.concat([panel, epiweek_of(panel["week_start"])], axis=1)

    seasons, held_weeks = held_out_weeks(
        panel,
        n_seasons=held_out_seasons,
        season_start=season_start,
        season_end=season_end,
    )
    origin_horizons = _origins_and_horizons(held_weeks, horizons)
    if not origin_horizons:
        raise ValueError("No valid rolling origins for the held-out window")

    ufs = sorted(panel["uf"].unique())
    first_origin = next(iter(origin_horizons))
    if arima_specs is None:
        arima_specs = {}
        for uf in ufs:
            series = (
                panel.loc[panel["uf"] == uf, ["week_start", "cases"]]
                .set_index("week_start")["cases"]
                .sort_index()
            )
            train = training_window(
                series, origin=first_origin, window_years=training_window_years
            )
            arima_specs[uf] = select_arima_fourier_spec(train)

    rows: list[dict] = []
    for uf in ufs:
        series = (
            panel.loc[panel["uf"] == uf, ["week_start", "cases"]]
            .set_index("week_start")["cases"]
            .sort_index()
        )
        spec = arima_specs[uf]

        for origin, origin_hs in origin_horizons.items():
            history = training_window(
                series, origin=origin, window_years=training_window_years
            )
            hist_frame = history.rename("cases").reset_index()

            naive = forecast_seasonal_naive(history, horizons=origin_hs)
            clim = forecast_climatology(hist_frame, origin=origin, horizons=origin_hs)
            # Always request the full horizon set so one fit covers every target from this origin.
            arima = forecast_arima_fourier(history, horizons=horizons, spec=spec)

            for model_name, preds in (
                ("seasonal_naive", naive),
                ("climatology", clim),
                ("arima_fourier", {h: arima[h] for h in origin_hs}),
            ):
                for horizon, value in preds.items():
                    rows.append(
                        {
                            "uf": uf,
                            "origin": origin,
                            "week_start": origin + pd.Timedelta(weeks=horizon),
                            "horizon": horizon,
                            "model": model_name,
                            "forecast": value,
                        }
                    )

    return pd.DataFrame(rows), arima_specs, seasons
