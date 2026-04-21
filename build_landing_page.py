#!/usr/bin/env python3
"""Regenerate docs/index.html from executed notebooks.

Reads the _plotly executed notebooks (which contain fully-rendered Plotly HTML)
and the regular executed notebooks (for pandas Styler tables and markdown narrative),
then rebuilds the GitHub Pages landing page with the latest data.
"""

import json
import re
import uuid
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
NOTEBOOKS = PROJECT / "notebooks"
DOCS = PROJECT / "docs"
OUTPUT = DOCS / "index.html"


def load_notebook(path):
    with open(path) as f:
        return json.load(f)


def extract_html_outputs(nb):
    """Return a list of (cell_index, html_string) for all code cells with text/html output."""
    results = []
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        for out in cell.get("outputs", []):
            data = out.get("data", {})
            if "text/html" in data:
                html = "".join(data["text/html"])
                results.append((i, html))
    return results


def plotly_json_to_html(plotly_json, div_id=None):
    if div_id is None:
        div_id = str(uuid.uuid4())
    fig_data = json.dumps(plotly_json.get("data", []))
    fig_layout = json.dumps(plotly_json.get("layout", {}))
    config = json.dumps(plotly_json.get("config", {"responsive": True}))
    return (
        f'<div id="{div_id}" class="plotly-graph-div" style="height:100%; width:100%;"></div>\n'
        f'<script>Plotly.newPlot("{div_id}", {fig_data}, {fig_layout}, {config});</script>'
    )


def extract_plotly_html(nb):
    """Return list of (cell_index, html_string) for cells with Plotly embeds."""
    results = []
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        for out in cell.get("outputs", []):
            data = out.get("data", {})
            if "text/html" in data:
                html = "".join(data["text/html"])
                if "plotly" in html.lower() and "Plotly.newPlot" in html:
                    results.append((i, html))
            elif "application/vnd.plotly.v1+json" in data:
                plotly_json = data["application/vnd.plotly.v1+json"]
                html = plotly_json_to_html(plotly_json)
                results.append((i, html))
    return results


def extract_table_html(nb):
    """Return list of (cell_index, html_string) for cells with table output (non-Plotly HTML)."""
    results = []
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        for out in cell.get("outputs", []):
            data = out.get("data", {})
            if "text/html" in data:
                html = "".join(data["text/html"])
                if "<table" in html and "Plotly.newPlot" not in html:
                    results.append((i, html))
    return results


def extract_markdown(nb):
    """Return dict of cell_index -> markdown source for all markdown cells."""
    results = {}
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "markdown":
            results[i] = "".join(cell["source"])
    return results


def get_chart_div_id(html):
    """Extract the plotly div id from the embedded HTML."""
    m = re.search(r'id="([a-f0-9-]+)"\s+class="plotly-graph-div"', html)
    if m:
        return m.group(1)
    return str(uuid.uuid4())


def make_plotly_chart_unique(html):
    """Replace the Plotly div id with a new unique one to avoid collisions."""
    old_id = get_chart_div_id(html)
    if not old_id:
        return html
    new_id = str(uuid.uuid4())
    html = html.replace(old_id, new_id)
    return html


# ---------------------------------------------------------------------------
# Load notebooks
# ---------------------------------------------------------------------------
q1_plotly = load_notebook(NOTEBOOKS / "Q1_Employment_Analysis_executed_plotly.ipynb")
q1_exec = load_notebook(NOTEBOOKS / "Q1_Employment_Analysis_executed.ipynb")
q2_plotly = load_notebook(NOTEBOOKS / "Q2_311_Analysis_executed_plotly.ipynb")
q2_exec = load_notebook(NOTEBOOKS / "Q2_311_Analysis_executed.ipynb")

# Q1 outputs
q1_tables = extract_table_html(q1_plotly)
q1_charts = extract_plotly_html(q1_plotly)
q1_md = extract_markdown(q1_exec)

# Q2 outputs
q2_tables = extract_table_html(q2_plotly)
q2_charts = extract_plotly_html(q2_plotly)
q2_md = extract_markdown(q2_exec)

