"""Guards for artifacts that a clean clone must ship."""

from pathlib import Path

import pandas as pd

from arboviruses_series_forecasting.data.epidemiological.pipeline import PANEL_COLUMNS

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = REPO_ROOT / "data" / "processed" / "dengue_uf_ew.parquet"
POPULATION_PATH = REPO_ROOT / "data" / "external" / "ibge_uf_population_2024.csv"
SCORES_PATH = REPO_ROOT / "results" / "baseline_scores.parquet"


def test_shipped_panel_is_rectangular_uf_week() -> None:
    assert PANEL_PATH.is_file(), f"missing tracked panel: {PANEL_PATH}"
    panel = pd.read_parquet(PANEL_PATH)
    assert list(panel.columns) == list(PANEL_COLUMNS)
    assert panel["uf"].nunique() == 27
    n_weeks = panel["week_start"].nunique()
    assert len(panel) == n_weeks * 27
    assert panel["cases"].isna().sum() == 0


def test_shipped_population_covers_all_ufs() -> None:
    assert POPULATION_PATH.is_file(), f"missing tracked population: {POPULATION_PATH}"
    population = pd.read_csv(POPULATION_PATH)
    panel_ufs = set(pd.read_parquet(PANEL_PATH, columns=["uf"])["uf"])
    assert set(population["uf"]) == panel_ufs


def test_shipped_baseline_scores_cover_three_models() -> None:
    assert SCORES_PATH.is_file(), f"missing tracked scores: {SCORES_PATH}"
    scores = pd.read_parquet(SCORES_PATH)
    assert set(scores["model"]) == {"seasonal_naive", "climatology", "arima_fourier"}
    assert set(scores["horizon"]) == {4, 12}
