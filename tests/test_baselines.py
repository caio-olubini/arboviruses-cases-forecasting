"""Tests for scoring and baseline forecasts."""

from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from arboviruses_series_forecasting.data.epidemiological.seasons import (
    held_out_season_end_years,
    season_end_year,
)
from arboviruses_series_forecasting.metrics.evaluate import (
    mae_log1p,
    score_forecasts,
    skill_vs_baseline,
)
from arboviruses_series_forecasting.models.arima_fourier import (
    ArimaFourierSpec,
    forecast_arima_fourier,
    fourier_design,
)
from arboviruses_series_forecasting.models.climatology import forecast_climatology
from arboviruses_series_forecasting.models.seasonal_naive import forecast_seasonal_naive


def test_mae_log1p_is_zero_when_forecast_equals_truth() -> None:
    assert mae_log1p([1.0, 10.0], [1.0, 10.0]) == 0.0


def test_mae_log1p_rejects_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="same shape"):
        mae_log1p([1.0], [1.0, 2.0])


def test_skill_vs_baseline_positive_when_model_better() -> None:
    assert skill_vs_baseline(0.5, 1.0) == pytest.approx(50.0)


def test_score_forecasts_returns_skill_column() -> None:
    truth = pd.DataFrame(
        {
            "uf": ["AC", "AC"],
            "week_start": pd.to_datetime(["2020-01-05", "2020-01-12"]),
            "cases": [10.0, 20.0],
        }
    )
    forecasts = pd.DataFrame(
        {
            "uf": ["AC", "AC", "AC", "AC"],
            "week_start": pd.to_datetime(
                ["2020-01-05", "2020-01-12", "2020-01-05", "2020-01-12"]
            ),
            "horizon": [4, 4, 4, 4],
            "model": [
                "seasonal_naive",
                "seasonal_naive",
                "climatology",
                "climatology",
            ],
            "forecast": [10.0, 20.0, 12.0, 18.0],
        }
    )

    scores = score_forecasts(forecasts, truth)
    naive = scores.loc[scores["model"] == "seasonal_naive", "mae_log1p"].item()
    assert naive == pytest.approx(0.0)
    assert "skill_vs_seasonal_naive" in scores.columns


def test_season_end_year_ew41_belongs_to_next_year() -> None:
    assert season_end_year(2023, 41) == 2024
    assert season_end_year(2024, 40) == 2024


def test_seasonal_naive_uses_lag_52() -> None:
    idx = pd.date_range("2018-01-07", periods=60, freq="W-SUN")
    values = pd.Series(np.arange(60, dtype=float), index=idx)
    origin = idx[52]
    history = values.loc[:origin]
    preds = forecast_seasonal_naive(history, horizons=[4])
    assert preds[4] == pytest.approx(float(values.loc[origin + timedelta(weeks=4 - 52)]))


def test_climatology_uses_same_ew_median() -> None:
    weeks = pd.date_range("2018-01-07", periods=104, freq="W-SUN")
    history = pd.DataFrame(
        {
            "week_start": weeks,
            "cases": [10.0] * 52 + [30.0] * 52,
        }
    )
    origin = weeks[100]
    preds = forecast_climatology(history.iloc[:101], origin=origin, horizons=[4])
    assert preds[4] >= 0.0


def test_fourier_design_has_2k_columns() -> None:
    design = fourier_design(np.arange(10), period=52, k=2)
    assert list(design.columns) == ["sin_1", "cos_1", "sin_2", "cos_2"]


def test_arima_fourier_returns_non_negative_counts() -> None:
    idx = pd.date_range("2015-01-04", periods=120, freq="W-SUN")
    # Mild seasonal signal so the fit is stable on a tiny series.
    t = np.arange(120)
    cases = pd.Series(
        np.clip(20 + 10 * np.sin(2 * np.pi * t / 52) + np.random.default_rng(0).normal(0, 1, 120), 0, None),
        index=idx,
    )
    preds = forecast_arima_fourier(
        cases,
        horizons=[4, 12],
        spec=ArimaFourierSpec(order=(1, 0, 0), fourier_k=1),
    )
    assert preds[4] >= 0.0
    assert preds[12] >= 0.0