# Sort by cell index to get deterministic order
q1_tables.sort(key=lambda x: x[0])
q1_charts.sort(key=lambda x: x[0])
q2_tables.sort(key=lambda x: x[0])
q2_charts.sort(key=lambda x: x[0])

# Get the specific outputs we need
# Q1: cell 5 = YoY table, cell 7 = 5yr table
yoy_table_html = next(html for ci, html in q1_tables if ci == 5)
fiveyr_table_html = next(html for ci, html in q1_tables if ci == 7)

# Q1: cell 9 = YoY chart, cell 11 = 1yr vs 5yr chart, cell 13 = trends chart
yoy_chart_html = make_plotly_chart_unique(next(html for ci, html in q1_charts if ci == 9))
compare_chart_html = make_plotly_chart_unique(next(html for ci, html in q1_charts if ci == 11))
trends_chart_html = make_plotly_chart_unique(next(html for ci, html in q1_charts if ci == 13))

# Narrative is hardcoded in Q1A_NARRATIVE and Q1B_NARRATIVE below

# Q2: cell 7 = complaint table, cell 13 = borough table, cell 17 = borough-type table
q2_complaint_table_html = next(html for ci, html in q2_tables if ci == 7)
q2_borough_table_html = next(html for ci, html in q2_tables if ci == 13)

# Q2: cell 9 = complaint bar chart, cell 11 = weekly trend chart, cell 15 = borough map
q2_complaint_chart_html = make_plotly_chart_unique(next(html for ci, html in q2_charts if ci == 9))
q2_weekly_chart_html = make_plotly_chart_unique(next(html for ci, html in q2_charts if ci == 11))
q2_borough_map_html = make_plotly_chart_unique(next(html for ci, html in q2_charts if ci == 15))


