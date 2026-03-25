"""
PDF Report Generator
Reads processed CSV data and generates a professional .pdf report.
"""

import csv
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor, white, black, grey
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image,
)

from report_config import COLORS, FONTS_PDF, SIZES, REPORT_TITLE, REPORT_SUBTITLE, SECTIONS

# ──────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DATA_DIR = Path(__file__).resolve().parent / "report_data"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ──────────────────────────────────────────────
# COLORS
# ──────────────────────────────────────────────

PRIMARY = HexColor(COLORS["primary"])
SECONDARY = HexColor(COLORS["secondary"])
ACCENT = HexColor(COLORS["accent"])
SUCCESS = HexColor(COLORS["success"])
DARK_TEXT = HexColor(COLORS["dark_text"])
LIGHT_BG = HexColor(COLORS["light_bg"])
BORDER = HexColor(COLORS["border"])

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def load_csv_data(filename):
    path = REPORT_DATA_DIR / filename
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fmt_dollar(value):
    return f"${float(value):,.2f}"

def fmt_dollar_short(value):
    v = float(value)
    if v >= 1_000_000:
        return f"${v / 1_000_000:,.1f}M"
    elif v >= 1_000:
        return f"${v / 1_000:,.0f}K"
    return f"${v:,.2f}"

def fmt_number(value):
    return f"{int(float(value)):,}"

def fmt_pct(value):
    v = float(value)
    return f"{'+' if v >= 0 else ''}{v}%"


# ──────────────────────────────────────────────
# STYLES
# ──────────────────────────────────────────────

base_styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "CustomTitle",
    parent=base_styles["Heading1"],
    fontSize=SIZES["title"],
    textColor=PRIMARY,
    spaceAfter=10,
    alignment=TA_CENTER,
    fontName=FONTS_PDF["heading"],
)

subtitle_style = ParagraphStyle(
    "CustomSubtitle",
    parent=base_styles["Heading2"],
    fontSize=SIZES["subtitle"] - 3,
    textColor=grey,
    spaceAfter=20,
    alignment=TA_CENTER,
    fontName=FONTS_PDF["body"],
)

section_style = ParagraphStyle(
    "SectionHeading",
    parent=base_styles["Heading2"],
    fontSize=SIZES["section"],
    textColor=PRIMARY,
    spaceBefore=6,
    spaceAfter=10,
    fontName=FONTS_PDF["heading"],
)

body_style = ParagraphStyle(
    "CustomBody",
    parent=base_styles["Normal"],
    fontSize=SIZES["body"],
    textColor=DARK_TEXT,
    alignment=TA_JUSTIFY,
    spaceAfter=10,
    fontName=FONTS_PDF["body"],
)

label_green = ParagraphStyle(
    "LabelGreen",
    parent=base_styles["Normal"],
    fontSize=SIZES["body"],
    textColor=SUCCESS,
    spaceBefore=14,
    spaceAfter=6,
    fontName=FONTS_PDF["heading"],
)

label_red = ParagraphStyle(
    "LabelRed",
    parent=base_styles["Normal"],
    fontSize=SIZES["body"],
    textColor=ACCENT,
    spaceBefore=14,
    spaceAfter=6,
    fontName=FONTS_PDF["heading"],
)


# ──────────────────────────────────────────────
# TABLE BUILDER
# ──────────────────────────────────────────────

