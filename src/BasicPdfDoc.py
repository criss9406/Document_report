from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from pathlib import Path

#obtener ruta para outputs (destino del pdf)
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)  # crea la carpeta si no existe

pdf_path = OUTPUT_DIR / "BasicPdfDoc.pdf"

#crear canvas
pdf = canvas.Canvas(str(pdf_path), pagesize=letter)

#get format dimentions haight and width
w, H = letter

#step 2: report content

#título
pdf.drawString(100, 750, "reporte de ventas mensual")


#subtitulo
pdf.drawString(100, 730, "mes: enero 2026")

#separador (línea horizontal)
pdf.line(100, 720, 500, 720) #(x1, y1, x2, y2)

#conteido principal
pdf.drawString(100, 690, "Resumen ejecutivo:")
pdf.drawString(100, 670, "-Total de ventas: $125,000")
pdf.drawString(100, 650, "-Número de transacciones: 45")
pdf.drawString(100, 630, "-Ticket promedio: $2,777")

#sección 2
pdf.drawString(100, 590, "Analisis por producto:")
pdf.drawString(120, 570, "1. Producto A: $50,000 (40%)")
pdf.drawString(120, 550, "2. Producto B: $45,000 (36%)")
pdf.drawString(120, 530, "3. Producto C: $30,000 (24%)")

#pie de página
pdf.drawString(100, 50, "Generado automáticamente con Python + ReportLab")
pdf.drawString(450, 50, "Página 1")

#step 3: save pdf
pdf.save()