# ---------------------------------------------------------------------------
# Build Q1a answer section
# ---------------------------------------------------------------------------
Q1A_NARRATIVE = """
                <h3 style="color:red">Decliners</h3>
                <ul style="margin: 8px 0 12px 20px;">
                    <li><strong>Manufacturing (NAICS 31-33): <span style="color:red">&minus;5.82% (&minus;3,100 jobs)</span></strong><br>
                    <em>BLS Supersector: Manufacturing (standalone).</em><br>
                    Manufacturing has been in long-term structural decline in NYC, driven by automation, offshoring of production, and the city's transition to a service-oriented economy.</li>

                    <li><strong>Mining/Construction (NAICS 21+23): <span style="color:red">&minus;4.82% (&minus;6,600 jobs)</span></strong><br>
                    <em>BLS Supersector: Mining, Logging &amp; Construction &mdash; provided as a single combined series for NYC.</em><br>
                    Higher interest rates throughout 2025 may have suppressed new housing starts and commercial development, and the completion of several major infrastructure projects could have reduced construction demand.</li>

                    <li><strong>Other Services (NAICS 81): <span style="color:red">&minus;2.77% (&minus;4,900 jobs)</span></strong><br>
                    <em>BLS Supersector: Other Services (standalone).</em><br>
                    Includes repair services, personal care, and civic organizations. Inflation may be reducing consumer discretionary spending on non-essential services.</li>

                    <li><strong>Leisure &amp; Hospitality (NAICS 71,72): <span style="color:red">&minus;2.28% (&minus;10,000 jobs)</span></strong><br>
                    <em>Composition: Arts, Entertainment &amp; Recreation (71) + Accommodation &amp; Food Services (72).</em><br>
                    The recovery in tourism, dining, and entertainment may have peaked, with consumers reallocating spending toward essentials.</li>

                    <li><strong>Education &amp; Health (NAICS 61,62): <span style="color:red">&minus;1.62% (&minus;21,400 jobs)</span></strong><br>
                    <em>Composition: Private Educational Services (61) + Health Care &amp; Social Assistance (62).</em><br>
                    The largest absolute YoY decline of any supersector. This reversal may reflect normalization after several years of strong growth in healthcare demand.</li>

                    <li><strong>Trade/Trans/Util (NAICS 22,42-49): <span style="color:red">&minus;1.22% (&minus;7,100 jobs)</span></strong><br>
                    <em>Composition: Utilities (22) + Wholesale Trade (42) + Retail Trade (44-45) + Transportation &amp; Warehousing (48-49).</em><br>
                    Broad-based but modest declines across retail, wholesale, and transportation may reflect softening consumer demand and ongoing e-commerce shifts.</li>

                    <li><strong>Prof &amp; Business (NAICS 54-56): <span style="color:red">&minus;0.82% (&minus;6,500 jobs)</span></strong><br>
                    <em>Composition: Professional/Scientific/Technical (54) + Management of Companies (55) + Admin/Waste Management (56).</em><br>
                    A modest decline that may reflect corporate cost-cutting and reduced demand for administrative and temp staffing services.</li>
                </ul>

                <h3 style="color:green">Growers</h3>
                <ul style="margin: 8px 0 12px 20px;">
                    <li><strong>Information (NAICS 51): <span style="color:green">+1.93% (+4,200 jobs)</span></strong><br>
                    <em>BLS Supersector: Information (standalone).</em><br>
                    Growth may be driven by media streaming, digital content, and AI-related services expanding in NYC.</li>

                    <li><strong>Government (NAICS 92): <span style="color:green">+1.58% (+9,500 jobs)</span></strong><br>
                    <em>BLS Supersector: Government (standalone).</em><br>
                    Local government hiring has continued, with the 1-year and 5-year growth rates similar, indicating steady expansion rather than recovery-driven gains.</li>

                    <li><strong>Financial Activities (NAICS 52,53): <span style="color:green">+1.27% (+6,500 jobs)</span></strong><br>
                    <em>Composition: Finance &amp; Insurance (52) + Real Estate &amp; Rental/Leasing (53).</em><br>
                    Steady expansion reflecting NYC's role as a global financial center.</li>
                </ul>

                <div class="takeaway"><strong>1-Year Takeaway:</strong> NYC Total Nonfarm fell by <span style="color:red">39,400 jobs (&minus;0.82%)</span> YoY to 4,791,000. Only 3 of 10 supersectors grew. Seven supersectors contracted, led by Manufacturing (<span style="color:red">&minus;5.82%</span>) and Mining/Construction (<span style="color:red">&minus;4.82%</span>). Information (<span style="color:green">+1.93%</span>) was the strongest grower.</div>
"""

def build_q1a_answer():
    parts = []
    parts.append(
        "<p>The latest available month is <strong>February 2026</strong>. "
        "NYC total nonfarm employment stood at <strong>4,791,000</strong>, "
        "down 39,400 (&minus;0.82%) from February 2025. "
        "Seven of ten BLS supersectors contracted; three grew.</p>"
    )

    parts.append(
        '<div class="chart-label">Year-over-Year Employment Change by Supersector (Feb 2026 vs Feb 2025)</div>'
    )
    parts.append(f'<div class="embedded-chart">{yoy_chart_html}</div>')

    parts.append(
        '<div class="chart-label">Year-over-Year Comparison Table (10 BLS Supersectors + Total Nonfarm)</div>'
    )
    parts.append(f'<div class="embedded-table">{yoy_table_html}</div>')

    parts.append(Q1A_NARRATIVE)

    parts.append(
        "<p>All figures are actual employment units (not thousands). Data is not seasonally adjusted.</p>"
    )
    return "\n                ".join(parts)