def build_table(headers, rows, col_widths, highlight_col=None):
    """Create a styled ReportLab Table."""
    data = [headers] + rows
    table = Table(data, colWidths=col_widths)

    style_cmds = [
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), FONTS_PDF["heading"]),
        ("FONTSIZE", (0, 0), (-1, 0), SIZES["table_head"]),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),

        # Data rows
        ("FONTNAME", (0, 1), (-1, -1), FONTS_PDF["body"]),
        ("FONTSIZE", (0, 1), (-1, -1), SIZES["table_body"]),
        ("TEXTCOLOR", (0, 1), (-1, -1), DARK_TEXT),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),

        # Borders
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("LINEBELOW", (0, 0), (-1, 0), 2, PRIMARY),
    ]

    # Alternate row shading
    for i in range(1, len(data)):
        if i % 2 == 1:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), LIGHT_BG))

    # Highlight column
    if highlight_col is not None:
        for i in range(1, len(data)):
            cell_val = str(rows[i - 1][highlight_col])
            try:
                v = float(cell_val.replace("%", "").replace("+", "").replace(",", ""))
                color = SUCCESS if v < 0 else ACCENT
                style_cmds.append(("TEXTCOLOR", (highlight_col, i), (highlight_col, i), color))
                style_cmds.append(("FONTNAME", (highlight_col, i), (highlight_col, i), FONTS_PDF["heading"]))
            except ValueError:
                pass

    table.setStyle(TableStyle(style_cmds))
    return table


# ──────────────────────────────────────────────
# KPI ROW
# ──────────────────────────────────────────────

def build_kpi_row(kpis):
    """Create a row of KPI cards as a table."""
    n = len(kpis)
    col_w = 6.5 * inch / n

    values = [Paragraph(f'<b>{k["value"]}</b>', ParagraphStyle(
        f"kpi_val_{i}", fontSize=16, textColor=PRIMARY, alignment=TA_CENTER,
        fontName=FONTS_PDF["heading"],
    )) for i, k in enumerate(kpis)]

    labels = [Paragraph(k["label"], ParagraphStyle(
        f"kpi_lbl_{i}", fontSize=8, textColor=grey, alignment=TA_CENTER,
        fontName=FONTS_PDF["body"],
    )) for i, k in enumerate(kpis)]

    table = Table([values, labels], colWidths=[col_w] * n)

    style_cmds = [
        ("LINEABOVE", (0, 0), (-1, 0), 2, PRIMARY),
        ("LINEBELOW", (0, -1), (-1, -1), 2, PRIMARY),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
    ]
    for i in range(n):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (i, 0), (i, -1), LIGHT_BG))

    table.setStyle(TableStyle(style_cmds))
    return table


# ──────────────────────────────────────────────
# CHART GENERATION
# ──────────────────────────────────────────────

def create_vendor_pie_chart(vendors):
    """Generate a pie chart of top 5 vendors + Others."""
    labels = [v["name"][:18] for v in vendors[:5]]
    values = [float(v["pct_of_total"]) for v in vendors[:5]]
    others = round(100 - sum(values), 1)
    labels.append("Others")
    values.append(others)

    colors_list = [
        COLORS["primary"], COLORS["secondary"], COLORS["accent"],
        COLORS["success"], "#F39C12", COLORS["border"],
    ]

    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct="%1.1f%%",
        colors=colors_list, startangle=90,
        pctdistance=0.75, textprops={"fontsize": 8},
    )
    for t in autotexts:
        t.set_fontsize(7)
        t.set_fontweight("bold")

    ax.legend(labels, loc="lower center", ncol=3, fontsize=7,
              bbox_to_anchor=(0.5, -0.15), frameon=False)
    ax.set_title("% of Total Spend", fontsize=10, fontweight="bold", pad=10)

    plt.tight_layout()
    chart_path = OUTPUT_DIR / "vendor_pie_chart.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight", transparent=True)
    plt.close()
    return chart_path


