import pandas as pd
import json
import sys

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name} — {detail}")

ces = pd.read_csv('data/ces.csv')
ces.columns = ces.columns.str.strip()
df311 = pd.read_csv('data/311_complaints.csv')
df311['created_date'] = pd.to_datetime(df311['created_date'])
nyc = ces[ces['AREANAME'] == 'New York City']

sectors = {
    '21+23': 'Mining, Logging and Construction',
    '31-33': 'Manufacturing',
    '42': 'Wholesale Trade',
    '44-45': 'Retail Trade',
    '48-49': 'Transportation and Warehousing',
    '22': 'Utilities',
    '51': 'Information',
    '52': 'Finance and Insurance',
    '53': 'Real Estate and Rental and Leasing',
    '54': 'Professional, Scientific, and Technical Services',
    '55': 'Management of Companies and Enterprises',
    '56': 'Administrative and Support and Waste Management and Remediation Services',
    '61': 'Private Educational Services',
    '62': 'Health Care and Social Assistance',
    '71': 'Arts, Entertainment, and Recreation',
    '72': 'Accommodation and Food Services',
    '81': 'Other Services',
    '92': 'Government',
}

def get_val(industry_title, year, month='FEB'):
    row = nyc[(nyc['YEAR'] == year) & (nyc['INDUSTRY_TITLE'] == industry_title)]
    if len(row) == 0:
        return None
    v = row.iloc[0][month]
    if pd.isna(v) or str(v).strip() == '':
        return None
    return int(v)

print("=" * 70)
print("AUDIT: Q1 EMPLOYMENT ANALYSIS")
print("=" * 70)

check("NYC is a direct AREANAME entry", len(nyc) > 0)
check("Latest year is 2026", 2026 in nyc['YEAR'].values)

raw_cols = pd.read_csv('data/ces.csv', nrows=0).columns.tolist()
check("CES columns have trailing spaces (documented gotcha)",
      any(c != c.strip() for c in raw_cols))

total_nf_26 = get_val('Total Nonfarm', 2026)
total_nf_25 = get_val('Total Nonfarm', 2025)
total_nf_21 = get_val('Total Nonfarm', 2021)

if total_nf_26 and total_nf_25:
    yoy = total_nf_26 - total_nf_25
    yoy_pct = yoy / total_nf_25 * 100
    print(f"\n  INFO  Total Nonfarm Feb 2026: {total_nf_26:,}")
    print(f"  INFO  Total Nonfarm Feb 2025: {total_nf_25:,}")
    print(f"  INFO  YoY: {yoy:+,} ({yoy_pct:+.2f}%)")
    check("Total Nonfarm Feb 2026 = 4,791,000", total_nf_26 == 4791000, f"got {total_nf_26:,}")
    check("YoY decline ≈ -0.82%", abs(yoy_pct - (-0.82)) < 0.05, f"got {yoy_pct:.4f}%")

if total_nf_26 and total_nf_21:
    five_yr = total_nf_26 - total_nf_21
    five_pct = five_yr / total_nf_21 * 100
    print(f"  INFO  Total Nonfarm Feb 2021: {total_nf_21:,}")
    print(f"  INFO  5yr: {five_yr:+,} ({five_pct:+.2f}%)")

print(f"\n  INFO  === ALL 18 SECTORS ===")
all_data = {}
for naics, title in sectors.items():
    v26 = get_val(title, 2026)
    v25 = get_val(title, 2025)
    v21 = get_val(title, 2021)
    all_data[naics] = {'title': title, 'v26': v26, 'v25': v25, 'v21': v21}
    if v26 and v25:
        chg = v26 - v25
        pct = chg / v25 * 100
        chg5 = v26 - v21 if v21 else None
        pct5 = chg5 / v21 * 100 if v21 else None
        print(f"  NAICS {naics:>6}: {v26:>10,}  YoY {chg:>+8,} ({pct:>+.2f}%)  5yr {chg5:>+8,} ({pct5:>+.1f}%)" if pct5 else f"  NAICS {naics:>6}: {v26:>10,}  YoY {chg:>+8,} ({pct:>+.2f}%)")
    else:
        print(f"  NAICS {naics:>6}: MISSING DATA")

check("All 18 sectors have Feb 2026 data",
      all(d['v26'] is not None for d in all_data.values()),
      f"missing: {[k for k,v in all_data.items() if v['v26'] is None]}")
check("All 18 sectors have Feb 2025 data",
      all(d['v25'] is not None for d in all_data.values()),
      f"missing: {[k for k,v in all_data.items() if v['v25'] is None]}")

hc = all_data.get('62', {})
if hc.get('v26') and hc.get('v25'):
    chg = hc['v26'] - hc['v25']
    pct = chg / hc['v25'] * 100
    check("Health Care YoY = -24,200", chg == -24200, f"got {chg:+,}")
    check("Health Care YoY% ≈ -2.32%", abs(pct - (-2.32)) < 0.05, f"got {pct:.4f}%")

