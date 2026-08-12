"""Score point forecasts against truth — Phase 1 headline metrics.

The multimodal model must call this unchanged: tidy forecasts in, tidy scores out.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

REQUIRED_FORECAST_COLUMNS = ("uf", "week_start", "horizon", "model", "forecast")
REQUIRED_TRUTH_COLUMNS = ("uf", "week_start", "cases")


def mae_log1p(forecast: pd.Series | np.ndarray, truth: pd.Series | np.ndarray) -> float:
    """Mean absolute error on log1p scale (headline metric for point forecasts)."""
    forecast = np.asarray(forecast, dtype=float)
    truth = np.asarray(truth, dtype=float)
    if forecast.shape != truth.shape:
        raise ValueError("forecast and truth must have the same shape")
    if len(forecast) == 0:
        return float("nan")
    return float(np.mean(np.abs(np.log1p(forecast) - np.log1p(truth))))


def skill_vs_baseline(model_mae: float, baseline_mae: float) -> float:
    """Percent improvement vs a reference MAE. Positive = better than the reference."""
    if baseline_mae == 0:
        return float("nan") if model_mae != 0 else 0.0
    return float(100.0 * (baseline_mae - model_mae) / baseline_mae)


def score_forecasts(
    forecasts: pd.DataFrame,
    truth: pd.DataFrame,
    *,
    skill_baseline_model: str = "seasonal_naive",
) -> pd.DataFrame:
    """Join forecasts to truth and return tidy scores by model × horizon.

    Expected columns
    ----------------
    forecasts: uf, week_start, horizon, model, forecast
    truth:     uf, week_start, cases

    Returns one row per (model, horizon) with mae_log1p and skill_vs_<baseline>.
    """
    _require_columns(forecasts, REQUIRED_FORECAST_COLUMNS, "forecasts")
    _require_columns(truth, REQUIRED_TRUTH_COLUMNS, "truth")

    scored = forecasts.merge(truth, on=["uf", "week_start"], how="inner")
    if scored.empty:
        raise ValueError("No overlapping (uf, week_start) rows between forecasts and truth")

    rows: list[dict] = []
    for (model, horizon), group in scored.groupby(["model", "horizon"], sort=True):
        rows.append(
            {
                "model": model,
                "horizon": int(horizon),
                "mae_log1p": mae_log1p(group["forecast"], group["cases"]),
                "n": len(group),
            }
        )
    scores = pd.DataFrame(rows)

    baseline = scores.loc[scores["model"] == skill_baseline_model, ["horizon", "mae_log1p"]]
    if baseline.empty:
        raise ValueError(
            f"skill baseline model {skill_baseline_model!r} not present in forecasts"
        )
    baseline = baseline.rename(columns={"mae_log1p": "baseline_mae"})
    scores = scores.merge(baseline, on="horizon", how="left")
    scores["skill_vs_seasonal_naive"] = [
        skill_vs_baseline(mae, base)
        for mae, base in zip(scores["mae_log1p"], scores["baseline_mae"])
    ]
    return scores.drop(columns=["baseline_mae"]).sort_values(
        ["horizon", "model"], ignore_index=True
    )


def _require_columns(frame: pd.DataFrame, required: tuple[str, ...], name: str) -> None:
    missing = set(required) - set(frame.columns)
    if missing:
        raise ValueError(f"{name} missing columns: {sorted(missing)}")
