# Phase 1 — Unimodal Statistical Baselines

**Project:** Multimodal neural forecasting of dengue in Brazil (MSc / article)
**Purpose of this phase:** make the multimodal result *believable*. The baselines are not a contribution — they are the reference the main model is measured against.

**Inclusion test for everything below:** would a reviewer object if it were missing? If not, cut it.

**Target duration:** 2 weeks.

---

## 0. Open decision (settle before Sprint 1)

**Does the multimodal model output distributions or point forecasts?**

| If | Then |
|---|---|
| Point forecasts | MAE on `log1p` throughout. Never touch WIS. |
| Distributions | CRPS throughout. Same baselines, same table, different scoring function. |

Decide now. Retrofitting the harness later is the expensive version.

---

## 1. Aggregation

One paragraph in the paper, no analysis section.

| Decision | Value |
|---|---|
| Spatial unit | UF (27 federative units) |
| Temporal unit | Epidemiological week |
| Season boundary | EW41 → EW40 |
| Date field | Symptom onset (`DT_SIN_PRI`) |
| Case definition | Probable cases (notified − discarded) |
| Window | EW01 2010 → last complete week |
| Right-censoring | Drop final 12 weeks of the extraction |

**Justification to write:** UF × EW is the established target of the Infodengue–Mosqlimate Dengue Challenge (IMDC), which makes results comparable to a published benchmark set. Right-censoring is required because SINAN notification is delayed — under 90% of cases arrive within 9 weeks and the database stays open ~6 months, so recent weeks in any snapshot are downward-biased.

**Deliverable:** `data/processed/dengue_uf_ew.parquet` + data dictionary.

---

## 2. Exploratory analysis

One figure, three sentences. Nothing else goes in the paper.

**Figure:** heatmap of `log10(I + 1)`, EW × year, faceted/ordered by UF longitude. Shows seasonality, burden gradient, the 2024 anomaly, and west→east timing in a single panel.

**Three sentences to support with numbers:**

1. **Overdispersion** — report the range of variance-to-mean ratio across UFs (one number range). Justifies the log transform.
2. **Annual periodicity** — confirms `m = 52`.
3. **2024 anomaly** — flagged explicitly, so it isn't silently driving error metrics later.

**Tests:** one line stating differencing orders were selected by the standard tests inside `auto.arima`. No stationarity test battery, no per-UF ACF/PACF panels, no wavelets.

> Cut from earlier draft: STL panels, seasonal strength table, wavelet spectra, phase-lag analysis, per-UF stationarity verdicts. All defensible, none load-bearing for a multimodality paper.

**Deliverable:** `notebooks/01_eda.ipynb` + one publication-quality figure.

---

## 3. Metrics and reporting

### Evaluation protocol
- Rolling origin, 6-year fixed training window
- **Horizons: two only** — 4 weeks (operational) and the horizon the multimodal model actually targets (12 or 52)
- Held-out: most recent 2 seasons

### Metrics
| Metric | Role |
|---|---|
| MAE on `log1p` (or CRPS) | Headline. Log scale so São Paulo doesn't dominate the cross-UF average. |
| % improvement vs seasonal naive | Skill score. The honest number. |

**Explicitly dropped:** MAPE (explodes on low-count states), RMSE, coverage tables, log-scale WIS, computational efficiency benchmarks, per-UF metric appendix.

### Reporting format
Single table: **3 baselines × 2 horizons**, two metrics per cell, averaged across UFs and seasons. ~6 numbers total.

**Deliverable:** `src/evaluate.py` — takes `(forecasts, truth)`, returns tidy scores. The multimodal model calls this unchanged. **This is the real artifact of Phase 1.**

---

## 4. Statistical baselines

Reproduce Chen & Moraga's *design*, not their geography: their rolling-window comparative framing, extended from Rio to all 27 UFs.

| # | Model | Why it's in |
|---|---|---|
| 1 | Seasonal naive (lag 52) | Skill-score denominator |
| 2 | Climatology (historical quantiles by EW) | Cheap, genuinely hard to beat at long horizons |
| 3 | ARIMA + Fourier terms on `log1p` | Literature standard. Fourier over SARIMA because `m = 52` is numerically miserable; select K by AICc |

**No covariates in this phase.** Climate, Google Trends and news enter in Phase 2 — that separation is the point of the paper.

**Intervals (only if going probabilistic):** conformal residual quantiles. Works uniformly across all three models.

> Cut from earlier draft: ETS, AR(1)/MA(1), NB-GLM, VAR, SARIMAX. Six models is a baselines paper; three is a baselines section.

**Deliverable:** `results/baseline_scores.parquet`.

---

## 5. Reading — incremental

Three papers. Read one, implement, read the next.

| When | Read | Time | For |
|---|---|---|---|
| Before Sprint 1 | Mosqlimate IMDC 2025 sprint page | 20 min | Target definition (§1) |
| After the EDA figure exists | Chen & Moraga 2025, *Trop Med Health* 53:52 + GitHub repo | 2h | Baseline design template (§4) |
| While writing | Baquero et al. 2018, *PLoS ONE* 13(4):e0195065 | 30 min | How SARIMA-vs-neural is framed in Brazilian dengue literature — your article's skeleton |

**Conditional:**
- Bracher et al. 2021 + Bosse et al. 2023 — **only if** the multimodal model outputs distributions
- Hyndman & Athanasopoulos, *FPP3* ch. 5 — **only if** stuck on Fourier terms

Everything else from the wider literature is citation material for the introduction, not reading needed now.

---

## 6. What "done" looks like

Four artifacts. If all four exist, Phase 1 is closed.

1. **One table** — 3 baselines × 2 horizons, MAE-log and skill vs naive. ~6 numbers. Every later chapter compares against this.
2. **One figure** — the EW × year × UF heatmap.
3. **Three paragraphs of Methods text**, article-ready: target definition, data handling, baseline specification.
4. **A scoring function the multimodal model calls unchanged.**

**Two sentences you must be able to state with evidence:**

- *"Dengue counts across Brazilian UFs are strongly overdispersed with a dominant annual cycle, motivating a log-transformed model with harmonic seasonal terms."*
- *"The best purely statistical baseline achieves X% improvement over seasonal naive at 4 weeks, degrading to Y% at [target horizon]."*

If both hold with numbers behind them, Phase 2 has a defensible target to beat.
