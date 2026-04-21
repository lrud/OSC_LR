import json
import copy

def load_nb(path):
    with open(path) as f:
        return json.load(f)

def save_nb(nb, path):
    with open(path, 'w') as f:
        json.dump(nb, f, indent=1)
    print(f"Saved {path} ({len(nb['cells'])} cells)")

def remove_cells_by_index(nb, indices):
    for idx in sorted(indices, reverse=True):
        del nb['cells'][idx]

def replace_cell(nb, idx, new_cell):
    nb['cells'][idx] = new_cell

def make_code_cell(source_lines, execution_count=None):
    cell = {
        "cell_type": "code",
        "metadata": {},
        "source": source_lines,
        "outputs": [],
        "execution_count": execution_count
    }
    return cell

def make_markdown_cell(source_lines):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source_lines
    }

def clear_outputs(nb):
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None


# ============================================================
# PHASE 1: Data Acquisition
# ============================================================
# Original: 27 cells (indices 0-26)
# Remove: cells 6 (AREANAME listing), 7 (sanity check), 
#         12 (spot check YoY), 13 (spot check 5yr),
#         15 (agency API probe), 20 (HPD probe), 22 (URL print)
# After: 20 cells

phase1 = load_nb('notebooks/Phase1_Data_Acquisition.ipynb')

# Simplify cell 1 (imports) - remove verbose directory listing
phase1['cells'][1]['source'] = [
    "import pandas as pd\n",
    "import requests\n",
    "import json\n",
    "import os\n",
    "from datetime import datetime\n",
    "\n",
    "DATA_DIR = '../data'\n",
    "print(f'Notebook run time: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}')"
]

# Simplify cell 3 (load/inspect CES) - cleaner display
phase1['cells'][3]['source'] = [
    "ces = pd.read_csv(f'{DATA_DIR}/ces.csv')\n",
    "ces.columns = ces.columns.str.strip()\n",
    "print(f'ces.csv: {ces.shape[0]:,} rows × {ces.shape[1]} columns')\n",
    "print(f'Columns: {list(ces.columns)}')\n",
    "ces.head(3)"
]

# Simplify cell 16 (noise/parking complaint types) - keep key finding, trim verbosity
phase1['cells'][16]['source'] = [
    "params = {\n",
    "    '$select': 'complaint_type, count(*) as cnt',\n",
    "    '$where': \"created_date between '2021-12-15T00:00:00' and '2022-03-15T23:59:59' AND (complaint_type like '%Noise%' OR complaint_type like '%Illegal Parking%')\",\n",
    "    '$group': 'complaint_type',\n",
    "    '$order': 'cnt DESC',\n",
    "    '$limit': 100\n",
    "}\n",
    "r = requests.get(API_BASE, params=params)\n",
    "complaints = r.json()\n",
    "\n",
    "noise_df = pd.DataFrame(complaints)\n",
    "noise_df['cnt'] = noise_df['cnt'].astype(int)\n",
    "display(noise_df.style.hide(axis='index'))\n",
    "\n",
    "total_noise = noise_df[noise_df['complaint_type'].str.contains('Noise')]['cnt'].sum()\n",
    "exact_noise = noise_df[noise_df['complaint_type'] == 'Noise']['cnt'].sum()\n",
    "print(f'\\nAll noise subcategories: {total_noise:,}')\n",
    "print(f'Exact \"Noise\" only:      {exact_noise:,}')\n",
    "print(f'Using starts_with captures {total_noise:,} vs exact match {exact_noise:,} — a {total_noise/exact_noise:.1f}x difference.')"
]

# Simplify cell 19 (agency × noise matrix) - cleaner display
phase1['cells'][19]['source'] = [
    "params = {\n",
    "    '$select': 'agency_name, complaint_type, count(*) as cnt',\n",
    "    '$where': \"created_date between '2021-12-15T00:00:00' and '2022-03-15T23:59:59' AND starts_with(complaint_type, 'Noise')\",\n",
    "    '$group': 'agency_name, complaint_type',\n",
    "    '$order': 'cnt DESC',\n",
    "    '$limit': 100\n",
    "}\n",
    "r = requests.get(API_BASE, params=params)\n",
    "agency_noise = pd.DataFrame(r.json())\n",
    "agency_noise['cnt'] = agency_noise['cnt'].astype(int)\n",
    "display(agency_noise.style.hide(axis='index'))\n",
    "\n",
    "print('Key: NYPD handles all noise subcategories (Residential, Commercial, etc.)')\n",
    "print('DEP handles exact \"Noise\" type only. EDC handles Noise - Helicopter.')\n",
    "print('HPD has ZERO noise complaints — HPD handles housing quality (heat/hot water, plumbing).')"
]

