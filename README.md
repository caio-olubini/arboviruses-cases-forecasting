# Arboviruses Series Forecasting

MSc research codebase for **dengue forecasting in Brazil**. Phase 1 builds a credible unimodal statistical baseline at the Infodengue–Mosqlimate Dengue Challenge (IMDC) grain (UF × epidemiological week). Later work adds multimodal neural models; everything here is the reference those models must beat.

---

## Done so far & decisions

**Built**

- SINAN → probable-case panel (`data/processed/dengue_uf_ew.parquet`) with a tested aggregation pipeline
- EDA notebook documenting overdispersion, annual seasonality, and the 2024 anomaly
- Three point-forecast baselines under a shared rolling-origin harness: seasonal naive, climatology, ARIMA + Fourier on `log1p`
- Shared scorer (`score_forecasts`) — MAE on `log1p` + skill vs seasonal naive; later models call this unchanged
- Baseline forecast/score artifacts under `results/`
- Dataset write-up for the article: [`docs/article/dataset.md`](docs/article/dataset.md)

**Locked decisions** (see `config.yml` and the Phase 1 roadmap)

| Choice | Value | Why |
| --- | --- | --- |
| Spatial / temporal grain | 27 UFs × epidemiological week | IMDC-aligned; avoids sparse municipality zeros |
| Case / date definition | Probable cases; symptom onset | Operational surveillance target and epidemic timing |
| Study window | 2010-EW01 → last complete week; drop final 12 weeks | Stable surveillance window; SINAN right-censoring |
| Season | EW41 → EW40 | Held-out evaluation seasons |
| Forecast type / metric | Point forecasts; MAE on `log1p` | Overdispersion; SP/MG must not own the national average |
| Protocol | Rolling origin, 6-year train, horizons 4 & 12, 2 held-out seasons | Operational short horizon + model target horizon |
| Baselines only (Phase 1) | No climate / Trends / news | Covariates are the Phase 2 claim |

Roadmap: [`docs/statistical-baselines-roadmap.md`](docs/statistical-baselines-roadmap.md).

---

## Next steps

- Close Phase 1 article artifacts: one baseline table, one EW×year×UF heatmap, Methods paragraphs on target / handling / baselines
- Phase 2: multimodal neural forecasting (climate, Google Trends, news) scored with the same harness
- Optional later: probabilistic outputs (CRPS) if the main model emits distributions

---

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python ≥ 3.12 (pinned in `.python-version`). Dependencies are locked in `uv.lock`.

```bash
uv sync --frozen
uv run pytest
```

That is enough for a clean clone: the processed panel, IBGE population CSV, and baseline score/forecast tables are tracked. Tests include integrity checks on those artifacts.

Notebooks (optional Jupyter stack from the `dev` group):

```bash
uv sync --frozen --group dev
uv run jupyter notebook notebooks/
```

### Data layout

| Path | In git? | Role |
| --- | --- | --- |
| `data/processed/dengue_uf_ew.parquet` | yes | Forecasting panel (UF × EW) |
| `data/external/ibge_uf_population_2024.csv` | yes | Incidence denominators for figures |
| `results/baseline_*.parquet` | yes | Phase 1 forecast/score tables |
| `data/raw/SINAN_dengue_cases.parquet` | no | Local SINAN snapshot (gitignored) |

To rebuild the panel from a local extract:

```bash
# place extract at data/raw/SINAN_dengue_cases.parquet (see config.yml)
uv run build-dengue-panel
```
---

## Directory tree

```
├── config.yml                 # aggregation, evaluation, paths
├── data/
│   ├── raw/                   # SINAN extract
│   ├── processed/             # UF × EW forecasting panel
│   └── external/              # IBGE population (figures / incidence)
├── docs/
│   ├── article/               # manuscript building blocks
│   ├── figures/
│   └── statistical-baselines-roadmap.md
├── notebooks/
│   ├── 01_eda.ipynb
│   └── 02_baselines.ipynb
├── results/                   # baseline forecasts & scores
├── src/arboviruses_series_forecasting/
│   ├── data/epidemiological/  # load → probable → aggregate → window
│   ├── models/                # seasonal naive, climatology, ARIMA+Fourier
│   ├── metrics/               # score_forecasts (shared harness)
│   └── utils/
└── tests/
```