arts = all_data.get('71', {})
if arts.get('v26') and arts.get('v25'):
    chg = arts['v26'] - arts['v25']
    pct = chg / arts['v25'] * 100
    check("Arts YoY = -4,700", chg == -4700, f"got {chg:+,}")
    check("Arts YoY% ≈ -5.34%", abs(pct - (-5.34)) < 0.1, f"got {pct:.4f}%")

trans = all_data.get('48-49', {})
if trans.get('v26') and trans.get('v25'):
    chg = trans['v26'] - trans['v25']
    pct = chg / trans['v25'] * 100
    check("Transportation YoY = -1,600", chg == -1600, f"got {chg:+,}")
    check("Transportation YoY% ≈ -1.19%", abs(pct - (-1.19)) < 0.1, f"got {pct:.4f}%")

mfg = all_data.get('31-33', {})
if mfg.get('v26') and mfg.get('v25'):
    chg = mfg['v26'] - mfg['v25']
    pct = chg / mfg['v25'] * 100
    check("Manufacturing YoY = -3,100", chg == -3100, f"got {chg:+,}")
    check("Manufacturing YoY% ≈ -5.81%", abs(pct - (-5.81)) < 0.1, f"got {pct:.4f}%")

gov = all_data.get('92', {})
if gov.get('v26') and gov.get('v25'):
    chg = gov['v26'] - gov['v25']
    pct = chg / gov['v25'] * 100
    check("Government YoY ≈ +9,500", abs(chg - 9500) <= 100, f"got {chg:+,}")
    check("Government YoY% ≈ +1.58%", abs(pct - 1.58) < 0.1, f"got {pct:.4f}%")

check("Total Nonfarm in actual units (~4.8M)",
      total_nf_26 is not None and 3000000 < total_nf_26 < 6000000,
      f"got {total_nf_26:,}" if total_nf_26 else "no data")

print("\n" + "=" * 70)
print("AUDIT: Q2 311 SERVICE REQUESTS")
print("=" * 70)

print(f"\n  INFO  Total rows: {len(df311):,}")
check("Total rows = 198,158", len(df311) == 198158, f"got {len(df311):,}")

min_d = df311['created_date'].min()
max_d = df311['created_date'].max()
print(f"  INFO  Date range: {min_d} to {max_d}")
check("Min >= Dec 15 2021", min_d >= pd.Timestamp('2021-12-15'))
check("Max <= Mar 15 2022", max_d <= pd.Timestamp('2022-03-15 23:59:59'))

agencies = df311['agency_name'].value_counts()
print(f"\n  INFO  Agencies:")
for a, c in agencies.items():
    print(f"         {a}: {c:,}")
check("100% NYPD", len(agencies) == 1 and agencies.index[0] == 'New York City Police Department')
check("HPD = 0", 'Housing' not in ' '.join(agencies.index))

complaints = df311['complaint_type'].value_counts()
print(f"\n  INFO  Complaint types:")
for ct, cnt in complaints.items():
    print(f"         {ct}: {cnt:,}")

check("Illegal Parking = 86,493", complaints.get('Illegal Parking', 0) == 86493)
check("Noise - Residential = 75,543", complaints.get('Noise - Residential', 0) == 75543)
check("Noise - Street/Sidewalk = 12,743", complaints.get('Noise - Street/Sidewalk', 0) == 12743)
check("Noise - Vehicle = 11,372", complaints.get('Noise - Vehicle', 0) == 11372)
check("Noise - Commercial = 11,114", complaints.get('Noise - Commercial', 0) == 11114)

noise_total = df311['complaint_type'].str.startswith('Noise').sum()
parking_total = (df311['complaint_type'] == 'Illegal Parking').sum()
print(f"\n  INFO  Noise total: {noise_total:,} ({noise_total/len(df311)*100:.1f}%)")
print(f"  INFO  Parking total: {parking_total:,} ({parking_total/len(df311)*100:.1f}%)")
check("Noise + Parking = grand total", noise_total + parking_total == len(df311),
      f"{noise_total:,} + {parking_total:,} = {noise_total+parking_total:,} vs {len(df311):,}")

check("No exact 'Noise' type (DEP)", (df311['complaint_type'] == 'Noise').sum() == 0)
check("No duplicates", df311.duplicated(subset=['unique_key']).sum() == 0)

boroughs = df311['borough'].value_counts()
print(f"\n  INFO  Boroughs:")
for b, c in boroughs.items():
    print(f"         {b}: {c:,}")
check("5 boroughs", len(boroughs) >= 5)

with open('notebooks/Q2_311_Analysis.ipynb') as f:
    nb = json.load(f)
url_ok = any("Department of Housing Preservation and Development')" in ''.join(c.get('source', []))
             or "Development\\') " in ''.join(c.get('source', []))
             for c in nb['cells'])
check("Q2 QUERY_URL correct parenthesization", url_ok)

print("\n" + "=" * 70)
print(f"AUDIT COMPLETE: {PASS} PASS, {FAIL} FAIL")
print("=" * 70)
sys.exit(1 if FAIL > 0 else 0)
