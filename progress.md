# Project Progress & Specification

# Bureau of Tax and Economic Analysis — Quantitative Research Project

---

## I. PROJECT REQUIREMENTS (Verbatim)

### Context
"The Bureau of Tax and Economic Analysis is looking for an individual who can provide support on its quantitative research pertaining to issues facing New York City."

### Data Sources
1. **NYS DOL CES Data**
   - https://dol.ny.gov/current-employment-statistics-0
   - https://dol.ny.gov/statistics-ceszip ("ces.csv")
2. **NYC OpenData 311 Service Requests**
   - https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9

### Q1: Employment Statistics
> "Using the New York State Department of Labor's employment statistics data for the latest available month,
> a) Discuss which major industries (by 2-digit NAICS) in New York City changed the most over the prior year. Describe possible reasons why these industries experienced greater change than other industries.
> b) How was the change that these industries experienced over the last year different from what they experienced over the last five years? Please include all analysis (calculations, tables, charts, etc.) in your response to this question."

### Q2: 311 Service Requests
> "Using NYC OpenData for 311 service requests,
> a) Using the API docs, pull and export only the following data. Please include the exact query that you used (in the form of https://...) in your response to this question.
>   1. created_date = all dates between 12/15/2021 and 3/15/2022
>   2. agency_name = New York City Police Department or Department of Housing Preservation and Development
>   3. complaint_type = noise or illegal parking
> b) Based on the data you pulled, how many complaints were there for each agency and complaint type? Please include all analysis (calculations, tables, charts, etc.) in your response to this question.
> c) Describe one way to visualize this data and include the visualization in your response. What do you want policymakers to know about your findings?
> d) Ask one research question about this data; discuss additional data that you would merge with this dataset to answer your question and write a simple equation that shows the relationship. Why is studying that relationship important for policymaking?"

---

## II. DATA SOURCE INTELLIGENCE

### Source 1: ces.csv (NYS DOL)

**What it is:** ZIP file containing not seasonally adjusted employment, hours, and earnings data by NAICS for NYS, metro areas, and counties. Historical back to 1990.

**Download URL:** https://dol.ny.gov/statistics-ceszip

**Key facts from documentation:**
- Based on survey of 15,400+ businesses in NYS
- Measures jobs by "place of work" — excludes self-employed, unpaid family workers, private household employees
- NOT seasonally adjusted → must compare same month across years only
- Recently revised: April 2023–December 2024 data was re-benchmarked and released March 13, 2025
- NAICS 2022 is current classification version
- 2-digit NAICS sectors include range codes: Manufacturing (31-33), Retail (44-45), Transportation (48-49)

**Unknowns (must resolve on inspection):**
- Exact column names and schema
- How "New York City" is labeled as an area (could be "New York City", "NYC", or need to aggregate boroughs)
- What the latest available month actually is
- How 2-digit NAICS codes are formatted (e.g., "31-33" vs "31,32,33")

### Source 2: NYC 311 API (Socrata)

**Dataset page:** https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9

**API docs:** https://dev.socrata.com/foundry/data.cityofnewyork.us/erm2-nwe9

**API endpoint (SODA 2.0):** `https://data.cityofnewyork.us/resource/erm2-nwe9.json`

**Key facts from documentation:**
- Socrata Open Data API (SODA) — SoQL query language
- Columns include: `unique_key`, `created_date` (floating_timestamp), `agency`, `agency_name` (text), `complaint_type` (text), `borough`, `incident_zip`, etc.
- Default limit is 1,000 rows — MUST set `$limit` explicitly
- API v3.0 also available via POST to `/api/v3/views/erm2-nwe9/query.json`
- Dataset updated daily

**Critical: `complaint_type` values for "noise":**
The 311 system has subcategories:
- "Noise - Residential"
- "Noise - Commercial"
- "Noise - Street/Sidewalk"
- "Noise - Vehicle"
- "Noise - Helicopter"
- Others possible
- "Noise" as exact value may have very few or zero records