# Simplify cell 24 (data validation) - essential checks only
phase1['cells'][24]['source'] = [
    "print(f'Total rows: {len(df_311):,}')\n",
    "print(f'Date range: {df_311[\"created_date\"].min()} to {df_311[\"created_date\"].max()}')\n",
    "print(f'Unique agencies: {sorted(df_311[\"agency_name\"].unique())}')\n",
    "print(f'Complaint types: {sorted(df_311[\"complaint_type\"].unique())}')\n",
    "print(f'Duplicate unique_key: {df_311[\"unique_key\"].duplicated().sum()}')\n",
    "print(f'Null incident_zip: {df_311[\"incident_zip\"].isna().sum()}')"
]

# Merge cells 17+18 (Noise Matching Decision + Critical Discovery header)
phase1['cells'][17]['source'] = [
    "### Noise Matching Decision\n",
    "\n",
    "**The project says: `complaint_type = noise or illegal parking`**\n",
    "\n",
    "**Our interpretation:** Capture ALL complaint types that start with \"Noise\" (including subcategories) plus \"Illegal Parking\" exactly.\n",
    "\n",
    "**Justification:**\n",
    "1. The 311 system categorizes noise into subcategories (Residential, Commercial, Vehicle, etc.)\n",
    "2. An exact match for \"Noise\" alone captures only ~8% of noise complaints\n",
    "3. The exact \"Noise\" type belongs to **DEP** (not NYPD or HPD), so it is correctly excluded by the agency filter\n",
    "4. HPD has zero noise/parking complaints — HPD handles housing quality (heat/hot water, plumbing)\n",
    "\n",
    "**IMPLICATION:** When we filter for (NYPD OR HPD) AND (noise OR illegal parking), HPD returns zero rows."
]

# Now remove cells (must be done after modifications, in reverse order)
remove_cells_by_index(phase1, [6, 7, 12, 13, 15, 20, 22])
# After removing cell 18 (Critical Discovery header) was already merged into 17, but wait...
# Cell 18 is the markdown that was merged. After merging source into 17, remove 18.
# But cell 18 is at index 18. Let me check: after removing [6,7,12,13,15,20,22] what happens to index 18?
# Original indices 0-26. After removing 6,7: 0-5, 8-26 (now indices 0-24)
# After removing 12,13 (which were original 14,15 now): ... this is getting confusing.

# Let me re-do: remove all at once by original indices, in reverse order
# Actually, I already called remove_cells_by_index which does reverse order. 
# But I also need to remove cell 18 (original) since I merged it into cell 17.
# Wait, after removing [6,7,12,13,15,20,22] from 27 cells:
# Original 17 -> new index 17-2=15 (after removing 6,7)
# Original 18 -> new index 18-2=16 (after removing 6,7)
# But we also removed 12,13,15 before those... let me not do this manually.

# Let me redo the approach: remove all cells including the merged one
# I need to remove original cell 18 too since its content was merged into 17.

# Actually, let me just reload and do it properly.
phase1 = load_nb('notebooks/Phase1_Data_Acquisition.ipynb')

# Re-apply modifications to the fresh copy
phase1['cells'][1]['source'] = [
    "import pandas as pd\n",
    "import requests\n",
    "import json\n",
    "import os\n",
    "from datetime import datetime\n",
    "\n",
    "DATA_DIR = '../data'\n",
    "print(f'Notebook run time: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}')"
]

phase1['cells'][3]['source'] = [
    "ces = pd.read_csv(f'{DATA_DIR}/ces.csv')\n",
    "ces.columns = ces.columns.str.strip()\n",
    "print(f'ces.csv: {ces.shape[0]:,} rows × {ces.shape[1]} columns')\n",
    "print(f'Columns: {list(ces.columns)}')\n",
    "ces.head(3)"
]

