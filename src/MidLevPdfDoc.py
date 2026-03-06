from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, white
from pathlib import Path

from BasicPdfDoc import H

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok = True)

pdf_path = OUTPUT_DIR / "MidLevPdfDoc.pdf"

# Brand color configurations
prim_color = HexColor('#2E5090')
sec_color = HexColor('#7FB3D5')
accent_color = HexColor('#E74C3C')
text_color = HexColor('#2C3E50')

# Helper functions

def AddHeading(pdf, H, W):
    """
    Reusable function to add corporate header
    """

    # heading background    
    pdf.setFillColor(prim_color)
    pdf.rect(0, H-100, W, 100, fill=True, stroke=False)

    # heading text
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(50, H-50, "Sales report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, H-70, "monthly analysis - January 2026")

    # separator line
    pdf.setStrokeColor(accent_color)
    pdf.setLineWidth(3)
    pdf.line(50, H-85, W-50, H-85)

def AddSection(pdf, title, Y0, data):
    """
    Function to add a section with title and data
    """

    #Section title
    pdf.setFillColor(prim_color)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, Y0, title)

    #Line under the heading
    pdf.setStrokeColor(sec_color)
    pdf.setLineWidth(1)
    pdf.line(50, Y0-5, 300, Y0-5)

    #section content
    pdf.setFillColor(text_color)
    pdf.setFont("Helvetica", 11)

    yc = Y0 - 25
    for linea in data:
        pdf.drawString(70, yc, linea)
        yc -= 20

    return yc #return y in final position


def AddFeaturedBox(pdf, x, y, boxWidth, text, Value):
    """
    Create a visual chart to highlight important metrics
    """

    #box background
    pdf.setFillColor(sec_color)
    pdf.setStrokeColor(prim_color)
    pdf.setLineWidth(2)
    pdf.rect(x, y, boxWidth, 60, fill=True, stroke=True)

    #label
    pdf.setFillColor(prim_color)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x+10, y+40, Value)

    #value
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(x+10, y+15, text)

def AddFooter(pdf, W, pageNum):
    """
    Footer with standard information
    """

    pdf.setFillColor(text_color)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(50, 30, "Automatically generated document | Python + ReportLab")

    pdf.drawString(W-100, 30, f"Page {pageNum}")

    #Upper decorative line
    pdf.setStrokeColor(sec_color)
    pdf.setLineWidth(1)
    pdf.line(50, 50, W-50, 50)


#create report
pdf = canvas.Canvas(str(pdf_path), pagesize=letter)

W, H = letter

#heading
AddHeading(pdf, H, W)

#Key metrics table
y_metrics = H-170
AddFeaturedBox(pdf, 50, y_metrics, 150, "Total sales", "$125,000")
AddFeaturedBox(pdf, 220, y_metrics, 150, "Transaction", "$45")
AddFeaturedBox(pdf, 390, y_metrics, 150, "Average ticket", "$2,777")

#section 1: Executive Summary
yc = y_metrics - 40
SummaryData = [
    "• 15% increase compared to the previous month",
    "• Largest sale: $8,500 (Customer ABC Corp)",
    "• Highest sales day: 15 January ($12,000)"
]

yc = AddSection(pdf, "Excecutive summary", yc, SummaryData)

#section 2: Breakdown by Product
yc -= 40
productData = [
    "Product A: $50,000 (40%) ↑ 10%",
    "Product B: $45,000 (36%) ↑ 5%",
    "Product C: $30,000 (24%) ↑ 20%",
]

yc = AddSection(pdf, "Analysis by Product", yc, productData)

#Section 3: Top 3 clients
yc -=40
clientsData = [
    "1. ABC Corp        $25,000",
    "2. XYZ industries  $18,000",
    "3. Global tech     $15,000",
]

yc = AddSection(pdf, "Top 3 Clients", yc, clientsData)

#page footer
AddFooter(pdf, H, 1)

