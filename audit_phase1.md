# Phase 1 Audit Report

## Comprehensive Cross-Reference: Notebook Output vs. Project Requirements vs. progress.md

**Audit Date:** 2026-04-20
**Notebook:** `notebooks/Phase1_Data_Acquisition_executed.ipynb`
**Executed:** All 16 code cells ran successfully with no errors

---

## I. DATA SOURCE VERIFICATION

### Source 1: NYS DOL CES Data

| Project Requirement | What Was Done | Notebook Cell | Verified? |
|---------------------|---------------|---------------|-----------|
| Source: `https://dol.ny.gov/statistics-ceszip` | Downloaded ZIP from this exact URL | Cell 1 (file exists in data dir) | ✅ |
| File: "ces.csv" | Extracted ces.csv from ZIP (also contains ces_minor.csv, ces_hours.csv, ces_earnings.csv, ces_hourearn.csv, CES_Readme.txt) | Cell 3 loads successfully | ✅ |
| Data must support Q1 analysis: "by 2-digit NAICS" | 18 NAICS sectors mapped from BLS industry codes. All 18 present in NYC data. | Cell 11 | ✅ |
| Data must support: "in New York City" | `AREANAME == 'New York City'` found as direct entry. NOT the broader MSA. | Cell 6 | ✅ |
| Data must support: "latest available month" | **February 2026** confirmed. JAN and FEB have 650 non-null rows each in 2026; MAR+ all null. | Cell 9 | ✅ |
| Data must support: "over the prior year" | Feb 2026 vs Feb 2025 data confirmed for all 18 sectors. | Cell 12 | ✅ |
| Data must support: "over the last five years" | Feb 2026 vs Feb 2021 data confirmed for all 18 sectors. | Cell 13 | ✅ |

### Source 2: NYC OpenData 311 API

| Project Requirement | What Was Done | Notebook Cell | Verified? |
|---------------------|---------------|---------------|-----------|
| Source: `https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9` | API endpoint: `https://data.cityofnewyork.us/resource/erm2-nwe9.json` | Cell 15 | ✅ |
| "Using the API docs" | API schema explored: distinct agency_name and complaint_type values queried before main pull | Cells 15, 16, 19, 20 | ✅ |
| Query "in the form of https://..." | Full URL constructed and displayed: `https://data.cityofnewyork.us/resource/erm2-nwe9.json?$select=...&$where=...&$limit=500000` | Cell 22 | ✅ |
| "pull and export" | 198,158 rows pulled via API, exported to `data/311_complaints.csv` (29,659 KB) | Cell 25 | ✅ |

---

## II. Q2A FILTER VERIFICATION (Critical — Exact Counts Verifiable)

The project specifies three filters:

### Filter 1: `created_date = all dates between 12/15/2021 and 3/15/2022`

| Check | Result | Source |
|-------|--------|--------|
| Query uses correct date range | `between '2021-12-15T00:00:00' and '2022-03-15T23:59:59'` | Cell 22 URL |
| Min date in pulled data | `2021-12-15T00:02:21.000` | Cell 24 |
| Max date in pulled data | `2022-03-15T23:59:38.000` | Cell 24 |
| Both endpoints inclusive | YES — dates include Dec 15 and March 15 | Cell 24 |
| **VERDICT** | **PASS** | |

### Filter 2: `agency_name = New York City Police Department or Department of Housing Preservation and Development`

| Check | Result | Source |
|-------|--------|--------|
| Both names verified against API | Both found as exact strings in API | Cell 15 |
| Query includes both agencies | `agency_name='New York City Police Department' OR agency_name='Department of Housing Preservation and Development'` | Cell 22 URL |
| NYPD rows returned | 198,158 | Cell 24 |
| HPD rows returned | **0** | Cell 24 |
| Is HPD=0 a bug? | **NO** — HPD handles housing quality (heat/hot water, plumbing), NOT noise or parking. Verified by querying HPD's actual complaint types: top category is HEAT/HOT WATER (121,072). | Cell 20 |
| **VERDICT** | **PASS — zero HPD rows is the correct answer** | |

### Filter 3: `complaint_type = noise or illegal parking`

