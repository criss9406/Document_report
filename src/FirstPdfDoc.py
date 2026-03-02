#importaciones
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pathlib import Path

#obtener ruta para outputs (destino del pdf)
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)  # crea la carpeta si no existe

pdf_path = OUTPUT_DIR / "FirstTestFile.pdf"

#crear canvas
pdf = canvas.Canvas(str(pdf_path), pagesize=letter)

#dibujar contenido
pdf.drawString(100,750, "hello world") #(x, y , text)

#guarda el archivo
pdf.save()
