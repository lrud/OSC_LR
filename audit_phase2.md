# Phase 2 Audit: Q1 Employment Analysis

**Audit Date:** 2026-04-20
**Notebook:** `notebooks/Q1_Employment_Analysis.ipynb`

---

## Audit Gate 2 Checklist

| Check | Status | Detail |
|-------|--------|--------|
| Only same-month comparisons used (Feb vs Feb) | PASS | No month-to-month comparisons with NSA data |
| Data revision date noted (March 2025 benchmark) | PASS | Noted in cross-reference cell; data downloaded April 20, 2026 |
| Hand-verified YoY calculation | PASS | Health Care/Social Asst: Feb 2026 = 1,017,700, Feb 2025 = 1,041,900 → -24,200 / -2.32% |
| Hand-verified 5-year calculation | PASS | Same sector: Feb 2021 = 783,200 → +234,500 / +29.94% |
| COVID context explicitly addressed | PASS | Multiple markdown cells; 5-year table header; Chart 2 subtitle; narrative sections |
| Total nonfarm cross-referenced | PASS | 4,791,000 consistent with BLS, NYC Comptroller, and NYS DOL sources |
| Narrative uses "possible reasons" language | PASS | "likely due to", "may reflect", "driven by" — no causal claims |
| All tables and charts rendering | PASS | 2 tables, 3 charts, all with supersectors + Total Nonfarm |

---

## Gotcha Verification

| Gotcha | Status |
|--------|--------|
| G1: Wrong geography (MSA vs NYC) | AVOIDED — AREANAME == 'New York City' |
| G2: Not latest month | AVOIDED — Feb 2026 confirmed in Phase 1 |
| G3: Month-to-month with NSA data | AVOIDED — Feb vs Feb only |
| G4: Pre-revision data | AVOIDED — Downloaded April 20, 2026, post-March 2025 benchmark |
| G5: COVID baseline not addressed | ADDRESSED — Multiple narrative sections and chart annotations |
| G6: NAICS range codes misunderstood | AVOIDED — 21+23, 31-33, 44-45, 48-49 handled correctly |

---

## Supersector Source

BLS NAICS Supersector definitions:
https://www.bls.gov/sae/additional-resources/naics-supersectors-for-ces-program.htm

| Supersector Code | Name | NAICS Sectors |
|-----------------|------|---------------|
| 40 | Trade, Transportation, and Utilities | 22, 42, 44-45, 48-49 |
| 55 | Financial Activities | 52, 53 |
| 60 | Professional and Business Services | 54, 55, 56 |
| 65 | Education and Health Services | 61, 62 |
| 70 | Leisure and Hospitality | 71, 72 |

---

## Cross-Reference Sources

1. **BLS Northeast Region**: https://www.bls.gov/regions/northeast/new_york.htm
2. **NYC Comptroller "What Is Going on with NYC Jobs?" (Feb 2026)**: https://comptroller.nyc.gov/reports/what-is-going-on-with-nyc-jobs/
3. **BLS CES Benchmark Article (Feb 2026)**: https://www.bls.gov/web/empsit/cesbmart.htm
4. **NYS DOL CES**: https://dol.ny.gov/current-employment-statistics-0
5. **BLS NAICS Supersector definitions**: https://www.bls.gov/sae/additional-resources/naics-supersectors-for-ces-program.htm

---

## Cross-Reference Values

| Metric | Value | Source |
|--------|-------|--------|
| NYC Total Nonfarm (Feb 2026) | 4,791,000 | NYS DOL ces.csv |
| NYC Total Nonfarm (Feb 2025) | 4,830,400 | NYS DOL ces.csv |
| NYC Total Nonfarm YoY | -39,400 (-0.82%) | Computed |
| NYC Private Sector (Feb 2026) | 4,179,700 | Total Nonfarm - Government |
| NYC Private Sector YoY | -48,900 | Computed |
| Health Care YoY spot-check | -24,200 (-2.32%) | Hand-verified: 1,017,700 - 1,041,900 |
| Health Care 5yr spot-check | +234,500 (+29.94%) | Hand-verified: 1,017,700 - 783,200 |

Note: Data downloaded April 20, 2026, includes March 2025 benchmark revisions. NYC Comptroller projects further downward revisions.

---

## Verdict

**Phase 2: PASS — all checks clear.**
