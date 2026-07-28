"""Case-definition filters for SINAN dengue notifications."""

import pandas as pd

# SINAN CLASSI_FIN: 5 = discarded. Probable = notified − discarded.
DISCARDED_CLASSIFICATION = 5


def keep_probable_cases(cases: pd.DataFrame) -> pd.DataFrame:
    # Missing CLASSI_FIN is still a notification; only explicit discards are removed.
    is_discarded = cases["final_classification"].eq(DISCARDED_CLASSIFICATION).fillna(False)
    return cases.loc[~is_discarded].copy()