**Our decision:** Capture ALL noise subcategories via `starts_with(complaint_type, 'Noise')`. Also document what an exact match would yield. This is the most defensible interpretation.

**Critical: `agency_name` exact values:**
Must verify against data, but project provides:
- "New York City Police Department"
- "Department of Housing Preservation and Development"

---

## III. IDENTIFIED GOTCHAS & TRICKS

The Bureau of Tax and Economic Analysis works with this data daily. They likely have internal answers. Everything must be verifiable.

### Q1 Gotchas

| # | Gotcha | Why It's Dangerous | How They'd Catch It |
|---|--------|-------------------|---------------------|
| G1 | **Wrong geography** — CES data has "New York City" AND "New York-Newark-Jersey City MSA." MSA includes NJ/PA suburbs. NYC total employment is ~4.5M; MSA is ~10M. | They know the NYC figure by heart. | Totals off by ~40% = instant disqualifier. |
| G2 | **Not using the actual latest month** — grabbing whatever month is in a cached download without checking the website. | They know the release schedule. | Stale data = looks careless. |
| G3 | **Month-to-month comparison with NSA data** — ces.csv is not seasonally adjusted. Comparing March to February is meaningless. Must compare March to March. | This is Economics 101 for their team. | Any month-over-month comparison = disqualifier. |
| G4 | **Pre-revision data** — NYS DOL revised Apr 2023–Dec 2024 in March 2025. Old cached files have stale numbers. | They issued the revision. | Numbers don't match their revised figures. |
| G5 | **COVID baseline for 5-year lookback** — If latest month is ~early 2026, 5 years back is ~early 2021 — still COVID-disrupted. Not mentioning this = shallow analysis. | They chose (or are aware of) this time range. | Omitting COVID context = missed the point. |
| G6 | **NAICS range codes** — Manufacturing is 31-33, Retail is 44-45, Transportation is 48-49. Treating "31" as a standalone 2-digit code misclassifies. | They classify industries daily. | Misclassified sectors = obvious error. |

### Q2 Gotchas

| # | Gotcha | Why It's Dangerous | How They'd Catch It |
|---|--------|-------------------|---------------------|
| G7 | **"noise" as exact complaint_type** — "Noise" exact may barely exist. Most are "Noise - Residential", "Noise - Commercial", etc. Exact match could yield near-zero results. | They know the exact breakdown. | Reporting "12 noise complaints" when there are 50,000+ = incompetent. |
| G8 | **Exact counts are verifiable** — They can run the same query in 30 seconds. All counts must match. | The data is public and stable. | Any count discrepancy = credibility problem. |
| G9 | **Date boundary: inclusive vs. exclusive** — "between 12/15/2021 and 3/15/2022" — does March 15 count or not? | Different interpretations → different counts. | Total row count either matches or doesn't. |
| G10 | **Agency name spelling** — Using "NYPD" instead of "New York City Police Department" = zero results. | They gave full names in the prompt. | Zero results for an agency = obvious error. |
| G11 | **API pagination / $limit** — SODA defaults to 1,000 rows. Forgetting `$limit` = silently truncated data = all counts wrong. | They know the dataset has millions of rows. | Total of exactly 1,000 = forgot the limit. |
| G12 | **Query must be a URL** — "in the form of https://..." — showing Python code instead = didn't follow instructions. | The instruction is explicit. | No URL = didn't read the question. |
| G13 | **Q2c wants BOTH description AND visualization** — "Describe one way to visualize this data AND include the visualization." | Two deliverables in one question. | Missing either = incomplete answer. |
| G14 | **Q2d says "simple equation"** — The word "simple" is doing work. Overly complex model = didn't follow instructions. | They chose the word "simple" deliberately. | Multi-equation structural model = missed the point. |

---

