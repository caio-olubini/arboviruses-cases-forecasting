"""Load the raw SINAN weekly count extract."""

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = (
    "ew_symptom_onset",
    "final_classification",
    "state_abbrev",
    "case_count",
)


def load_sinan_cases(path: Path | str) -> pd.DataFrame:
    cases = pd.read_parquet(path, columns=list(REQUIRED_COLUMNS))
    missing = set(REQUIRED_COLUMNS) - set(cases.columns)
    if missing:
        raise ValueError(f"SINAN extract missing columns: {sorted(missing)}")

    cases = cases.copy()
    cases["ew_symptom_onset"] = pd.to_datetime(cases["ew_symptom_onset"])
    # Parquet stores this as nullable int8; pandas widens to float when nulls appear.
    cases["final_classification"] = cases["final_classification"].astype("Int8")
    cases["case_count"] = cases["case_count"].astype("int64")
    return cases