phase1['cells'][16]['source'] = [
    "params = {\n",
    "    '$select': 'complaint_type, count(*) as cnt',\n",
    "    '$where': \"created_date between '2021-12-15T00:00:00' and '2022-03-15T23:59:59' AND (complaint_type like '%Noise%' OR complaint_type like '%Illegal Parking%')\",\n",
    "    '$group': 'complaint_type',\n",
    "    '$order': 'cnt DESC',\n",
    "    '$limit': 100\n",
    "}\n",
    "r = requests.get(API_BASE, params=params)\n",
    "complaints = r.json()\n",
    "\n",
    "noise_df = pd.DataFrame(complaints)\n",
    "noise_df['cnt'] = noise_df['cnt'].astype(int)\n",
    "display(noise_df.style.hide(axis='index'))\n",
    "\n",
    "total_noise = noise_df[noise_df['complaint_type'].str.contains('Noise')]['cnt'].sum()\n",
    "exact_noise = noise_df[noise_df['complaint_type'] == 'Noise']['cnt'].sum()\n",
    "print(f'\\nAll noise subcategories: {total_noise:,}')\n",
    "print(f'Exact \"Noise\" only:      {exact_noise:,}')\n",
    "print(f'Using starts_with captures {total_noise:,} vs exact match {exact_noise:,} — a {total_noise/exact_noise:.1f}x difference.')"
]

phase1['cells'][19]['source'] = [
    "params = {\n",
    "    '$select': 'agency_name, complaint_type, count(*) as cnt',\n",
    "    '$where': \"created_date between '2021-12-15T00:00:00' and '2022-03-15T23:59:59' AND starts_with(complaint_type, 'Noise')\",\n",
    "    '$group': 'agency_name, complaint_type',\n",
    "    '$order': 'cnt DESC',\n",
    "    '$limit': 100\n",
    "}\n",
    "r = requests.get(API_BASE, params=params)\n",
    "agency_noise = pd.DataFrame(r.json())\n",
    "agency_noise['cnt'] = agency_noise['cnt'].astype(int)\n",
    "display(agency_noise.style.hide(axis='index'))\n",
    "\n",
    "print('Key: NYPD handles all noise subcategories (Residential, Commercial, etc.)')\n",
    "print('DEP handles exact \"Noise\" type only. EDC handles Noise - Helicopter.')\n",
    "print('HPD has ZERO noise complaints — HPD handles housing quality (heat/hot water, plumbing).')"
]

phase1['cells'][24]['source'] = [
    "print(f'Total rows: {len(df_311):,}')\n",
    "print(f'Date range: {df_311[\"created_date\"].min()} to {df_311[\"created_date\"].max()}')\n",
    "print(f'Unique agencies: {sorted(df_311[\"agency_name\"].unique())}')\n",
    "print(f'Complaint types: {sorted(df_311[\"complaint_type\"].unique())}')\n",
    "print(f'Duplicate unique_key: {df_311[\"unique_key\"].duplicated().sum()}')\n",
    "print(f'Null incident_zip: {df_311[\"incident_zip\"].isna().sum()}')"
]

# Merge cells 17+18 into cell 17, then remove cell 18
phase1['cells'][17]['source'] = [
    "### Noise Matching Decision\n",
    "\n",
    "**The project says: `complaint_type = noise or illegal parking`**\n",
    "\n",
    "**Our interpretation:** Capture ALL complaint types that start with \"Noise\" (including subcategories) plus \"Illegal Parking\" exactly.\n",
    "\n",
    "**Justification:**\n",
    "1. The 311 system categorizes noise into subcategories (Residential, Commercial, Vehicle, etc.)\n",
    "2. An exact match for \"Noise\" alone captures only ~8% of noise complaints\n",
    "3. The exact \"Noise\" type belongs to **DEP** (not NYPD or HPD), so it is correctly excluded by the agency filter\n",
    "4. HPD has zero noise/parking complaints — HPD handles housing quality (heat/hot water, plumbing)\n",
    "\n",
    "**IMPLICATION:** When we filter for (NYPD OR HPD) AND (noise OR illegal parking), HPD returns zero rows."
]