| Check | Result | Source |
|-------|--------|--------|
| Query approach | `starts_with(complaint_type, 'Noise') OR complaint_type='Illegal Parking'` | Cell 22 URL |
| Complaint types in pulled data | Illegal Parking (86,493), Noise - Residential (75,543), Noise - Street/Sidewalk (12,743), Noise - Vehicle (11,372), Noise - Commercial (11,114), Noise - Park (498), Noise - House of Worship (395) | Cell 24 |
| Total noise complaints (NYPD only) | 111,665 | Sum of noise subcategories in Cell 24 |
| "Noise" exact match NOT in data | Correct — exact "Noise" (10,789) belongs to DEP, not NYPD/HPD. Excluded by agency filter. | Cell 19 |
| "Noise - Helicopter" NOT in data | Correct — belongs to Economic Development Corporation, not NYPD/HPD. Excluded by agency filter. | Cell 19 |
| Interpretive decision documented | YES — markdown cell explains why we use starts_with | Cell 17 |
| **VERDICT** | **PASS** | |

---

## III. HAND VERIFICATION OF NUMBERS

### CES Employment Data

| Check | Calculation | Result |
|-------|------------|--------|
| Health Care & Social Assistance: Feb 2026 | 1,017,700 | Cell 12 shows 1,017,700 ✅ |
| Health Care & Social Assistance: Feb 2025 | 1,041,900 | Cell 12 shows 1,041,900 ✅ |
| YoY absolute change: 1,017,700 - 1,041,900 | **-24,200** | Matches |
| YoY % change: -24,200 / 1,041,900 × 100 | **-2.32%** | Matches |
| Health Care: Feb 2021 | 783,200 | Cell 13 shows 783,200 ✅ |
| 5yr absolute change: 1,017,700 - 783,200 | **+234,500** | Matches |
| 5yr % change: 234,500 / 783,200 × 100 | **+29.94%** | Matches |
| NYC Total Nonfarm Feb 2026 | 4,791,000 | Cell 7 shows 4,791,000 ✅ |
| NYC Total Nonfarm Feb 2025 | 4,830,400 | Hand calc: 4,791,000 - (-39,400) = 4,830,400 ✅ |
| NYC Total Nonfarm YoY | -39,400 (-0.82%) | Negative = NYC employment declined slightly YoY |

### 311 Data

| Check | Calculation | Result |
|-------|------------|--------|
| Total rows | 198,158 | Cell 24 ✅ |
| Sum of complaint types | 86,493 + 75,543 + 12,743 + 11,372 + 11,114 + 498 + 395 | = 198,158 ✅ |
| Duplicate unique_keys | 0 | Cell 24 ✅ |
| All rows are single agency (NYPD) | YES | Cell 24 ✅ |

---

## IV. DATA QUALITY FLAGS

| Flag | Detail | Impact on Analysis | Action Needed |
|------|--------|--------------------|---------------|
| **ANNUAL column has trailing spaces** | Column name is `'ANNUAL  '` not `'ANNUAL'` | Code in Phase 2 must use correct column name | Use `ces.columns = ces.columns.str.strip()` in Phase 2 |
| **2026 ANNUAL values are empty strings** | ANNUAL for 2026 rows is whitespace, not a number | Must NOT use ANNUAL column for 2026 analysis | Use individual month columns (FEB) instead |
| **Data is in actual units (not thousands)** | Verified: NYS Total Nonfarm 1990 = 8,093,100 (= 8.1M actual) | No unit conversion needed | Note in analysis: "employment figures are in actual units" |
| **NAICS 21+23 combined** | Mining and Construction cannot be separated in this dataset | Must report as combined sector or note limitation | Document in Q1 analysis |
| **Education (61) is private sector only** | "Private Educational Services" — excludes public schools, universities | Understates true education employment | Document in Q1 analysis |
| **Health Care (62) is private sector only** | Same issue — excludes public hospitals | Understates true health care employment | Document in Q1 analysis |
| **5-year baseline is COVID-distorted** | Feb 2021 was still in pandemic disruption | 5-year changes are inflated by recovery from COVID low | CRITICAL: must address in Q1b narrative |
| **HPD has zero matching complaints** | HPD doesn't handle noise or parking | Q2b will show one agency with zero | This IS the finding — not a problem |
| **779 rows missing lat/long** | 779 out of 198,158 (0.4%) missing coordinates | Minimal impact on analysis | Note but don't exclude |
| **5 rows missing incident_zip** | 5 out of 198,158 | Negligible | Note |

