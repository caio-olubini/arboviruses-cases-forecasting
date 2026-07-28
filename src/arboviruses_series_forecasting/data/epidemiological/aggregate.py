"""Roll notifications up to UF × symptom-onset epidemiological week."""

import pandas as pd


def aggregate_by_uf_and_onset_week(cases: pd.DataFrame) -> pd.DataFrame:
    weekly = (
        cases.groupby(["state_abbrev", "ew_symptom_onset"], as_index=False, observed=True)[
            "case_count"
        ]
        .sum()
        .rename(columns={"state_abbrev": "uf", "ew_symptom_onset": "week_start", "case_count": "cases"})
    )
    return weekly.sort_values(["uf", "week_start"], ignore_index=True)


def complete_uf_week_panel(weekly: pd.DataFrame) -> pd.DataFrame:
    """Fill missing UF × week cells with zero so every series is regularly spaced."""
    if weekly.empty:
        return weekly.copy()

    ufs = sorted(weekly["uf"].unique())
    week_starts = pd.date_range(
        weekly["week_start"].min(),
        weekly["week_start"].max(),
        freq="W-SUN",
    )
    panel_index = pd.MultiIndex.from_product([ufs, week_starts], names=["uf", "week_start"])
    panel = (
        weekly.set_index(["uf", "week_start"])
        .reindex(panel_index, fill_value=0)
        .reset_index()
    )
    panel["cases"] = panel["cases"].astype("int64")
    return panel.sort_values(["uf", "week_start"], ignore_index=True)