## IV. EXECUTION PHASES

### Phase 1: Data Acquisition & Inspection

| Step | Action | Maps To | Status |
|------|--------|---------|--------|
| 1.1 | Download ZIP from `https://dol.ny.gov/statistics-ceszip`, extract `ces.csv` | Data Source 1: "ces.csv" | ✅ Done — file downloaded 2026-04-20, 810KB zip, 6.2MB csv |
| 1.2 | Inspect ces.csv: print column names, data types, sample rows | Preparation for Q1a ("by 2-digit NAICS", "in New York City") | ✅ Done — 23,810 rows × 19 cols |
| 1.3 | Print all unique `Area` values — identify how NYC is labeled | Q1a: "in New York City" | ✅ Done — **AREANAME == 'New York City'** (not MSA) |
| 1.4 | Print max date in data — confirm "latest available month" | Q1a: "for the latest available month" | ✅ Done — **February 2026** (JAN+FEB have data, MAR+ null) |
| 1.5 | Print all unique NAICS codes at 2-digit level — confirm format of range codes (31-33, 44-45, 48-49) | Q1a: "by 2-digit NAICS" | ✅ Done — BLS codes map to NAICS sectors; 18 sectors mapped |
| 1.6 | Test-query 311 API: `SELECT DISTINCT agency_name` in date range | Q2a: "agency_name = New York City Police Department or Department of Housing Preservation and Development" | ✅ Done — both exact strings verified |
| 1.7 | Test-query 311 API: `SELECT DISTINCT complaint_type` where complaint_type contains 'Noise' or 'Illegal Parking' | Q2a: "complaint_type = noise or illegal parking" | ✅ Done — 9 noise types found; exact "Noise" belongs to DEP not NYPD |
| 1.8 | Build full SoQL query URL, execute, save to `data/311_complaints.csv` | Q2a: "pull and export only the following data" | ✅ Done — 198,158 rows exported |
| 1.9 | Print min/max created_date, total row count, unique agencies, unique complaint types from pulled data | Verification for Q2a | ✅ Done — dates correct, 100% NYPD, 0 HPD, 0 dupes |

**AUDIT GATE 1** (must pass before Phase 2):
- [x] NYC geography identifier found and documented (Gotcha G1) — `AREANAME == 'New York City'`
- [x] Latest available month confirmed and documented (Gotcha G2) — **February 2026**
- [x] NAICS code format understood — range codes identified (Gotcha G6) — BLS codes, 18 sectors mapped
- [x] Exact agency_name spellings verified (Gotcha G10) — both confirmed
- [x] Noise complaint_type values cataloged — exact vs. subcategory split documented (Gotcha G7) — exact "Noise" is DEP only
- [x] 311 data row count confirmed (198,158) and not truncated (Gotcha G11)
- [x] **CRITICAL FINDING: HPD returns zero matching rows** — HPD handles housing quality, not noise/parking. Not a bug.
- [x] **CRITICAL FINDING: Exact "Noise" type belongs to DEP** — NYPD handles subcategories only

### Phase 2: Q1 Analysis — Employment Statistics

