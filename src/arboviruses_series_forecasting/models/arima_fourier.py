"""ARIMA with Fourier seasonality on log1p counts.

Fourier terms replace seasonal ARIMA: m = 52 is numerically miserable as a SARIMA period.
K (number of harmonics) and (p, d, q) are chosen by AICc on a training window.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

SEASONAL_PERIOD = 52
MAX_FOURIER_K = 3
# Tiny ARIMA grid: Fourier K is the load-bearing choice for m = 52.
CANDIDATE_ORDERS = ((1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1), (2, 0, 1))


@dataclass(frozen=True)
class ArimaFourierSpec:
    order: tuple[int, int, int]
    fourier_k: int


def fourier_design(time_index: np.ndarray, *, period: int, k: int) -> pd.DataFrame:
    """Columns sin_1..sin_k, cos_1..cos_k for week indices ``time_index``."""
    design = {}
    for harmonic in range(1, k + 1):
        angle = 2.0 * np.pi * harmonic * time_index / period
        design[f"sin_{harmonic}"] = np.sin(angle)
        design[f"cos_{harmonic}"] = np.cos(angle)
    return pd.DataFrame(design)


def _aicc(n_obs: int, n_params: int, aic: float) -> float:
    if n_obs - n_params - 1 <= 0:
        return np.inf
    return aic + (2 * n_params * (n_params + 1)) / (n_obs - n_params - 1)


def _fit_sarimax(
    log_cases: np.ndarray,
    exog: pd.DataFrame | None,
    order: tuple[int, int, int],
):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = SARIMAX(
            log_cases,
            exog=exog,
            order=order,
            seasonal_order=(0, 0, 0, 0),
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        return model.fit(disp=False)


def select_arima_fourier_spec(
    cases: pd.Series,
    *,
    period: int = SEASONAL_PERIOD,
    max_k: int = MAX_FOURIER_K,
) -> ArimaFourierSpec:
    """Pick Fourier K and a small ARIMA order by AICc on ``cases`` (raw counts)."""
    log_cases = np.log1p(cases.astype(float).to_numpy())
    t = np.arange(len(log_cases), dtype=float)
    best: tuple[float, ArimaFourierSpec] | None = None

    for k in range(1, max_k + 1):
        exog = fourier_design(t, period=period, k=k)
        for order in CANDIDATE_ORDERS:
            try:
                fitted = _fit_sarimax(log_cases, exog, order)
            except Exception:
                continue
            p, d, q = order
            n_params = p + q + d + 2 * k + 1
            score = _aicc(len(log_cases), n_params, float(fitted.aic))
            spec = ArimaFourierSpec(order=order, fourier_k=k)
            if best is None or score < best[0]:
                best = (score, spec)

    if best is None:
        return ArimaFourierSpec(order=(1, 0, 0), fourier_k=1)
    return best[1]


def forecast_arima_fourier(
    history: pd.Series,
    *,
    horizons: list[int],
    spec: ArimaFourierSpec,
    period: int = SEASONAL_PERIOD,
) -> dict[int, float]:
    """Fit ``spec`` on history and forecast each horizon on the count scale."""
    history = history.astype(float).sort_index()
    log_cases = np.log1p(history.to_numpy())
    n = len(log_cases)
    t_train = np.arange(n, dtype=float)
    exog_train = fourier_design(t_train, period=period, k=spec.fourier_k)

    fitted = _fit_sarimax(log_cases, exog_train, spec.order)

    max_h = max(horizons)
    t_future = np.arange(n, n + max_h, dtype=float)
    exog_future = fourier_design(t_future, period=period, k=spec.fourier_k)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        log_forecast = fitted.forecast(steps=max_h, exog=exog_future)

    # Invert log1p; clip at 0 in case of tiny negative numerical noise.
    count_forecast = np.expm1(np.asarray(log_forecast, dtype=float))
    count_forecast = np.clip(count_forecast, 0.0, None)

    return {horizon: float(count_forecast[horizon - 1]) for horizon in horizons}
