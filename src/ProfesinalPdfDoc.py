from time import strftime
from reportlab.lib import colors
from reportlab.lib import styles
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
                                Spacer, PageBreak, Image, tables)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT 
from reportlab.lib.colors import HexColor
import matplotlib.pyplot as plt
from datetime import datetime

from pathlib import Path

from MidLevPdfDoc import sec_color


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR/"outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

pdf_path = OUTPUT_DIR/"ProfesionalPdfDoc.pdf"

#brand color
prim_color = HexColor("#2E5090")
dec_color = HexColor("#7FB3D5")
accent_color = HexColor("#E74C3C")
success_color = HexColor("#27AE60")

#Obtain base styles from ReportLab
styles = getSampleStyleSheet()

#create custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=prim_color,
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

subtitle_style = ParagraphStyle(
    'CustomSubtitle',
    parent=styles['Heading2'],
    fontSize=16,
    textColor=prim_color,
    spaceAfter=12,
    fontName='Helvetica-Bold'
)

normal_style = ParagraphStyle(
    'CustomNormal',
    parent=styles['Normal'],
    fontSize=11,
    textColor=colors.HexColor('#2C3E50'),
    alignment=TA_JUSTIFY,
    spaceAfter=12
)

#graph generation function
def create_sales_graph():
    """
    Gnerate a bar graph and save it as image
    """

    products = ['Product A', 'Product B', 'Product C']
    sales = [50000, 45000, 30000]
    bar_color = ['#2E5090', '#7FB3D5', '#E74C3C']

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(products, sales, color=bar_color)
    ax.set_ylabel('sales ($)', fontsize=12, fontweight='bold')
    ax.set_title('sales by product', fontsize=14, fontweight='bold')

    #add values on the bars
    for i, v in enumerate(sales):
        ax.text(i, v + 1000, f'${v:,}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    DIR_imgGraph = OUTPUT_DIR / "sales_graph.png"
    plt.savefig(DIR_imgGraph, dpi=150, bbox_inches='tight')
    plt.close()

    return DIR_imgGraph

def add_heading(canvas, doc):
    """
    This function runs automatically on evey page
    """

    canvas.saveState()

    #Heading
    canvas.setFillColor(prim_color)
    canvas.rect(
        0, 
        doc.height + doc.topMargin + 20,
        doc.width + 2*doc.leftMargin, 
        60,
        fill=True,
        stroke = False
    )

    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 16)
    canvas.drawString(
        doc.leftMargin,
        doc.height + doc.topMargin + 50,
        "SALES REPORT"
    )

    canvas.setFont('Helvetica', 10)
    canvas.drawString(
        doc.leftMargin,
        doc.height + doc.height + doc.topMargin + 30,
        f"Generated: {datetime.now().strftime('%d/%m%Y %H:%M')}"
    )

    #page footer
    canvas.setFillColor(sec_color)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(doc.leftMargin, 20, "2026 company_name|confidential")
    canvas.drawString(
        doc.width + doc.leftMargin -50,
        20,
        f"Page {doc.page}"
    )

#generate professional table
def create_sales_table():

    data = [
        ['Product', 'Units', 'Price.unit', 'Total', 'Variation'],
        ['Product A', '250', '$200', '$50.000', '↑ 10%'],
        ['Product B', '300', '$150', '$45.000', '↑ 5%'],
        ['Product C', '200', '$150', '$30.000', '↑ 20%'],
        ['', '', 'Total:', '$125.000', '↑ 15%']
    ]

    #createtable object
    table = Table(data, colWidths=[2*inch, 1*inch, 1.2*inch, 1.2*inch, 1*inch])

    table_style = TableStyle([
        #heading (row0)
        ('BACKGROUND', (0,0), (-1,0), prim_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),

        #data (row 1-3)
        ('BACKGROUND', (0,1), (-1,-2), colors.beige),
        ('TEXTCOLOR', (0,1), (-1,-2), colors.black),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),

        #total (last row)
        ('BACKGROUND', (0,-1), (-1,-1), sec_color),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.black),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 11),

        #borders
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('LINEBELOW', (0,0), (-1,0), 2, prim_color),
        ('LINEABOVE', (0,-1), (-1,-1), 2, prim_color),
    ])

    table.setStyle(table_style)
    return table

