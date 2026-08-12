# Dataset: Brazilian dengue at UF × epidemiological week

> Base text for manuscripts that use this panel. Numbers match
> `data/processed/dengue_uf_ew.parquet` from the SINAN snapshot in this repository.

**One-line claim.** Probable dengue counts for all 27 Brazilian UFs by epidemiological week of symptom onset — the Infodengue–Mosqlimate Dengue Challenge (IMDC) grain for national forecasting benchmarks [1].

---

## Snapshot


| Quantity                  | Value                                              |
| ------------------------- | -------------------------------------------------- |
| Spatial units             | 27 UFs                                             |
| Temporal unit             | Epidemiological week (Sunday start, CDC-style)     |
| Date field                | Symptom onset                                      |
| Case definition           | Probable = notified − discarded (`CLASSI_FIN ≠ 5`) |
| Window (current snapshot) | 2010-EW01 → week starting 2026-04-19               |
| Panel size                | 22,977 UF–weeks (851 weeks × 27 UFs)               |
| Total probable cases      | 22,657,574                                         |
| Zero-filled cells         | 308 (1.34%)                                        |
| Dengue season             | EW41 → EW40                                        |
| Right-censoring           | Drop final 12 weeks of extract                     |
| Population (optional)     | IBGE SIDRA 6579, 2024-07-01 (~212.6 M)             |


---



## Files


| Role              | Path                                        | Notes                            |
| ----------------- | ------------------------------------------- | -------------------------------- |
| Raw SINAN extract | `data/raw/SINAN_dengue_cases.parquet`       | Aggregated notification counts   |
| Processed panel   | `data/processed/dengue_uf_ew.parquet`       | Forecasting target               |
| UF population     | `data/external/ibge_uf_population_2024.csv` | Incidence figures only (Phase 1) |
| Build pipeline    | `src/.../epidemiological/pipeline.py`       | `build_dengue_uf_ew_series`      |


---



## Column dictionaries



### Raw extract (`SINAN_dengue_cases.parquet`)


| Column                 | Type              | Meaning                                                |
| ---------------------- | ----------------- | ------------------------------------------------------ |
| `ew_recorded`          | date (week start) | Epidemiological week of database recording             |
| `ew_notification`      | date (week start) | Epidemiological week of notification                   |
| `ew_symptom_onset`     | date (week start) | Epidemiological week of symptom onset (**index used**) |
| `final_classification` | int / missing     | SINAN `CLASSI_FIN`; `5` = discarded                    |
| `state_abbrev`         | str               | UF abbreviation (27 values)                            |
| `case_count`           | int               | Count in that cell of the extract                      |


Source: SINAN (Sistema de Informação de Agravos de Notificação) [2]. Probable cases are notified suspected dengue excluding discarded cases.

### Processed panel (`dengue_uf_ew.parquet`)


| Column        | Type     | Meaning                                   |
| ------------- | -------- | ----------------------------------------- |
| `uf`          | str      | Federative unit abbreviation              |
| `week_start`  | datetime | Sunday opening the epidemiological week   |
| `cases`       | int      | Probable dengue count; `0` if zero-filled |
| `ew_year`     | int      | Epidemiological year of `week_start`      |
| `ew`          | int      | Epidemiological week number (1–53)        |
| `log10_cases` | float    | `log10(cases + 1)` (figures)              |


---



## Construction


| Decision         | Value                           | Purpose                                             |
| ---------------- | ------------------------------- | --------------------------------------------------- |
| Spatial unit     | UF (27)                         | IMDC alignment; avoids sparse municipality zeros    |
| Temporal unit    | Epidemiological week            | Brazilian epi-week reporting                        |
| Date field       | Symptom onset                   | Epidemic timing, not system lag                     |
| Case definition  | Probable (notified − discarded) | Operational surveillance target                     |
| Study start      | 2010-EW01                       | Stable surveillance window in this codebase         |
| Right-censoring  | Final 12 weeks dropped          | Open snapshots under-count recent weeks             |
| Missing UF–weeks | Zero-filled                     | Rectangular panel for forecasting                   |
| Season boundary  | EW41 → EW40                     | Held-out evaluation seasons                         |
| Population       | IBGE 2024-07-01 (~212.6 M)      | Cases/million for figures — not a Phase 1 covariate |