| Step | Action | Maps To | Status |
|------|--------|---------|--------|
| 2.1 | Filter ces.csv to NYC geography, 2-digit NAICS level only | Q1a: "major industries (by 2-digit NAICS) in New York City" | ⬜ |
| 2.2 | Identify three time points: latest month, same month -1 year, same month -5 years | Q1a: "over the prior year"; Q1b: "over the last five years" | ⬜ |
| 2.3 | Check for null/blank/suppressed employment values at all three time points | Data quality check | ⬜ |
| 2.4 | For each industry: compute YoY absolute change, YoY % change | Q1a: "changed the most over the prior year" | ⬜ |
| 2.5 | Rank industries by magnitude of change (present both absolute and % — project doesn't specify which) | Q1a: "which major industries... changed the most" | ⬜ |
| 2.6 | Hand-verify one industry's YoY calculation manually (look up two numbers, subtract, divide) | Audit check | ⬜ |
| 2.7 | For each industry: compute 5-year absolute change, 5-year % change | Q1b: "what they experienced over the last five years" | ⬜ |
| 2.8 | Hand-verify one industry's 5-year calculation manually | Audit check | ⬜ |
| 2.9 | Build comparison table: Industry | Latest Month | Prior Year | YoY Abs | YoY % | 5yr Ago | 5yr Abs | 5yr % | Q1b: "include all analysis (calculations, tables, charts, etc.)" | ⬜ |
| 2.10 | Build Chart 1: Diverging horizontal bar — YoY % change by industry, centered at 0 | Q1b: "charts" | ⬜ |
| 2.11 | Build Chart 2: Grouped bar or slope chart — 1-year vs. 5-year % change for top movers | Q1b: "How was the change... different" | ⬜ |
| 2.12 | Build Chart 3 (optional): Small-multiple line charts — 5-year employment trend for key industries | Q1b: "charts" | ⬜ |
| 2.13 | Write narrative for Q1a: for top 3-5 movers, describe **possible reasons** with cited context (COVID recovery, interest rates, tech restructuring, tourism, remote work) | Q1a: "Describe possible reasons why these industries experienced greater change" | ⬜ |
| 2.14 | Write narrative for Q1b: compare 1-year vs. 5-year, note COVID baseline distortion in 5-year lookback | Q1b: "How was the change... different" | ⬜ |
| 2.15 | Cross-reference our NYC total nonfarm employment against any published NYS DOL press release or BLS figure | Audit check | ⬜ |

**AUDIT GATE 2** (must pass before Phase 3):
- [ ] Only same-month comparisons used (no month-to-month with NSA data) (Gotcha G3)
- [ ] Data revision date noted (Gotcha G4)
- [ ] Hand-verified YoY calculation matches code output
- [ ] Hand-verified 5-year calculation matches code output
- [ ] COVID context explicitly addressed in 5-year narrative (Gotcha G5)
- [ ] Total nonfarm employment figure cross-referenced against published source
- [ ] Narrative uses "possible reasons" language — hypotheses, not proven causes
- [ ] All tables and charts rendering correctly in notebook

### Phase 3: Q2 Analysis — 311 Service Requests

| Step | Action | Maps To | Status |
|------|--------|---------|--------|
| 3.1 | Construct the exact SoQL query URL in `https://...` format | Q2a: "include the exact query that you used (in the form of https://...)" | ⬜ |
| 3.2 | Filter: `created_date between '2021-12-15T00:00:00' and '2022-03-15T23:59:59'` (inclusive both ends) | Q2a condition 1: "all dates between 12/15/2021 and 3/15/2022" | ⬜ |
| 3.3 | Filter: `agency_name` = 'New York City Police Department' OR 'Department of Housing Preservation and Development' | Q2a condition 2 | ⬜ |
| 3.4 | Filter: `complaint_type` = 'Illegal Parking' OR starts_with(complaint_type, 'Noise') | Q2a condition 3: "noise or illegal parking" | ⬜ |
| 3.5 | Set `$limit` to value larger than expected result set | Gotcha G11: prevent silent truncation | ⬜ |
| 3.6 | Document the exact URL prominently in a notebook markdown cell | Q2a: "include the exact query... in the form of https://..." | ⬜ |
| 3.7 | Test the URL by pasting in browser — confirm it returns data | Audit check (Gotcha G12) | ⬜ |
| 3.8 | Export pulled data to `data/311_complaints.csv` | Q2a: "pull and export" | ⬜ |
| 3.9 | Cross-tabulate: `pd.crosstab(df['agency_name'], df['complaint_type'], margins=True)` | Q2b: "how many complaints were there for each agency and complaint type" | ⬜ |
| 3.10 | Manually spot-check one cell (e.g., NYPD + Illegal Parking) by counting raw CSV rows | Audit check (Gotcha G8) | ⬜ |
| 3.11 | Build styled table with raw counts, row %, column % | Q2b: "include all analysis (calculations, tables, charts, etc.)" | ⬜ |
| 3.12 | Describe one visualization method in a markdown cell | Q2c: "Describe one way to visualize this data" | ⬜ |
| 3.13 | Build the visualization (proposed: grouped/stacked bar chart — agency × complaint_type) | Q2c: "include the visualization in your response" | ⬜ |
| 3.14 | Write policy message based on observed data patterns | Q2c: "What do you want policymakers to know about your findings?" | ⬜ |
| 3.15 | Pose one research question (socioeconomic lens) | Q2d: "Ask one research question about this data" | ⬜ |
| 3.16 | Identify additional data to merge (ACS 5-year estimates: median income, population by zip) | Q2d: "discuss additional data that you would merge" | ⬜ |
| 3.17 | Write a **simple** equation: `ComplaintsPerCapita_i = β₀ + β₁·MedianIncome_i + β₂·PopulationDensity_i + ε_i` | Q2d: "write a simple equation that shows the relationship" | ⬜ |
| 3.18 | Explain policy relevance of the research question | Q2d: "Why is studying that relationship important for policymaking?" | ⬜ |

**AUDIT GATE 3** (must pass before Phase 4):
- [ ] Exact query URL is a valid `https://...` link and works in browser (Gotcha G12)
- [ ] Date boundaries are inclusive on both ends (Gotcha G9)
- [ ] `$limit` is set and actual count is below the limit (Gotcha G11)
- [ ] Row count matches NYC OpenData portal web UI filter
- [ ] Cross-tab spot-check: manual count matches code output (Gotcha G8)
- [ ] Both a description AND a visualization are present for Q2c (Gotcha G13)
- [ ] Equation is genuinely simple — one equation, not a system (Gotcha G14)
- [ ] Policy message is grounded in observed data, not speculative
- [ ] Noise matching approach documented (all subcategories vs. exact match) (Gotcha G7)

### Phase 4: Presentation & Delivery

| Step | Action | Maps To | Status |
|------|--------|---------|--------|
| 4.1 | Clean up Q1 notebook: polished markdown, clear headings, all outputs visible | Q1b: "include all analysis (calculations, tables, charts, etc.)" | ⬜ |
| 4.2 | Clean up Q2 notebook: polished markdown, clear headings, all outputs visible | Q2b: "include all analysis (calculations, tables, charts, etc.)" | ⬜ |
| 4.3 | Render Q1 notebook to HTML: `jupyter nbconvert --to html` | Delivery format | ⬜ |
| 4.4 | Render Q2 notebook to HTML: `jupyter nbconvert --to html` | Delivery format | ⬜ |
| 4.5 | Build `index.html` landing page linking to both notebooks | Value-add delivery format | ⬜ |
| 4.6 | Build `css/style.css` for landing page | Value-add | ⬜ |
| 4.7 | Initialize git repo, push to GitHub, enable GitHub Pages | Delivery | ⬜ |
| 4.8 | Test live site — all links work, charts render, tables display | Final verification | ⬜ |

**AUDIT GATE 4** (final):
- [ ] All rendered HTML files open correctly in browser
- [ ] All Plotly charts are interactive and display properly
- [ ] The exact query URL is prominently visible in Q2 output
- [ ] No placeholder text or TODO comments remain
- [ ] User follows the USER AUDIT CHECKLIST (Section VIII below)

---

## V. SELF-AUDIT FRAMEWORK

### Q1 Self-Audit Checks

| Check | Method | Pass Criteria | Status |
|-------|--------|---------------|--------|
| Geography | Print all unique `Area` values. Identify NYC string. Print total nonfarm employment. | Total in plausible range (~4-5M). String clearly NYC, not MSA. | ⬜ |
| Date | Print max date in data. Cross-check with NYS DOL website. | Month/year matches latest on website. | ⬜ |
| NAICS codes | Print all unique 2-digit NAICS codes. Check range sectors. | Manufacturing = 31-33, Retail = 44-45, Transportation = 48-49. | ⬜ |
| YoY spot-check | Manually compute YoY change for one industry. Compare to code. | Hand calc matches code output exactly. | ⬜ |
| 5-year spot-check | Same as above for 5-year lookback. | Hand calc matches code output exactly. | ⬜ |
| Cross-reference | Compare NYC total nonfarm against published NYS DOL/BLS figure. | Within 1-2% (minor revision timing differences OK). | ⬜ |
| Seasonal adjustment | Confirm data is NSA. Confirm NO month-to-month comparisons. | Only same-month-across-years comparisons exist. | ⬜ |
| Missing data | Check for null employment values at all three time points. | All analyzed industries have valid data. | ⬜ |

### Q2 Self-Audit Checks

| Check | Method | Pass Criteria | Status |
|-------|--------|---------------|--------|
| Schema exploration | Run exploratory query for distinct agency_name and complaint_type before main query. | Actual values seen and documented before filtering. | ⬜ |
| Agency name match | Compare project's agency names to API output, character-for-character. | Exact match. | ⬜ |
| Noise category audit | Count records with `complaint_type = 'Noise'` exactly vs. `starts_with('Noise')`. Document split. | Both numbers known and documented. | ⬜ |
| Row count vs. portal | Apply same filters in NYC OpenData web UI. Compare total. | Counts match (± small caching difference). | ⬜ |
| Duplicate check | Check for duplicate `unique_key` values. | No duplicates. | ⬜ |
| Date boundary check | Print min/max `created_date` in pulled data. | Min >= 2021-12-15, Max <= 2022-03-15. | ⬜ |
| Cross-tab spot-check | Pick one cell. Count manually in raw CSV. Compare to code. | Manual count matches code. | ⬜ |
| URL validation | Paste query URL in browser. Confirm JSON returns. | URL works. | ⬜ |
| Limit check | Print actual row count vs. `$limit` parameter. | Count < limit (no truncation). | ⬜ |

---

## VI. USER AUDIT CHECKLIST

### Step 1: Verify Data Sources
- [ ] Open https://dol.ny.gov/statistics-ceszip in browser. Download file. Confirm ces.csv inside matches what was used (same row count, same date range).
- [ ] Open https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9 in browser. Apply same filters in web UI (date range, agency, complaint type). Check total row count matches our pull.

### Step 2: Spot-Check Q1 Numbers
- [ ] Open ces.csv in Excel/text editor. Find NYC rows for the latest month. Pick one industry. Manually compute YoY change (subtract, divide). Confirm it matches notebook output.
- [ ] Do the same for 5-year comparison.
- [ ] Google "NYC employment [latest month] [latest year]" — find NYS DOL press release. Compare total nonfarm to our figure.
- [ ] Read Q1a narrative. For each industry claimed to have changed, verify the reason is plausible. Google the industry + "NYC" + year for supporting articles.
- [ ] Confirm no month-to-month comparisons exist anywhere (only same-month across years).

### Step 3: Spot-Check Q2 Numbers
- [ ] Copy the exact query URL from the notebook. Paste in browser. Confirm JSON data returns.
- [ ] In NYC OpenData portal, apply same filters via web UI. Compare total count to our count.
- [ ] Open data/311_complaints.csv in Excel. Create pivot table: agency_name × complaint_type. Confirm counts match notebook cross-tab.
- [ ] Pick one bar in the chart. Find corresponding number in table. Confirm they match.

### Step 4: Check for Grandiosity
- [ ] Q2d research question: is it actually simple? Not over-engineered?
- [ ] Q2c policy message: grounded in data, or making sweeping claims?
- [ ] Q1a narrative: using "possible reasons" / "may reflect" language, not "caused by" / "proves"?
- [ ] Q2d equation: genuinely simple — one equation?
- [ ] Q2c: both a description AND a visualization present?

### Step 5: Final Sanity Check
- [ ] Every requirement in the original prompt is addressed in the notebooks?
- [ ] Exact query URL is visibly included in Q2 output?
- [ ] All charts and tables render in the HTML files?
- [ ] Would this make sense to someone who hasn't seen the project?

---

## VII. ANTI-GRANDIOSITY PRINCIPLES

| # | Principle | Application |
|---|-----------|-------------|
| 1 | **Data first, narrative second** | Every claim traces to a specific number in the data. No unsupported assertions. |
| 2 | **Label uncertainty** | Use "may be related to," "could reflect," "is consistent with" — never "is caused by" or "proves." |
| 3 | **Show the work** | Every intermediate calculation visible in notebook. No black boxes. |
| 4 | **Don't over-model** | Q2d says "simple equation" — one regression equation, not a structural model. |
| 5 | **Don't over-visualize** | Q2c says "one way to visualize" — one primary chart. Additional charts fine for Q1b. |
| 6 | **Acknowledge limitations** | 5-year COVID baseline is a limitation. 311 data = complaints, not conditions. State these explicitly. |
| 7 | **Match data granularity** | 3 months of 311 data → no annual trend claims. Employment levels only → no wage dynamics claims. |
| 8 | **No speculative predictions** | Describe what the data shows. Don't forecast or recommend policy changes beyond what the data supports. |

---

## VIII. ASSUMPTION LOG

Every assumption made during execution gets logged here.

| # | Assumption | Justification | Date Resolved | Verified? |
|---|-----------|---------------|---------------|-----------|
| A1 | ces.csv contains a "New York City" area entry | Must verify on inspection | 2026-04-20 | ✅ YES — `AREANAME == 'New York City'` directly |
| A2 | Latest available month is approximately Feb/March 2026 | Based on typical NYS DOL release schedule | 2026-04-20 | ✅ YES — Feb 2026 confirmed |
| A3 | 5-year lookback baseline (early 2021) is COVID-distorted | COVID was still severely impacting employment in early 2021 | 2026-04-20 | ✅ YES — Feb 2021 baseline is COVID-era |
| A4 | ces.csv is not seasonally adjusted | Stated in NYS DOL documentation | 2026-04-20 | ✅ YES — per README |
| A5 | "Noise" in complaint_type should include all subcategories | 311 system splits noise into sub-types; exact "Noise" may have few records | 2026-04-20 | ✅ YES — exact "Noise" is DEP only; subcategories are NYPD |
| A6 | 311 complaints ≠ actual conditions (self-selection bias) | 311 data reflects who files complaints, not objective conditions | — | Ongoing |
| A7 | Date boundaries are inclusive on both ends | Most natural reading of "between X and Y" | — | To verify in Phase 3 |
| A8 | Agency names in data match project prompt exactly | Project provides full names; must still verify | 2026-04-20 | ✅ YES — both confirmed character-for-character |

---

## IX. OPEN QUESTIONS

| # | Question | When Resolved |
|---|----------|---------------|
| O1 | What is the exact column schema of ces.csv? | Phase 1, Step 1.2 |
| O2 | How is "New York City" labeled in the Area column? | Phase 1, Step 1.3 |
| O3 | What is the actual latest available month? | Phase 1, Step 1.4 |
| O4 | How are NAICS range codes formatted (31-33 vs 31,32,33)? | Phase 1, Step 1.5 |
| O5 | What are the exact complaint_type values that start with "Noise"? | Phase 1, Step 1.7 |
| O6 | Do the agency names in the data match the project prompt exactly? | Phase 1, Step 1.6 |
| O7 | How many total rows will the 311 query return? | Phase 1, Step 1.8 |
| O8 | Are there any suppressed/missing employment values for NYC industries? | Phase 2, Step 2.3 |

---

## X. FILE STRUCTURE

```
OFC_Project/
├── progress.md                     # This file
├── project_description.md           # Original prompt
├── README.md                        # Project overview + live site link
├── .gitignore
├── index.html                       # GitHub Pages landing page
├── css/
│   └── style.css
├── data/
│   ├── ces.csv                      # Raw employment data (from NYS DOL ZIP)
│   └── 311_complaints.csv           # Pulled 311 data (from API)
├── notebooks/
│   ├── Q1_Employment_Analysis.ipynb
│   ├── Q1_Employment_Analysis.html  # Rendered output
│   ├── Q2_311_Analysis.ipynb
│   └── Q2_311_Analysis.html         # Rendered output
└── analysis/
    ├── q1_employment.py             # Standalone script (reproducibility)
    └── q2_311.py                    # Standalone script (reproducibility)
```

---

## XI. REQUIREMENT COVERAGE MATRIX

Every project requirement mapped to the step that addresses it.

| Requirement | Source | Plan Step |
|-------------|--------|-----------|
| Use "the latest available month" | Q1a | 1.4, 2.2 |
| "major industries (by 2-digit NAICS)" | Q1a | 1.5, 2.1 |
| "in New York City" | Q1a | 1.3, 2.1 |
| "changed the most over the prior year" | Q1a | 2.4, 2.5 |
| "Describe possible reasons why" | Q1a | 2.13 |
| "over the last five years" | Q1b | 2.7 |
| "How was the change... different" (1yr vs 5yr) | Q1b | 2.14 |
| "include all analysis (calculations, tables, charts, etc.)" | Q1b | 2.9, 2.10, 2.11, 2.12 |
| "Using the API docs" | Q2a | 1.5 (reference to API docs page) |
| "pull and export only the following data" | Q2a | 1.8, 3.8 |
| "include the exact query... in the form of https://..." | Q2a | 3.1, 3.6 |
| created_date between 12/15/2021 and 3/15/2022 | Q2a #1 | 3.2 |
| agency_name = NYPD or HPD | Q2a #2 | 3.3 |
| complaint_type = noise or illegal parking | Q2a #3 | 3.4 |
| "how many complaints for each agency and complaint type" | Q2b | 3.9, 3.11 |
| "include all analysis (calculations, tables, charts, etc.)" | Q2b | 3.11 |
| "Describe one way to visualize" | Q2c | 3.12 |
| "include the visualization" | Q2c | 3.13 |
| "What do you want policymakers to know" | Q2c | 3.14 |
| "Ask one research question" | Q2d | 3.15 |
| "discuss additional data that you would merge" | Q2d | 3.16 |
| "write a simple equation" | Q2d | 3.17 |
| "Why is studying that relationship important for policymaking?" | Q2d | 3.18 |

---

## XII. STATUS LOG

| Date | Action Taken | Notes |
|------|-------------|-------|
| 2026-04-20 | Project initiated | |
| 2026-04-20 | progress.md created | Full specification compiled |
| 2026-04-20 | **Phase 1 COMPLETE** | All 9 steps done. All audit gate checks passed. |
| 2026-04-20 | CES data downloaded & inspected | ces.csv: 23,810 rows, NYC found, Feb 2026 latest, 18 NAICS sectors mapped |
| 2026-04-20 | 311 API queried & data exported | 198,158 rows, 100% NYPD, 0 HPD. Noise subcategories documented. |
| 2026-04-20 | Key finding: HPD has zero matching rows | HPD handles housing quality, not noise/parking. Not a data error. |
| 2026-04-20 | Key finding: exact "Noise" type is DEP-only | NYPD handles noise subcategories. DEP handles the "Noise" exact type. |
| | | |
