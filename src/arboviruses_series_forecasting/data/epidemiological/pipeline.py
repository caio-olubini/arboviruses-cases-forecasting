"""Orchestrate SINAN aggregation into a UF × epidemiological-week panel."""

from pathlib import Path

import pandas as pd

from arboviruses_series_forecasting.data.epidemiological.aggregate import (
    aggregate_by_uf_and_onset_week,
    complete_uf_week_panel,
)
from arboviruses_series_forecasting.data.epidemiological.load import load_sinan_cases
from arboviruses_series_forecasting.data.epidemiological.probable import (
    keep_probable_cases,
)
from arboviruses_series_forecasting.data.epidemiological.window import (
    clip_to_study_window,
    drop_right_censored_weeks,
)


def build_dengue_uf_ew_series(
    sinan_path: Path | str,
    *,
    window_start: str = "2010-EW01",
    right_censor_weeks: int = 12,
) -> pd.DataFrame:
    """Probable dengue counts by UF and symptom-onset epidemiological week."""
    cases = load_sinan_cases(sinan_path)
    probable = keep_probable_cases(cases)
    weekly = aggregate_by_uf_and_onset_week(probable)
    started = clip_to_study_window(weekly, start=window_start)
    observed = drop_right_censored_weeks(started, n_weeks=right_censor_weeks)
    return complete_uf_week_panel(observed)
