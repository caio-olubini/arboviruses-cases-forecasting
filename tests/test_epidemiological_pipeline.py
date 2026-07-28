"""Tests for SINAN → UF × EW aggregation steps."""

from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from arboviruses_series_forecasting.data.epidemiological.aggregate import (
    aggregate_by_uf_and_onset_week,
    complete_uf_week_panel,
)
from arboviruses_series_forecasting.data.epidemiological.pipeline import (
    build_dengue_uf_ew_series,
)
from arboviruses_series_forecasting.data.epidemiological.probable import (
    DISCARDED_CLASSIFICATION,
    keep_probable_cases,
)
from arboviruses_series_forecasting.data.epidemiological.window import (
    drop_right_censored_weeks,
    parse_epiweek_label,
    sunday_of_epiweek,
)


def test_sunday_of_epiweek_matches_cdc_week1_2010() -> None:
    assert sunday_of_epiweek(2010, 1) == pd.Timestamp("2010-01-03")


def test_parse_epiweek_label() -> None:
    assert parse_epiweek_label("2010-EW01") == (2010, 1)


def test_keep_probable_cases_drops_only_discarded() -> None:
    cases = pd.DataFrame(
        {
            "final_classification": [5, 10, pd.NA],
            "case_count": [100, 7, 3],
        }
    ).astype({"final_classification": "Int8"})

    probable = keep_probable_cases(cases)

    assert list(probable["case_count"]) == [7, 3]
    assert DISCARDED_CLASSIFICATION not in set(probable["final_classification"].dropna())


def test_aggregate_sums_within_uf_and_week() -> None:
    cases = pd.DataFrame(
        {
            "state_abbrev": ["SP", "SP", "RJ"],
            "ew_symptom_onset": pd.to_datetime(
                ["2010-01-03", "2010-01-03", "2010-01-03"]
            ),
            "case_count": [2, 5, 1],
        }
    )

    weekly = aggregate_by_uf_and_onset_week(cases)

    assert list(weekly.columns) == ["uf", "week_start", "cases"]
    sp = weekly.loc[weekly["uf"] == "SP", "cases"].item()
    assert sp == 7


def test_complete_panel_fills_missing_weeks_with_zero() -> None:
    weekly = pd.DataFrame(
        {
            "uf": ["AC", "AC"],
            "week_start": pd.to_datetime(["2010-01-03", "2010-01-17"]),
            "cases": [4, 9],
        }
    )

    panel = complete_uf_week_panel(weekly)

    assert len(panel) == 3
    gap = panel.loc[panel["week_start"] == pd.Timestamp("2010-01-10"), "cases"].item()
    assert gap == 0


def test_drop_right_censored_weeks_removes_newest_n() -> None:
    weeks = pd.to_datetime(
        ["2010-01-03", "2010-01-10", "2010-01-17", "2010-01-24"]
    )
    weekly = pd.DataFrame({"uf": ["AC"] * 4, "week_start": weeks, "cases": [1, 1, 1, 1]})

    kept = drop_right_censored_weeks(weekly, n_weeks=2)

    assert kept["week_start"].max() == pd.Timestamp("2010-01-10")


def test_build_dengue_uf_ew_series_on_tiny_parquet(tmp_path: Path) -> None:
    path = tmp_path / "sinan.parquet"
    pd.DataFrame(
        {
            "ew_recorded": [datetime(2010, 1, 3).date()] * 4,
            "ew_notification": [datetime(2010, 1, 3).date()] * 4,
            "ew_symptom_onset": [
                datetime(2010, 1, 3).date(),
                datetime(2010, 1, 3).date(),
                datetime(2010, 1, 10).date(),
                datetime(2010, 1, 17).date(),
            ],
            "final_classification": [10, 5, 10, 10],
            "state_abbrev": ["AC", "AC", "AC", "AC"],
            "case_count": [10, 99, 4, 6],
        }
    ).to_parquet(path)

    # right_censor_weeks=1 drops 2010-01-17; panel covers 2010-01-03 and 2010-01-10
    series = build_dengue_uf_ew_series(
        path, window_start="2010-EW01", right_censor_weeks=1
    )

    assert list(series.columns) == ["uf", "week_start", "cases"]
    assert series["week_start"].max() == pd.Timestamp("2010-01-10")
    assert series.loc[series["week_start"] == "2010-01-03", "cases"].item() == 10
    assert series["cases"].sum() == 14


def test_sunday_of_epiweek_rejects_week_zero() -> None:
    with pytest.raises(ValueError, match="1..53"):
        sunday_of_epiweek(2010, 0)