def createClientsTable():
    
    data = [
        ['Ranking', 'Cliente', 'Total sales', 'State'],
        ['1', 'ABC corporation', '$25,000', 'Active'],
        ['2', 'XYZ industries', '$18,000', 'Active'],
        ['3', 'Global tech Ltd', '$15,000', 'Active'],
        ['4', 'Innovate solutions', '$12,000', 'Pending'],
        ['5', 'Tech Dynamics', '$10,000', 'Active'],
    ]

    table = Table(data, colWidths=[0.8*inch, 2.5*inch, 1.5*inch, 1.2*inch])

    table_style = TableStyle([
        #heading
        ('BACKGROUND', (0,0), (-1,0), accent_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),

        #data
        ('BACKGROUND', (0,1), (-1,-1), accent_color),
        ('ALIGN', (0,1), (-1,-1), 'CENTER'),
        ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
        ('ALIGN', (3,1), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),

        #border
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.lightgrey]),
    ])

    table.setStyle(table_style)
    return table

#create complete report

pdf = SimpleDocTemplate(
    "ProfessionalPdfDoc.pdf",
    pagesizes=letter,
    rightMargin=0.75*inch,
    leftMargin=0.75*inch,
    topMargin=1.2*inch,
    bottomMargin=0.75*inch
)

#list of elements included in pdf
elements = []

#Page 1

#principal heading
title = Paragraph("Monthly sales report", title_style)
elements.append(title)

subtitle = Paragraph("Complete analysis - January 2026")
elements.append(subtitle)

elements.append(Spacer(1, 0.3*inch))

# Executive summary
summarytext = """
Executive Summary:
During January, there was a <b>15% increase</b> in total sales 
compared to the previous month, reaching a total of <b>$125,000</b>. This growth is 
mainly attributed to the 20% increase in sales of Product C, which has 
shown a sustained positive trend over the last three months.
The total number of transactions was <b>45</b>, with an average ticket of <b>$2,777</b>. 
The top three customers account for 46.8% of total sales, indicating 
a significant concentration that requires diversification strategies.
"""

elements.append(Paragraph(summarytext, normal_style))

elements.append(Spacer(1, 0.4*inch))

#table subtitle
elements.append(Paragraph("Breakdown of Sales by Product", subtitle_style))
elements.append(Spacer(1, 0.2*inch))


#add sales table
elements.append(create_sales_table())

elements.append(Spacer(1, 0.4*inch))

#page 2

elements.append(PageBreak())

elements.append(Paragraph("Visual sales analysis", subtitle_style))
elements.append(Spacer(1, 0.2*inch))

#Generate and add graph
graph_dir = create_sales_graph()
elements.append(Image(graph_dir, width=5*inch, height=3.3*inch))

elements.append(Spacer(1, 0.3*inch))

#graph analysis
analysis_text = """
<b>Executive Summary:</b><br/>
During January, there was a <b>15% increase</b> in total sales 
compared to the previous month, reaching a total of <b>$125,000</b>. This growth is 
mainly attributed to the 20% increase in sales of Product C, which has 
shown a sustained positive trend over the last three months.
<br/><br/>
The total number of transactions was <b>45</b>, with an average ticket of <b>$2,777</b>. 
The top three customers account for 46.8% of total sales, indicating 
a significant concentration that requires diversification strategies.
"""

elements.append(Paragraph(analysis_text, normal_style))

elements.append(Spacer(1, 0.4*inch))

#page 3 
elements.append(Paragraph("Top 5 costumer of the month", subtitle_style))
elements.append(Spacer(1, 0.2*inch))

elements.append(createClientsTable())

elements.append(Spacer(1, 0.3*inch))

#recomendations
elements.append(Paragraph("Strategic recomendations", subtitle_style))
elements.append(Spacer(1, 0.1*inch))

recomendations_text = """
<b>1. Customer Diversification:</b> The top three customers account for almost 47% of sales. 
It is recommended to implement customer acquisition strategies to reduce dependency.<br/><br/>

<b>2. Promote Product C:</b> Take advantage of positive momentum with targeted campaigns 
and special promotions.<br/><br/>

<b>3. Recovery of Product B:</b> Conduct a detailed analysis of the causes of the decline 
and adjust the pricing or marketing strategy.<br/><br/>

<b>4. Loyalty:</b> Implement a loyalty program for active customers and recover 
those in pending status.
"""

elements.append(Paragraph(recomendations_text, normal_style))

# build pdf

pdf.build(elements, onFirstPage=add_heading, onLaterPages=add_heading)

pdf.save()

print("✅ PDF nivel 3 creado: reporte_nivel3.pdf")
print("✅ Gráfico generado: grafico_ventas.png")