def create_rotation_bar_chart(fastest, slowest):
    """Generate a horizontal bar chart comparing fastest/slowest movers."""
    fast_names = [r["description"][:20] for r in fastest[:5]]
    fast_vals = [int(float(r["delta"])) for r in fastest[:5]]
    slow_names = [r["description"][:20] for r in slowest[:5]]
    slow_vals = [int(float(r["delta"])) for r in slowest[:5]]

    names = fast_names[::-1] + slow_names[::-1]
    vals = fast_vals[::-1] + slow_vals[::-1]
    bar_colors = [COLORS["success"]] * 5 + [COLORS["accent"]] * 5

    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.barh(names, vals, color=bar_colors, height=0.6)
    ax.set_xlabel("Stock Delta (units)", fontsize=9)
    ax.set_title("Top 5 Fastest vs Slowest Moving Products", fontsize=10, fontweight="bold")
    ax.axvline(x=0, color="grey", linewidth=0.5)

    for i, v in enumerate(vals):
        offset = 200 if v >= 0 else -200
        ha = "left" if v >= 0 else "right"
        ax.text(v + offset, i, f"{v:,}", ha=ha, va="center", fontsize=7, fontweight="bold")

    ax.tick_params(axis="y", labelsize=7)
    ax.tick_params(axis="x", labelsize=7)
    plt.tight_layout()

    chart_path = OUTPUT_DIR / "rotation_bar_chart.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight", transparent=True)
    plt.close()
    return chart_path


# ──────────────────────────────────────────────
# HEADER / FOOTER (canvas callback)
# ──────────────────────────────────────────────

def add_header_footer(canvas, doc):
    """Runs automatically on every page."""
    canvas.saveState()

    # Header bar
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, doc.height + doc.topMargin, doc.width + 2 * doc.leftMargin, 50, fill=True, stroke=False)

    canvas.setFillColor(white)
    canvas.setFont(FONTS_PDF["heading"], 14)
    canvas.drawString(doc.leftMargin, doc.height + doc.topMargin + 20, REPORT_TITLE)

    canvas.setFont(FONTS_PDF["body"], 8)
    canvas.drawRightString(
        doc.width + doc.leftMargin,
        doc.height + doc.topMargin + 20,
        f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
    )

    # Footer
    canvas.setFillColor(grey)
    canvas.setFont(FONTS_PDF["body"], SIZES["footer"])
    canvas.drawString(doc.leftMargin, 20, "Confidential — Internal Use Only")
    canvas.drawRightString(doc.width + doc.leftMargin, 20, f"Page {doc.page}")

    canvas.restoreState()


# ──────────────────────────────────────────────
# REPORT ASSEMBLY
# ──────────────────────────────────────────────