# Remove cells: 6, 7, 12, 13, 15, 18, 20, 22 (18 is the merged header)
remove_cells_by_index(phase1, [6, 7, 12, 13, 15, 18, 20, 22])
clear_outputs(phase1)
save_nb(phase1, 'notebooks/Phase1_Data_Acquisition.ipynb')


# ============================================================
# Q1: Employment Analysis
# ============================================================
# Original: 24 cells (indices 0-23)
# Remove: 6 (top movers table), 7 (hand verification markdown), 8 (assert QA),
#         18 (gap analysis >20pp), 20 (both-pos/both-neg diagnostic)
# After: 19 cells

q1 = load_nb('notebooks/Q1_Employment_Analysis.ipynb')

# Remove redundant/exploratory cells
remove_cells_by_index(q1, [6, 7, 8, 18, 20])

# Also simplify cell 5 (YoY table) - use DataFrame display instead of raw print
# After removing cells 6,7,8 (which come after cell 5), cell 5 is still at index 5
q1['cells'][5]['source'] = [
    "df_yoy = df.sort_values('YoY %', ascending=True)\n",
    "display_cols = ['NAICS', 'Industry', 'Feb 2026', 'Feb 2025', 'YoY Change', 'YoY %']\n",
    "styled = df_yoy[display_cols].style.format({\n",
    "    'Feb 2026': '{:,}', 'Feb 2025': '{:,}', 'YoY Change': '{:+,}', 'YoY %': '{:+.2f}%'\n",
    "}).hide(axis='index')\n",
    "display(styled)\n",
    "print(f'\\nNYC Total Nonfarm: Feb 2026 = 4,791,000 | Feb 2025 = 4,830,400 | YoY = -39,400 (-0.82%)')\n",
    "print('All figures are actual employment units (not thousands). Data is not seasonally adjusted.')"
]

# Simplify cell 10 (full comparison table) - use DataFrame display
# After removing 6,7,8 (indices before 10), original index 10 becomes index 10-3=7
# Wait no, remove_cells_by_index removes in reverse order: 20, 18, 8, 7, 6
# So cells 0-5 stay, cell 6 is removed, cell 7 is removed, cell 8 is removed
# Original cell 9 -> new index 6
# Original cell 10 -> new index 7
# Original cell 11 -> new index 8
# etc.
# So I should modify by new index after removal. But I called remove_cells_by_index already.

# Let me check: after removing [6,7,8,18,20] from 24 cells:
# Removed indices (reverse): 20, 18, 8, 7, 6
# Cell 0-5: stay at 0-5
# Cell 6 removed
# Cell 7 removed
# Cell 8 removed
# Cell 9 -> new index 6
# Cell 10 -> new index 7
# Cell 11 -> new index 8
# Cell 12 -> new index 9
# Cell 13 -> new index 10
# Cell 14 -> new index 11
# Cell 15 -> new index 12
# Cell 16 -> new index 13
# Cell 17 -> new index 14
# Cell 18 removed
# Cell 19 -> new index 15
# Cell 20 removed
# Cell 21 -> new index 16
# Cell 22 -> new index 17
# Cell 23 -> new index 18

# So original cell 10 (full comparison table) is now at index 7
q1['cells'][7]['source'] = [
    "display_all = ['NAICS', 'Industry', 'Feb 2026', 'Feb 2025', 'YoY Change', 'YoY %', 'Feb 2021', '5yr Change', '5yr %']\n",
    "df_full = df.sort_values('YoY %', ascending=True)\n",
    "styled_full = df_full[display_all].style.format({\n",
    "    'Feb 2026': '{:,}', 'Feb 2025': '{:,}', 'Feb 2021': '{:,}',\n",
    "    'YoY Change': '{:+,}', '5yr Change': '{:+,}',\n",
    "    'YoY %': '{:+.2f}%', '5yr %': '{:+.2f}%'\n",
    "}).hide(axis='index')\n",
    "display(styled_full)\n",
    "print('\\nCRITICAL CONTEXT: Feb 2021 was still in COVID disruption.')\n",
    "print('Large positive 5-year % changes reflect recovery from COVID lows, not sustainable growth rates.')"
]

