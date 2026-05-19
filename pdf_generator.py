"""
Generador de PDFs para recetas médicas — diseño mateouribe
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas as rl_canvas


# Colores del brand
COLOR_BORDER = HexColor("#5B4FCF")       # borde morado
COLOR_NAVY   = HexColor("#1A1A3E")       # "mate" oscuro
COLOR_BLUE   = HexColor("#2B6CB0")       # "ouribe" azul
COLOR_TAGLINE = HexColor("#888888")      # tagline gris
COLOR_TEXT   = HexColor("#1A1A2E")       # texto principal
COLOR_BRAND  = HexColor("#2B1FA8")       # azul marca (encabezado secundario)


def _draw_border(c, width, height):
    """Dibuja el borde morado alrededor de la página."""
    margin = 28
    c.setStrokeColor(COLOR_BORDER)
    c.setLineWidth(2.5)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin, stroke=1, fill=0)


def _draw_logo(c, width, height):
    """Dibuja el logo real de mateouribe desde la imagen extraída del brand PDF."""
    logo_path = os.path.join(os.path.dirname(__file__), "logo_brand.png")
    if not os.path.exists(logo_path):
        return

    logo_w = 5.5 * cm
    logo_h = logo_w * (1037 / 4455)  # mantener proporción original

    x = width - logo_w - 2.8 * cm
    y = 1.2 * cm

    c.drawImage(logo_path, x, y, width=logo_w, height=logo_h, mask="auto")


def _draw_header_info(c, data, width, height):
    """Dibuja fecha, paciente y diagnóstico en la parte superior de la página."""
    top_y = height - 2.2 * cm
    left_x = 3.2 * cm

    c.setFont("Helvetica", 9)
    c.setFillColor(COLOR_TEXT)

    items = []
    if data.get("date"):
        items.append(f"Fecha: {data['date']}")
    if data.get("patient"):
        items.append(f"Paciente: {data['patient']}")
    if data.get("diagnosis"):
        items.append(f"Diagnóstico: {data['diagnosis']}")

    for i, text in enumerate(items):
        c.drawString(left_x, top_y - i * 0.5 * cm, text)


def _draw_medications(c, medications, width, height):
    """Dibuja la lista de medicamentos en el área central de la receta."""
    left_x = 3.2 * cm
    # Empieza desde arriba dependiendo de si hay info de paciente
    start_y = height * 0.72   # aprox 72% desde abajo = 28% desde arriba

    y = start_y

    for med in medications:
        generic = med.get("generic", "")
        brand = med.get("brand", "")
        form_text = med.get("form", "")
        instructions = med.get("instructions", "")

        # Nombre genérico — negrita
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(COLOR_TEXT)
        c.drawString(left_x, y, generic)
        y -= 0.55 * cm

        # Nombre comercial (si existe)
        if brand:
            c.setFont("Helvetica-Oblique", 11)
            c.setFillColor(COLOR_TEXT)
            c.drawString(left_x, y, brand)
            y -= 0.5 * cm

        # Presentación (si existe)
        if form_text:
            c.setFont("Helvetica-Oblique", 11)
            c.setFillColor(COLOR_TEXT)
            c.drawString(left_x, y, form_text)
            y -= 0.5 * cm

        # Instrucciones — siempre se muestra
        if instructions:
            c.setFont("Helvetica-Oblique", 11)
            c.setFillColor(COLOR_TEXT)
            c.drawString(left_x, y, instructions)
            y -= 0.5 * cm

        # Espacio entre medicamentos
        y -= 0.6 * cm


def generate_prescription_pdf(output_path: str, data: dict):
    """
    Genera un PDF de receta médica.

    data keys:
      - patient (str, optional)
      - date (str, optional)
      - diagnosis (str, optional)
      - medications (list of dicts with keys: generic, brand, form, instructions)
    """
    width, height = letter  # 8.5 x 11 pulgadas

    c = rl_canvas.Canvas(output_path, pagesize=letter)

    # Fondo blanco
    c.setFillColor(white)
    c.rect(0, 0, width, height, stroke=0, fill=1)

    _draw_border(c, width, height)
    _draw_header_info(c, data, width, height)
    _draw_medications(c, data.get("medications", []), width, height)
    _draw_logo(c, width, height)

    c.save()