### Pipeline (ordered)


| Step | Operation                                                               |
| ---- | ----------------------------------------------------------------------- |
| 1    | Load SINAN extract                                                      |
| 2    | Drop discarded (`CLASSI_FIN = 5`); keep other / missing classifications |
| 3    | Aggregate `case_count` → UF × `ew_symptom_onset`                        |
| 4    | Clip to study start (`2010-EW01`)                                       |
| 5    | Drop rightmost 12 weeks                                                 |
| 6    | Complete UF × week grid; fill gaps with `cases = 0`                     |


**Right-censoring.** In practice, fewer than 90% of dengue cases are reported within 9 weeks, and open SINAN dumps revise recent counts for months [3]. Scoring on the trailing edge without a censor cut evaluates models against incomplete truth.

---



## Empirical properties

Facts that fix modelling and metric choices.


| Property                                            | Estimate (this panel)                 | Modelling consequence                                     |
| --------------------------------------------------- | ------------------------------------- | --------------------------------------------------------- |
| Overdispersion (weekly VMR by UF)                   | 105 – 44,933 (median ≈ 1,129)         | Headline error on `log1p`; heatmaps on `log10(cases + 1)` |
| Seasonal peak / trough (mean profile, years < 2024) | EW15 / EW39                           | Annual epidemic shape                                     |
| Autocorr of `log1p` (median UF)                     | lag 52 ≈ 0.51; lag 26 ≈ −0.13         | Seasonal period `m = 52`                                  |
| Zero-week share                                     | 1.34% overall; 0 – ≈10% by UF         | Sparsity is state-level, not national                     |
| Max UF–week                                         | SP, week of 2024-05-05: 156,074 cases | Extreme peak in evaluation era                            |




### Calendar-year burden (probable cases)


| Year | Cases     | Note                                    |
| ---- | --------- | --------------------------------------- |
| 2024 | 6,540,531 | Out-of-envelope outbreak (~3.9× 2023)   |
| 2015 | 1,712,992 | Prior high year in panel                |
| 2023 | 1,696,058 | Immediate pre-anomaly year              |
| 2025 | 1,613,560 | Partial / post-peak in current snapshot |
| 2019 | 1,552,924 | —                                       |


Held-out dengue seasons in the current protocol include **2024** and **2025** — evaluation is intentionally stress-tested by the anomaly, not shielded from it.

---



## Scope and limits


| This panel is                      | This panel is not                  |
| ---------------------------------- | ---------------------------------- |
| Probable notified dengue           | Lab-confirmed incidence alone      |
| UF × epi-week of onset             | Municipality or month resolution   |
| Dengue only                        | Chikungunya / Zika                 |
| One SINAN snapshot                 | A continuously refreshed live feed |
| 2024 IBGE denominators for figures | Year-varying demographic series    |


**Still in the counts:** classification error, under-notification, and differential testing by UF and year. **Rebuilding from a later dump** shifts the right edge and can revise weeks that were still open in earlier extracts.

**Why keep it.** The target is operational state-week dengue as Brazil records it — delayed, overdispersed, and extreme in 2024 — which is what a forecasting model must beat to matter outside a cleaned textbook series.

---



## References

1. Mosqlimate / Infodengue. *Instructions — 3rd Infodengue–Mosqlimate Dengue Challenge (IMDC)*. [https://sprint.mosqlimate.org/instructions/](https://sprint.mosqlimate.org/instructions/) (accessed 2026-08-12).
2. Ministério da Saúde (Brazil). *Sistema de Informação de Agravos de Notificação (SINAN)*. [https://www.gov.br/saude/pt-br/composicao/svsa/sistemas-de-informacao/sinan/sinan](https://www.gov.br/saude/pt-br/composicao/svsa/sistemas-de-informacao/sinan/sinan) (accessed 2026-08-12).
3. Bastos, L. S. *et al.* A modelling approach for correcting reporting delays in disease surveillance data. *Stat. Med.* **38**, 4363–4377 (2019). [https://doi.org/10.1002/sim.8303](https://doi.org/10.1002/sim.8303)

---

*LLM-based tools were used to assist with drafting and formatting; all experimental design, analysis, interpretation, and conclusions are the author's own.*