def generate_report():
    print("Loading processed data...")
    es = load_csv_data("executive_summary.csv")[0]
    stores = load_csv_data("store_overview.csv")
    top_margin = load_csv_data("top_margin.csv")
    bottom_margin = load_csv_data("bottom_margin.csv")
    fastest = load_csv_data("fastest_moving.csv")
    slowest = load_csv_data("slowest_moving.csv")
    vendors = load_csv_data("vendor_top10.csv")

    pdf_path = OUTPUT_DIR / "WarehouseReport.pdf"

    pdf = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=1.0 * inch,
        bottomMargin=0.75 * inch,
    )

    elements = []

    # ═══════════════════════════════════════════
    # PAGE 1: TITLE + EXECUTIVE SUMMARY
    # ═══════════════════════════════════════════

    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(REPORT_TITLE, title_style))
    elements.append(Paragraph(REPORT_SUBTITLE, subtitle_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Section heading
    elements.append(Paragraph(SECTIONS[0], section_style))

    # KPI row
    elements.append(build_kpi_row([
        {"label": "Stores", "value": es["total_stores"]},
        {"label": "Active SKUs (EOY)", "value": fmt_number(es["unique_skus_end"])},
        {"label": "Avg Margin", "value": f"{es['avg_margin_pct']}%"},
        {"label": "Vendors", "value": es["total_vendors"]},
    ]))

    elements.append(Spacer(1, 0.2 * inch))

    summary_text = (
        f"During fiscal year 2016, total inventory units grew from "
        f"<b>{fmt_number(es['beg_total_units'])}</b> to <b>{fmt_number(es['end_total_units'])}</b> "
        f"({fmt_pct(es['unit_change_pct'])}), representing an inventory value increase from "
        f"<b>{fmt_dollar(es['beg_total_value'])}</b> to <b>{fmt_dollar(es['end_total_value'])}</b> "
        f"({fmt_pct(es['value_change_pct'])}). The product catalog expanded from "
        f"{fmt_number(es['unique_skus_beg'])} to {fmt_number(es['unique_skus_end'])} SKUs. "
        f"Total procurement spend reached <b>{fmt_dollar(es['total_purchase_spend'])}</b> with "
        f"{fmt_dollar(es['total_freight'])} in freight costs across {es['total_vendors']} "
        f"active suppliers. The average product margin stands at <b>{es['avg_margin_pct']}%</b>, "
        f"and {es['dead_stock_count']} products showed zero movement throughout the year."
    )
    elements.append(Paragraph(summary_text, body_style))

    # ═══════════════════════════════════════════
    # PAGE 2: INVENTORY OVERVIEW
    # ═══════════════════════════════════════════

    elements.append(PageBreak())
    elements.append(Paragraph(SECTIONS[1], section_style))
    elements.append(Paragraph("Top 10 stores by end-of-year inventory value:", body_style))
    elements.append(Spacer(1, 0.1 * inch))

    store_headers = ["Store", "City", "Beg Units", "End Units", "Delta", "Beg Value", "End Value"]
    store_widths = [0.5 * inch, 1.0 * inch, 0.9 * inch, 0.9 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch]
    store_rows = []
    for s in stores:
        delta = int(float(s["delta_units"]))
        store_rows.append([
            s["store"], s["city"],
            fmt_number(s["beg_units"]), fmt_number(s["end_units"]),
            f"{'+' if delta >= 0 else ''}{delta:,}",
            fmt_dollar(s["beg_value"]), fmt_dollar(s["end_value"]),
        ])

    elements.append(build_table(store_headers, store_rows, store_widths, highlight_col=4))
    elements.append(Spacer(1, 0.2 * inch))

    top_store = stores[0]
    elements.append(Paragraph(
        f"The store with the highest inventory value at year-end is Store {top_store['store']} "
        f"in {top_store['city']}, holding {fmt_number(top_store['end_units'])} units valued at "
        f"<b>{fmt_dollar(top_store['end_value'])}</b>. Across all stores, inventory grew by "
        f"{fmt_pct(es['unit_change_pct'])} in units and {fmt_pct(es['value_change_pct'])} in value.",
        body_style,
    ))

    # ═══════════════════════════════════════════
    # PAGE 3: MARGIN ANALYSIS
    # ═══════════════════════════════════════════

    elements.append(PageBreak())
    elements.append(Paragraph(SECTIONS[2], section_style))
    elements.append(Paragraph(
        f"The average margin across all products is <b>{es['avg_margin_pct']}%</b>. "
        f"Below are the top and bottom 10 products by margin percentage.",
        body_style,
    ))

    margin_headers = ["Product", "Price", "Cost", "Margin $", "Margin %", "Brand"]
    margin_widths = [2.0 * inch, 0.7 * inch, 0.7 * inch, 0.7 * inch, 0.7 * inch, 0.6 * inch]

    def margin_to_rows(items):
        return [[
            m["description"][:35], fmt_dollar(m["price"]), fmt_dollar(m["cost"]),
            fmt_dollar(m["margin_abs"]), f"{m['margin_pct']}%", m["brand"],
        ] for m in items]

    elements.append(Paragraph("Top 10 — Highest Margin Products", label_green))
    elements.append(build_table(margin_headers, margin_to_rows(top_margin), margin_widths, highlight_col=4))

    elements.append(Paragraph("Bottom 10 — Lowest Margin Products", label_red))
    elements.append(build_table(margin_headers, margin_to_rows(bottom_margin), margin_widths, highlight_col=4))

    # ═══════════════════════════════════════════
    # PAGE 4: STOCK ROTATION
    # ═══════════════════════════════════════════

    elements.append(PageBreak())
    elements.append(Paragraph(SECTIONS[3], section_style))
    elements.append(Paragraph(
        f"Products with the largest decrease in stock are considered fast-moving. "
        f"Those with the largest increase indicate slow rotation or over-purchasing. "
        f"<b>{es['dead_stock_count']} products</b> showed zero movement during the year.",
        body_style,
    ))

    rot_headers = ["Product", "Beg Stock", "End Stock", "Delta", "Brand"]
    rot_widths = [2.2 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch, 0.7 * inch]

    def rotation_to_rows(items):
        rows = []
        for r in items:
            delta = int(float(r["delta"]))
            rows.append([
                r["description"][:35],
                fmt_number(r["beg_stock"]), fmt_number(r["end_stock"]),
                f"{'+' if delta >= 0 else ''}{delta:,}", r["brand"],
            ])
        return rows

    elements.append(Paragraph("Top 10 — Fastest Moving (biggest stock decrease)", label_green))
    elements.append(build_table(rot_headers, rotation_to_rows(fastest), rot_widths, highlight_col=3))

    elements.append(Paragraph("Top 10 — Slowest Moving (biggest stock increase)", label_red))
    elements.append(build_table(rot_headers, rotation_to_rows(slowest), rot_widths, highlight_col=3))

    # ═══════════════════════════════════════════
    # PAGE 5: ROTATION CHART
    # ═══════════════════════════════════════════

    elements.append(PageBreak())
    elements.append(Paragraph("Stock Rotation — Visual Comparison", section_style))
    elements.append(Spacer(1, 0.1 * inch))

    print("Generating rotation chart...")
    rotation_chart_path = create_rotation_bar_chart(fastest, slowest)
    elements.append(Image(str(rotation_chart_path), width=6 * inch, height=3.5 * inch))

    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(
        "<b>Chart Analysis:</b> The contrast between fast and slow movers highlights "
        "products that may need promotional support or purchasing adjustments. "
        "Smirnoff 80 Proof leads sales with a stock decrease of over 13,000 units, "
        "while Smirnoff Traveler accumulated over 13,000 units.",
        body_style,
    ))

    # ═══════════════════════════════════════════
    # PAGE 6: SUPPLIER ANALYSIS
    # ═══════════════════════════════════════════

    elements.append(PageBreak())
    elements.append(Paragraph(SECTIONS[4], section_style))
    elements.append(Paragraph(
        f"The company works with <b>{es['total_vendors']} active suppliers</b>. "
        f"Total procurement spend in 2016 was <b>{fmt_dollar(es['total_purchase_spend'])}</b> "
        f"plus {fmt_dollar(es['total_freight'])} in freight.",
        body_style,
    ))

    vendor_headers = ["Supplier", "Spend", "Freight", "Orders", "Pay Days", "% Total"]
    vendor_widths = [1.8 * inch, 1.1 * inch, 0.8 * inch, 0.6 * inch, 0.7 * inch, 0.6 * inch]
    vendor_rows = [[
        v["name"][:25], fmt_dollar_short(v["spend"]), fmt_dollar_short(v["freight"]),
        v["orders"], f"{v['avg_pay_days']}d", f"{v['pct_of_total']}%",
    ] for v in vendors]

    elements.append(build_table(vendor_headers, vendor_rows, vendor_widths, highlight_col=5))

    elements.append(Spacer(1, 0.2 * inch))

    print("Generating vendor pie chart...")
    pie_chart_path = create_vendor_pie_chart(vendors)
    elements.append(Image(str(pie_chart_path), width=4 * inch, height=3 * inch))

    elements.append(Spacer(1, 0.1 * inch))

    top_v = vendors[0]
    elements.append(Paragraph(
        f"The largest supplier is <b>{top_v['name'].strip()}</b>, accounting for "
        f"{top_v['pct_of_total']}% of total procurement spend ({fmt_dollar(top_v['spend'])}). "
        f"Average payment terms across top suppliers range from "
        f"{min(int(v['avg_pay_days']) for v in vendors)} to "
        f"{max(int(v['avg_pay_days']) for v in vendors)} days.",
        body_style,
    ))

    # ═══════════════════════════════════════════
    # BUILD
    # ═══════════════════════════════════════════

    print("Building PDF...")
    pdf.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    print(f"\n✓ Report saved to {pdf_path}")


if __name__ == "__main__":
    generate_report()