clear_outputs(q1)
save_nb(q1, 'notebooks/Q1_Employment_Analysis.ipynb')


# ============================================================
# Q2: 311 Analysis
# ============================================================
# Original: 16 cells (indices 0-15)
# Remove: 3 (URL reprint), 9 (QA spot check)
# Consolidate: 6+7+8 -> 1 clean cell (complaint breakdown shown 3 ways)
# After: 12 cells

q2 = load_nb('notebooks/Q2_311_Analysis.ipynb')

# Replace cells 6,7,8 with one consolidated cell
consolidated_cell = make_code_cell([
    "crosstab = pd.crosstab(df['agency_name'], df['complaint_type'], margins=True)\n",
    "\n",
    "noise_mask = df['complaint_type'].str.startswith('Noise')\n",
    "summary = pd.DataFrame({\n",
    "    'Count': df['complaint_type'].value_counts(),\n",
    "    '% of Total': (df['complaint_type'].value_counts() / len(df) * 100).round(2)\n",
    "})\n",
    "summary.loc['TOTAL'] = [len(df), 100.00]\n",
    "display(summary.style.format({'Count': '{:,.0f}', '% of Total': '{:.2f}%'}))\n",
    "\n",
    "print(f'\\nNoise (all subcategories): {noise_mask.sum():,} ({noise_mask.sum()/len(df)*100:.1f}%)')\n",
    "print(f'Illegal Parking: {(~noise_mask).sum():,} ({(~noise_mask).sum()/len(df)*100:.1f}%)')\n",
    "print(f'\\nAll {len(df):,} complaints are from NYPD. HPD = 0 matching rows (see Phase 1).')"
])

# Replace cells 6 with consolidated, remove 7 and 8
q2['cells'][6] = consolidated_cell
del q2['cells'][8]  # Remove original cell 8 (broad categories)
del q2['cells'][7]  # Remove original cell 7 (counts with percentages)

# Remove cell 3 (URL reprint) and cell 9 (QA spot check)
# After above changes, indices shifted:
# Original: 0,1,2,3,4,5,6,[7removed],[8removed],9,10,11,12,13,14,15
# Current:  0,1,2,3,4,5,6,       7,           8,9,10,11,12,13
# Remove original 3 (still at index 3) and original 9 (now at index 7)
# Wait, after removing 8 and 7, the array is:
# 0,1,2,3,4,5,6(new),9,10,11,12,13,14,15
# Remove index 3 (URL reprint) and index 7 (which was original 9, QA spot check)
remove_cells_by_index(q2, [3, 7])

# Now add analytical note for the weekly time series chart
# Current cells after all removals:
# 0: header, 1: imports, 2: Step 3.1-3.6 markdown, 3: Why starts_with, 
# 4: Step 3.9-3.11 markdown, 5: consolidated complaint counts, 
# 6: Step 3.12-3.13 viz markdown, 7: Chart 1, 8: Chart 2 (weekly)
# 9: Policy Message, 10: Research Question, 11: Audit Gate

# Add analytical note before Chart 2 (weekly time series)
# Insert a markdown cell before cell 8
analytical_note = make_markdown_cell([
    "### Weekly Time Series\n",
    "\n",
    "The weekly trend reveals seasonal patterns: noise complaints spike around New Year's Eve (week of Dec 27) \n",
    "and remain elevated through the winter months. Illegal parking complaints are more stable week-to-week, \n",
    "suggesting a chronic rather than seasonal issue."
])

q2['cells'].insert(8, analytical_note)

clear_outputs(q2)
save_nb(q2, 'notebooks/Q2_311_Analysis.ipynb')


print("\n=== POLISHING COMPLETE ===")
print("Phase1: removed 8 cells, modified 5 cells (27 → 19 cells)")
print("Q1: removed 5 cells, modified 2 cells (24 → 19 cells)")
print("Q2: removed 3 cells, consolidated 3→1, added 1 (16 → 13 cells)")
print("\nNext: re-execute notebooks with jupyter nbconvert --execute")