# ---------------------------------------------------------------------------
# Build Q1b answer section
# ---------------------------------------------------------------------------
Q1B_NARRATIVE = """
                <h3 style="color:green">Growers</h3>
                <ul style="margin: 8px 0 12px 20px;">
                    <li><strong>Leisure &amp; Hospitality (NAICS 71,72): <span style="color:green">+85.05% (+197,400 jobs)</span></strong><br>
                    <em>Composition: Arts, Entertainment &amp; Recreation (71) + Accommodation &amp; Food Services (72).</em><br>
                    Feb 2021 employment was just 232,100. The large 5-year gain reflects recovery from that low base, though the sector has now begun to contract again YoY.</li>

                    <li><strong>Education &amp; Health (NAICS 61,62): <span style="color:green">+25.07% (+260,100 jobs)</span></strong><br>
                    <em>Composition: Private Educational Services (61) + Health Care &amp; Social Assistance (62).</em><br>
                    The largest absolute 5-year gain of any supersector, driven by both recovery from Feb 2021 lows and structural demand growth in healthcare.</li>

                    <li><strong>Prof &amp; Business (NAICS 54-56): <span style="color:green">+12.75% (+89,200 jobs)</span></strong><br>
                    <em>Composition: Professional/Scientific/Technical (54) + Management of Companies (55) + Admin/Waste Management (56).</em><br>
                    Strong 5-year growth despite a modest YoY decline, suggesting the sector expanded during the recovery and is now consolidating.</li>

                    <li><strong>Financial Activities (NAICS 52,53): <span style="color:green">+12.13% (+55,900 jobs)</span></strong><br>
                    <em>Composition: Finance &amp; Insurance (52) + Real Estate &amp; Rental/Leasing (53).</em><br>
                    Steady 5-year expansion across both finance and real estate, reflecting NYC's continued role as a global financial center.</li>

                    <li><strong>Trade/Trans/Util (NAICS 22,42-49): <span style="color:green">+7.86% (+41,800 jobs)</span></strong><br>
                    <em>Composition: Utilities (22) + Wholesale Trade (42) + Retail Trade (44-45) + Transportation &amp; Warehousing (48-49).</em><br>
                    Growth was broad-based across the supersector, driven by recovery in retail and transportation from Feb 2021 lows.</li>

                    <li><strong>Other Services (NAICS 81): <span style="color:green">+6.37% (+10,300 jobs)</span></strong><br>
                    <em>BLS Supersector: Other Services (standalone).</em><br>
                    Modest growth in repair services, personal care, and civic organizations as consumer spending patterns normalized.</li>

                    <li><strong>Government (NAICS 92): <span style="color:green">+5.47% (+31,700 jobs)</span></strong><br>
                    <em>BLS Supersector: Government (standalone).</em><br>
                    Steady hiring across local government agencies, with similar 1-year and 5-year rates indicating consistent expansion.</li>

                    <li><strong>Information (NAICS 51): <span style="color:green">+5.23% (+11,000 jobs)</span></strong><br>
                    <em>BLS Supersector: Information (standalone).</em><br>
                    Growth in media streaming, digital content, and technology services, though the sector experienced a dip in 2024-2025 before rebounding.</li>
                </ul>

                <h3 style="color:red">Decliners</h3>
                <ul style="margin: 8px 0 12px 20px;">
                    <li><strong>Mining/Construction (NAICS 21+23): <span style="color:red">&minus;3.91% (&minus;5,300 jobs)</span></strong><br>
                    <em>BLS Supersector: Mining, Logging &amp; Construction &mdash; provided as a single combined series for NYC.</em><br>
                    Construction employment in Feb 2021 was still relatively elevated compared to other sectors, leaving less recovery upside. The 5-year decline combined with the YoY decline suggests a sustained downturn in the sector.</li>

                    <li><strong>Manufacturing (NAICS 31-33): <span style="color:red">&minus;3.65% (&minus;1,900 jobs)</span></strong><br>
                    <em>BLS Supersector: Manufacturing (standalone).</em><br>
                    The only sector besides Mining/Construction to decline over both 1-year and 5-year horizons, confirming a decades-long structural decline that has persisted regardless of broader economic conditions.</li>
                </ul>

                <div class="takeaway"><strong>5-Year Takeaway:</strong> NYC Total Nonfarm grew by <span style="color:green">690,200 jobs (+16.83%)</span> over five years to 4,791,000. Eight of ten supersectors grew, led by Leisure &amp; Hospitality (<span style="color:green">+85.05%</span>) and Education &amp; Health (<span style="color:green">+25.07%</span>). Only Manufacturing (<span style="color:red">&minus;3.65%</span>) and Mining/Construction (<span style="color:red">&minus;3.91%</span>) declined over both 1-year and 5-year horizons.</div>
"""

