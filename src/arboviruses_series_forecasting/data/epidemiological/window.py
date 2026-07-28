"""Study-window and right-censoring rules for the UF × EW panel."""

from datetime import date, timedelta

import pandas as pd

# SINAN / Brazilian epi weeks start on Sunday (CDC-style), matching this extract.


def parse_epiweek_label(label: str) -> tuple[int, int]:
    """Parse labels like ``2010-EW01`` into ``(year, week)``."""
    year_text, week_text = label.upper().split("-EW")
    return int(year_text), int(week_text)


def sunday_of_epiweek(year: int, week: int) -> pd.Timestamp:
    """Sunday that opens CDC epidemiological week ``week`` of ``year``."""
    if week < 1 or week > 53:
        raise ValueError(f"Epidemiological week must be in 1..53, got {week}")

    # CDC week 1 is the Sunday-start week that contains the year's first Thursday.
    jan1 = date(year, 1, 1)
    days_until_thursday = (3 - jan1.weekday()) % 7
    first_thursday = jan1 + timedelta(days=days_until_thursday)
    week1_sunday = first_thursday - timedelta(days=4)
    return pd.Timestamp(week1_sunday + timedelta(weeks=week - 1))


def epiweek_of(week_start: pd.Series) -> pd.DataFrame:
    """Map Sunday week-starts to CDC ``ew_year`` and ``ew`` (1–53)."""
    week_start = pd.to_datetime(week_start)
    # Epi-year follows the Thursday inside the Sunday-start week.
    thursday = week_start + pd.Timedelta(days=4)
    ew_year = thursday.dt.year
    week1_sunday = ew_year.map(lambda year: sunday_of_epiweek(int(year), 1))
    ew = ((week_start - week1_sunday).dt.days // 7) + 1
    return pd.DataFrame({"ew_year": ew_year.to_numpy(), "ew": ew.to_numpy()})


def clip_to_study_window(weekly: pd.DataFrame, *, start: str) -> pd.DataFrame:
    year, week = parse_epiweek_label(start)
    window_start = sunday_of_epiweek(year, week)
    return weekly.loc[weekly["week_start"] >= window_start].copy()


def drop_right_censored_weeks(weekly: pd.DataFrame, *, n_weeks: int) -> pd.DataFrame:
    """Drop the newest ``n_weeks`` of the extract — recent SINAN weeks are downward-biased."""
    if n_weeks < 0:
        raise ValueError(f"right_censor_weeks must be >= 0, got {n_weeks}")
    if weekly.empty or n_weeks == 0:
        return weekly.copy()

    last_kept_week = weekly["week_start"].max() - pd.Timedelta(weeks=n_weeks)
    return weekly.loc[weekly["week_start"] <= last_kept_week].copy()
