# Arboviruses Series Forecasting

MSc research codebase for **dengue forecasting models** in Brazil — statistical baselines first, then multimodal neural forecasting.

## Layout

```
├── config.yml          # project settings (aggregation, eval, paths)
├── data/
│   ├── raw/            # original extracts (e.g. SINAN)
│   ├── processed/      # UF × EW series, model-ready tables
│   └── external/       # covariates / aux sources
├── docs/               # notes, roadmaps, figures
├── notebooks/          # EDA and experiments
├── src/arboviruses_series_forecasting/
│   ├── data/           # load / aggregate / preprocess
│   ├── models/         # baselines + neural models
│   ├── metrics/        # scoring and skill scores
│   └── utils/
└── tests/
```

## Setup

```bash
uv sync
```

## Phase 1

See [docs/statistical-baselines-roadmap.md](docs/statistical-baselines-roadmap.md).