def build_q1b_answer():
    parts = []
    parts.append(
        "<p>The 1-year and 5-year comparisons tell very different stories. "
        "The Feb 2021 baseline was a period when employment was well below pre-pandemic levels across most sectors, "
        "making 5-year comparisons particularly important context for interpretation.</p>"
    )

    parts.append(
        '<div class="chart-label">1-Year vs 5-Year Employment % Change by Supersector</div>'
    )
    parts.append(f'<div class="embedded-chart">{compare_chart_html}</div>')

    parts.append(
        '<div class="chart-label">February Employment Trends for Key NYC Supersectors (2021&ndash;2026)</div>'
    )
    parts.append(f'<div class="embedded-chart">{trends_chart_html}</div>')

    parts.append(
        '<div class="chart-label">Full Comparison Table: Feb 2026 vs Feb 2025 vs Feb 2021</div>'
    )
    parts.append(f'<div class="embedded-table">{fiveyr_table_html}</div>')

    parts.append(Q1B_NARRATIVE)

    return "\n                ".join(parts)


# ---------------------------------------------------------------------------
# Build the full HTML page
# ---------------------------------------------------------------------------
def build_page():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bureau of Tax and Economic Analysis — Quantitative Research</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f7; color: #1d1d1f; line-height: 1.6;
        }}
        header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: white; padding: 60px 20px; text-align: center;
        }}
        header h1 {{ font-size: 2.2rem; font-weight: 600; letter-spacing: -0.02em; margin-bottom: 8px; }}
        header p {{ font-size: 1.1rem; opacity: 0.85; max-width: 600px; margin: 0 auto; }}
        .container {{ max-width: 960px; margin: 0 auto; padding: 40px 20px; }}
        .section-label {{
            font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.08em; color: #86868b; margin-bottom: 12px;
        }}
        .cards {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px; margin-bottom: 48px;
        }}
        .card {{
            background: white; border-radius: 12px; padding: 28px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            transition: transform 0.15s, box-shadow 0.15s;
            text-decoration: none; color: inherit; display: block;
        }}
        .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); }}
        .card .icon {{ font-size: 1.8rem; margin-bottom: 12px; }}
        .card h2 {{ font-size: 1.15rem; font-weight: 600; margin-bottom: 6px; }}
        .card p {{ font-size: 0.9rem; color: #6e6e73; line-height: 1.5; }}
        .card .tag {{
            display: inline-block; font-size: 0.72rem; font-weight: 500;
            padding: 3px 8px; border-radius: 4px; margin-top: 12px;
        }}
        .tag-blue {{ background: #e8f0fe; color: #1a73e8; }}
        .tag-green {{ background: #e6f4ea; color: #137333; }}
        .tag-orange {{ background: #fef7e0; color: #b06000; }}

        .qa-block {{
            background: white; border-radius: 12px; padding: 32px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 20px;
        }}
        .qa-block h2 {{ font-size: 1rem; font-weight: 600; color: #0f3460; margin-bottom: 6px; }}
        .qa-block .question {{
            font-size: 0.92rem; color: #555; margin-bottom: 16px;
            padding-bottom: 12px; border-bottom: 1px solid #eee; font-style: italic;
        }}
        .qa-block .answer {{ font-size: 0.92rem; color: #1d1d1f; line-height: 1.7; }}
        .qa-block .answer p {{ margin-bottom: 10px; }}
        .qa-block .answer ul {{ margin: 8px 0 12px 20px; }}
        .qa-block .answer li {{ margin-bottom: 4px; }}
        .qa-block .answer strong {{ color: #0f3460; }}
        .qa-block .answer .query-url {{
            background: #f5f5f7; border: 1px solid #e0e0e0; border-radius: 6px;
            padding: 12px 16px; font-family: 'SF Mono', 'Consolas', monospace;
            font-size: 0.78rem; color: #333; word-break: break-all; margin: 12px 0; line-height: 1.5;
        }}

        .embedded-chart {{
            margin: 16px 0; border: 1px solid #eee; border-radius: 8px;
            padding: 4px; width: 100%; max-width: 100%; overflow: hidden;
        }}
        .embedded-chart > div {{ max-width: 100% !important; overflow: hidden; }}
        .embedded-chart .plotly-graph-div {{ width: 100% !important; max-width: 100% !important; }}
        .embedded-chart svg.main-svg {{ max-width: 100% !important; }}

        .embedded-table {{
            margin: 16px 0; width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch;
        }}
        .embedded-table table {{
            font-size: 0.8rem; border-collapse: collapse; width: 100%; min-width: 600px;
        }}
        .embedded-table th, .embedded-table td {{
            padding: 5px 8px; text-align: left; border-bottom: 1px solid #eee; white-space: normal; word-break: break-word; max-width: 180px;
        }}
        .embedded-table th {{
            background: #f5f5f7; font-weight: 600; color: #333; font-size: 0.75rem;
        }}
        .embedded-table td:nth-child(n+3), .embedded-table th:nth-child(n+3) {{
            text-align: right; font-variant-numeric: tabular-nums;
        }}
        .embedded-table tr:hover {{ background: #fafafa; }}

        .chart-label {{
            font-size: 0.75rem; color: #86868b; font-weight: 500;
            text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px;
        }}

        .takeaway {{
            background: #f0f4f8;
            border-left: 4px solid #0f3460;
            border-radius: 6px;
            padding: 12px 16px;
            margin: 16px 0;
            font-size: 0.92rem;
            line-height: 1.6;
        }}

        footer {{
            text-align: center; padding: 32px 20px; color: #86868b; font-size: 0.8rem;
        }}
        footer a {{ color: #6e6e73; text-decoration: none; }}
    </style>
</head>
<body>
    <header>
        <h1>Bureau of Tax and Economic Analysis</h1>
        <p>Quantitative Research Project &mdash; NYC Employment Trends &amp; 311 Service Requests</p>
    </header>

    <div class="container">
        <div class="section-label">Analysis Notebooks</div>
        <div class="cards">
            <a class="card" href="phase1.html">
                <div class="icon">&#128202;</div>
                <h2>Phase 1: Data Acquisition</h2>
                <p>Download, inspect, and validate both datasets.</p>
                <span class="tag tag-green">CES + 311 API</span>
            </a>
            <a class="card" href="q1.html">
                <div class="icon">&#128200;</div>
                <h2>Q1: Employment Analysis</h2>
                <p>Year-over-year and 5-year industry changes across 10 BLS supersectors plus Total Nonfarm.</p>
                <span class="tag tag-blue">10 Supersectors + TNF &middot; 3 Charts</span>
            </a>
            <a class="card" href="q2.html">
                <div class="icon">&#128222;</div>
                <h2>Q2: 311 Service Requests</h2>
                <p>198,158 NYPD noise and illegal parking complaints (Dec 2021 &ndash; Mar 2022).</p>
                <span class="tag tag-orange">198K Records &middot; 2 Charts</span>
            </a>
        </div>

        <div class="section-label">Responses</div>

        <!-- Q1a -->
        <div class="qa-block">
            <h2>Question 1a</h2>
            <div class="question">Using the NYS DOL's employment statistics data for the latest available month, discuss which major industries (by 2-digit NAICS) in New York City changed the most over the prior year. Describe possible reasons why these industries experienced greater change than other industries.</div>
            <div class="answer">
                {build_q1a_answer()}
            </div>
        </div>

        <!-- Q1b -->
        <div class="qa-block">
            <h2>Question 1b</h2>
            <div class="question">How was the change that these industries experienced over the last year different from what they experienced over the last five years? Please include all analysis (calculations, tables, charts, etc.) in your response.</div>
            <div class="answer">
                {build_q1b_answer()}
            </div>
        </div>

        <!-- Q2a -->
        <div class="qa-block">
            <h2>Question 2a</h2>
            <div class="question">Using the API docs, pull and export only the following data. Please include the exact query that you used (in the form of https://...) in your response.</div>
            <div class="answer">
                <p>Filters applied:</p>
                <ul>
                    <li><code>created_date</code> between 12/15/2021 and 3/15/2022 (inclusive)</li>
                    <li><code>agency_name</code> = NYPD or HPD</li>
                    <li><code>complaint_type</code> starts with "Noise" (all subcategories) or equals "Illegal Parking"</li>
                </ul>
                <p><strong>Exact query URL:</strong></p>
                <div class="query-url">https://data.cityofnewyork.us/resource/erm2-nwe9.json?$select=unique_key,created_date,agency_name,complaint_type,descriptor,borough,incident_zip,latitude,longitude&amp;$where=created_date between '2021-12-15T00:00:00' and '2022-03-15T23:59:59' AND (agency_name='New York City Police Department' OR agency_name='Department of Housing Preservation and Development') AND (starts_with(complaint_type, 'Noise') OR complaint_type='Illegal Parking')&amp;$limit=500000</div>
                <p>This returned <strong>198,158 rows</strong>, all from NYPD. HPD returned zero matching rows because HPD handles housing quality (heat/hot water, plumbing) &mdash; not noise or parking.</p>
                <p><strong>Note on noise matching:</strong> An exact match for <code>complaint_type = 'Noise'</code> captures only ~10,800 DEP records &mdash; missing 92% of noise complaints. Using <code>starts_with(complaint_type, 'Noise')</code> captures all subcategories. The exact "Noise" type belongs to DEP (not NYPD/HPD), so it is correctly excluded by the agency filter.</p>
            </div>
        </div>

        <!-- Q2b -->
        <div class="qa-block">
            <h2>Question 2b</h2>
            <div class="question">Based on the data you pulled, how many complaints were there for each agency and complaint type? Please include all analysis (calculations, tables, charts, etc.) in your response.</div>
            <div class="answer">
                <p><strong>By agency:</strong> All 198,158 complaints came from NYPD. HPD returned <strong>zero</strong> matching rows (HPD handles housing quality, not noise/parking).</p>

                <div class="chart-label">Complaint Counts by Type</div>
                <div class="embedded-table">{q2_complaint_table_html}</div>
                <p>Noise (all subcategories): 111,665 (56.4%)</p>
<p>Illegal Parking: 86,493 (43.6%)</p>
<p>All 198,158 complaints are from NYPD. HPD = 0 matching rows (see Phase 1).</p>

                <div class="chart-label">Complaints by Type</div>
                <div class="embedded-chart">{q2_complaint_chart_html}</div>

                <p><strong>Noise (all subcategories)</strong> accounts for 111,665 complaints (56.4%) and <strong>Illegal Parking</strong> accounts for 86,493 (43.6%). Nearly 200,000 quality-of-life complaints in three months.</p>
            </div>
        </div>

        <!-- Q2c -->
        <div class="qa-block">
            <h2>Question 2c</h2>
            <div class="question">Describe one way to visualize this data and include the visualization in your response. What do you want policymakers to know about your findings?</div>
            <div class="answer">
                <p><strong>Visualization:</strong> A horizontal bar chart (above) showing complaint volume by type, color-coded by category (red = noise, blue = illegal parking). A weekly time series (below) shows seasonal patterns.</p>

                <div class="chart-label">Weekly Complaint Trends</div>
                <div class="embedded-chart">{q2_weekly_chart_html}</div>

                <div class="chart-label">Complaints by Borough</div>
                <div class="embedded-chart">{q2_borough_map_html}</div>
                <div class="embedded-table">{q2_borough_table_html}</div>

                <p><strong>What policymakers should know:</strong></p>
                <ul>
                    <li><strong>Residential noise dominates.</strong> 75,543 complaints (38%) &mdash; the single largest quality-of-life concern. Dense multi-unit living is a persistent friction point.</li>
                    <li><strong>Illegal parking rivals all noise combined.</strong> 86,493 complaints (44%) &mdash; a significant enforcement burden. Could parking enforcement be handled by a civilian agency?</li>
                    <li><strong>Nearly 200,000 complaints in 3 months</strong> is an extraordinary volume. Quality-of-life enforcement consumes substantial NYPD resources.</li>
                </ul>
            </div>
        </div>

        <!-- Q2d -->
        <div class="qa-block">
            <h2>Question 2d</h2>
            <div class="question">Ask one research question about this data; discuss additional data that you would merge with this dataset to answer your question and write a simple equation that shows the relationship. Why is studying that relationship important for policymaking?</div>
            <div class="answer">
                <p><strong>Research question:</strong> Do neighborhoods with lower median household incomes generate more noise and illegal parking complaints per capita, after controlling for population density?</p>
                <p><strong>Additional data:</strong> ACS 5-Year Estimates (Census Bureau) &mdash; median household income, population, and land area by zip code. Merge on <code>incident_zip</code> from the 311 data.</p>
                <p><strong>Equation (OLS):</strong></p>
                <p style="font-family: 'SF Mono', 'Consolas', monospace; font-size: 0.88rem; background: #f5f5f7; padding: 10px 16px; border-radius: 6px; display: inline-block;">
                    ComplaintsPerCapita<sub>i</sub> = &beta;<sub>0</sub> + &beta;<sub>1</sub> &middot; MedianIncome<sub>i</sub> + &beta;<sub>2</sub> &middot; PopulationDensity<sub>i</sub> + &epsilon;<sub>i</sub>
                </p>
                <p>If &beta;<sub>1</sub> is negative and significant, lower-income neighborhoods file more complaints per person, after accounting for density.</p>
                <p><strong>Why this matters:</strong></p>
                <ul>
                    <li><strong>Equity:</strong> If lower-income areas have more per-capita complaints, services should be proportionally directed to where need is greatest.</li>
                    <li><strong>Complaint vs. need:</strong> 311 reflects who files complaints, not who experiences problems. Higher-income residents may file more, biasing allocation. Understanding this helps distinguish need from reporting behavior.</li>
                </ul>
            </div>
        </div>
    </div>

    <footer>
        <p>Data: <a href="https://dol.ny.gov/current-employment-statistics-0">NYS DOL CES</a> &middot; <a href="https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9">NYC 311 OpenData</a></p>
        <p style="margin-top: 8px;">Bureau of Tax and Economic Analysis &mdash; Quantitative Research Project</p>
    </footer>

    <script>
    function resizePlotlyCharts() {{
        document.querySelectorAll('.embedded-chart').forEach(function(el) {{
            var w = el.clientWidth;
            if (w < 1) return;
            el.querySelectorAll('.plotly-graph-div').forEach(function(div) {{
                div.style.width = w + 'px';
                if (window.Plotly) {{ try {{ Plotly.Plots.resize(div); }} catch(e) {{}} }}
            }});
        }});
    }}
    if (document.readyState === 'complete') {{
        setTimeout(resizePlotlyCharts, 300);
        setTimeout(resizePlotlyCharts, 1500);
    }} else {{
        window.addEventListener('load', function() {{
            setTimeout(resizePlotlyCharts, 300);
            setTimeout(resizePlotlyCharts, 1500);
        }});
    }}
    window.addEventListener('resize', resizePlotlyCharts);
    </script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
html = build_page()
OUTPUT.write_text(html)
print(f"Wrote {OUTPUT} ({len(html)} bytes)")

# Quick validation: count key structural elements
table_count = html.count("<table ")
chart_count = html.count("Plotly.newPlot")
print(f"  Tables: {table_count}")
print(f"  Plotly charts: {chart_count}")
print(f"  '10 Supersectors' in Q1 card: {'10 Supersectors' in html}")