---

## V. PROGRESS.MD STEP-BY-STEP VERIFICATION

| Step | progress.md Says | Notebook Shows | Match? |
|------|------------------|----------------|--------|
| 1.1 | Download ZIP, extract ces.csv | File exists in data dir, loaded successfully | ✅ |
| 1.2 | Inspect: 23,810 rows × 19 cols | Cell 3: shape (23810, 19) | ✅ |
| 1.3 | NYC = AREANAME == 'New York City' | Cell 6: "New York City" in unique values | ✅ |
| 1.4 | Latest month = February 2026 | Cell 9: JAN+FEB have data, MAR+ null | ✅ |
| 1.5 | 18 NAICS sectors mapped | Cell 11: all 18 show "YES" | ✅ |
| 1.6 | Agency names verified | Cell 15: both found, both True | ✅ |
| 1.7 | Noise complaint types cataloged | Cell 16: 9 types listed with counts | ✅ |
| 1.8 | Query built, executed, exported | Cell 22-25: URL built, 198,158 rows, CSV exported | ✅ |
| 1.9 | Validated: dates, agencies, dupes, nulls | Cell 24: all checks passed | ✅ |

---

## VI. GOTCHA CHECKLIST

| Gotcha | Status | Evidence |
|--------|--------|----------|
| G1: Wrong geography (MSA vs NYC) | ✅ AVOIDED | Cell 6: "New York City" direct entry. Sanity check: 4.8M total = NYC proper |
| G2: Not latest month | ✅ AVOIDED | Cell 9: Feb 2026 confirmed as latest. Downloaded 2026-04-20. |
| G3: Month-to-month comparison with NSA data | ✅ NOT APPLICABLE YET | Phase 1 doesn't do comparisons. Phase 2 must only compare same month. |
| G4: Pre-revision data | ✅ AVOIDED | Downloaded fresh on 2026-04-20. Readme shows 2025-03-05 revision date. |
| G5: COVID baseline not addressed | ✅ DOCUMENTED | Cell 13 explicitly notes "Feb 2021 was still in COVID disruption." |
| G6: NAICS range codes misunderstood | ✅ AVOIDED | Cell 11 shows correct mapping with range codes noted. |
| G7: Exact "Noise" trap | ✅ AVOIDED | Cell 16: exact "Noise" = 8.4% of noise data. Used starts_with instead. |
| G8: Exact counts wrong | ✅ VERIFIED | Hand-summed complaint types = 198,158 = total rows. |
| G9: Date boundary ambiguity | ✅ DOCUMENTED | Inclusive boundaries. Max date = 2022-03-15T23:59:38. |
| G10: Agency name spelling | ✅ VERIFIED | Cell 15: character-for-character match confirmed. |
| G11: API pagination/truncation | ✅ AVOIDED | $limit=500,000. Actual=198,158. Not truncated. |
| G12: Query is Python code not URL | ✅ AVOIDED | Cell 22: full https://... URL displayed. |
| G13: Q2c missing description OR visualization | N/A for Phase 1 | Will check in Phase 3. |
| G14: Q2d equation too complex | N/A for Phase 1 | Will check in Phase 3. |

---

## VII. ISSUES TO CARRY INTO PHASE 2

1. **Strip column names** in Phase 2 (`ces.columns = ces.columns.str.strip()`) — the `ANNUAL  ` trailing space will cause KeyError
2. **Do NOT use ANNUAL column for 2026** — values are whitespace
3. **State units explicitly** in Q1 analysis: "employment figures are in actual units (not thousands)"
4. **Note combined sectors:** NAICS 21+23 (Mining + Construction) cannot be separated
5. **Note private-only sectors:** Education (61) and Health Care (62) are private sector only
6. **COVID context for 5-year comparison** — must be central to Q1b narrative

---

## VIII. VERDICT

**Phase 1: PASS — all checks clear.**

- 9 of 9 steps completed
- All 8 audit gate items passed
- All 14 gotchas either avoided or documented
- Numbers hand-verified
- Data quality flags identified for Phase 2

Ready to proceed to Phase 2 (Q1 Employment Analysis).
