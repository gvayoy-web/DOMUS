"""Genera los planos ULTIMATE de construcción física de PROJECT DOMUS.

El documento describe únicamente la maqueta en crudo. No contiene diagramas
eléctricos, conexiones, firmware ni instrucciones para instalar sensores.
"""

from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
PDF_OUT = ROOT / "PLANOS_ULTIMATE_CONSTRUCCION_MAQUETA.pdf"
W, H = landscape(A3)

INK = colors.HexColor("#10233f")
NAVY = colors.HexColor("#08111f")
BLUE = colors.HexColor("#155eef")
CYAN = colors.HexColor("#12b8d0")
PALE = colors.HexColor("#eef3f7")
GRID = colors.HexColor("#d8e2ec")
WOOD = colors.HexColor("#efd5ac")
WOOD_DARK = colors.HexColor("#b97a3f")
GLASS = colors.HexColor("#dff5f7")
PURPLE = colors.HexColor("#9b51e0")
GREEN = colors.HexColor("#dff4e8")
RED = colors.HexColor("#c43737")

MODULES = [
    ("Invernadero", 20, 184, 200, 280, GREEN),
    ("Casa abierta", 240, 240, 344, 260, WOOD),
    ("Porche", 272, 57.6, 200, 156, colors.HexColor("#dbeafe")),
    ("Jarvis vacío", 600, 196, 84, 94.4, colors.HexColor("#d6e4ff")),
    ("Gabinete vacío", 696, 188, 88, 120, colors.HexColor("#e6edf3")),
]

MATERIALS = [
    ["M-01", "MDF", "12 mm", "1 pieza 800 × 520", "Base estructural"],
    ["M-02", "Plywood/MDF", "3 mm", "2 láminas 600 × 900 aprox.", "Casa, cubiertas, pisos y faldón"],
    ["M-03", "Acrílico transparente", "1.5 mm", "1 lámina 600 × 900", "Invernadero"],
    ["M-04", "Acrílico transparente", "3 mm", "1 lámina 300 × 450", "Gabinete y tapas removibles"],
    ["M-05", "Listón cuadrado", "7 × 7 mm", "2.5 m", "Bastidores e invernadero"],
    ["M-06", "Listón cuadrado", "8 × 8 mm", "1.2 m", "Porche y cumbrera"],
    ["M-07", "PVC espumado", "2 mm", "1 lámina A3", "Bancales y jardineras"],
    ["M-08", "PET/acetato flexible", "0.5 mm", "4 recortes", "Forros impermeables removibles"],
    ["M-09", "Imán neodimio", "Ø8 × 4 mm", "4 pares", "Techo removible de la casa"],
    ["M-10", "Pasamuros/tapón", "Ø12 mm", "5 unidades", "Accesos futuros, entregados cerrados"],
    ["M-11", "Adhesivo PVA + cemento acrílico", "-", "Según consumo", "Uniones estructurales"],
    ["M-12", "Pintura/sellador", "-", "Negro mate + protector", "Base, cantos y madera"],
]

CUTS = [
    ["B-01", "Base", 1, "MDF 12", "800 × 520", "Cantos escuadrados"],
    ["B-02", "Faldón frontal", 1, "Plywood 3", "800 × 75", "Cuelga 63 mm bajo base"],
    ["B-03", "Tapa canal", 1, "Plywood 3", "552 × 22.4", "Removible"],
    ["C-01", "Piso casa", 1, "Plywood 3", "344 × 260", "Sobre bastidor 7 × 7"],
    ["C-02", "Muro posterior", 1, "Plywood 3", "344 × 225", "Hatch removible 70 × 40"],
    ["C-03", "Muros laterales", 2, "Plywood 3", "260 × 225", "Frente completamente abierto"],
    ["C-04", "Techo casa", 1, "Plywood 3", "356.8 × 272.8", "Removible"],
    ["C-05", "Alero frontal", 1, "Plywood 3", "368 × 17.6", "Bajo techo"],
    ["C-06", "Tabique dormitorio", 1, "Plywood 3", "182.4 × 188", "Desmontable"],
    ["P-01", "Plataforma porche", 1, "Plywood 3", "200 × 156", "Sobre bastidor"],
    ["P-02", "Cubierta porche", 1, "Plywood 3", "212.8 × 168", "Alero perimetral"],
    ["P-03", "Postes porche", 2, "Listón 8 × 8", "134 largo", "Altura libre 134"],
    ["P-04", "Pasarela", 1, "Plywood 3", "46.4 × 88", "Centrada"],
    ["P-05", "Jardineras", 2, "PVC 2", "30.4 × 108 × 26 ext.", "Con forro removible"],
    ["I-01", "Base invernadero", 1, "Plywood 3", "200 × 280", "Sobre bastidor"],
    ["I-02", "Laterales transparentes", 2, "Acrílico 1.5", "280 × 165", "Sin taladros"],
    ["I-03", "Panel posterior", 1, "Acrílico 1.5", "200 × 165", "Sin taladros"],
    ["I-04", "Cubiertas inclinadas", 2, "Acrílico 1.5", "280 × 108.1", "Ángulo 22.3°"],
    ["I-05", "Postes exteriores", 4, "Listón 7 × 7", "165 largo", "Esquinas"],
    ["I-06", "Postes cumbrera", 2, "Listón 7 × 7", "206 largo", "Centro frente/fondo"],
    ["I-07", "Viga cumbrera", 1, "Listón 8 × 8", "280 largo", "Cota superior 225"],
    ["I-08", "Bancales para tierra", 2, "PVC 2", "60.8 × 224 × 42 ext.", "Interior 56.8 × 220 × 38"],
    ["J-01", "Frente Jarvis", 1, "Plywood 3", "84 × 290", "Removible y sin huecos finales"],
    ["J-02", "Fondo Jarvis", 1, "Plywood 3", "84 × 290", "Estructural"],
    ["J-03", "Laterales Jarvis", 2, "Plywood 3", "88.4 × 290", "Entre frente y fondo"],
    ["J-04", "Tapa/fondo horizontal", 2, "Plywood 3", "78 × 88.4", "Caja vacía"],
    ["G-01", "Base gabinete", 1, "Plywood 7", "88 × 120", "Cota Z 12-19"],
    ["G-02", "Fondo gabinete", 1, "Plywood 3", "88 × 250", "Estructural"],
    ["G-03", "Laterales gabinete", 2, "Acrílico 3", "120 × 250", "Transparentes"],
    ["G-04", "Frente gabinete", 1, "Acrílico 3", "88 × 250", "Removible"],
]

HOLES = [
    ["H-01", "Base bajo invernadero", "X 120 / Y 196", "Ø12 pasante", "Colocar tapón; sin cable"],
    ["H-02", "Base bajo casa", "X 400 / Y 250", "Ø12 pasante", "Colocar tapón; sin cable"],
    ["H-03", "Base bajo porche", "X 372 / Y 205", "Ø12 pasante", "Colocar tapón; sin cable"],
    ["H-04", "Base bajo Jarvis", "X 642 / Y 205", "Ø12 pasante", "Colocar tapón; sin cable"],
    ["H-05", "Base bajo gabinete", "X 740 / Y 200", "Ø12 pasante", "Colocar tapón; sin cable"],
    ["H-06", "Techo casa, 4 esquinas", "A 8 mm de cada borde", "Ø8 × 4 prof.", "Alojamiento de imanes"],
    ["H-07", "Hatch muro posterior", "Centrado; borde inf. 15", "70 × 40", "Recorte reutilizado como tapa"],
    ["H-08", "Insertos de bancal", "Local 30 / 112", "16 × 16 removible", "Marcar Ø8; no abrir hasta medir sonda"],
]


def write_csv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def pstyle(size=8, color=INK, bold=False, leading=None, align=TA_LEFT):
    return ParagraphStyle(
        "x", fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=size, leading=leading or size * 1.25, textColor=color,
        alignment=align, spaceAfter=0, spaceBefore=0,
    )


def para(text, size=8, color=INK, bold=False):
    return Paragraph(text, pstyle(size=size, color=color, bold=bold))


def header(c: canvas.Canvas, page: int, code: str, title: str, subtitle: str = ""):
    c.setFillColor(colors.white); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(NAVY); c.rect(0, H - 25 * mm, W, 25 * mm, fill=1, stroke=0)
    c.setFillColor(CYAN); c.setFont("Helvetica-Bold", 8); c.drawString(14 * mm, H - 9 * mm, "PROJECT DOMUS - PLANOS ULTIMATE DE CONSTRUCCIÓN")
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 18); c.drawString(14 * mm, H - 19 * mm, title)
    if subtitle:
        c.setFillColor(colors.HexColor("#52667a")); c.setFont("Helvetica", 7.5); c.drawString(14 * mm, H - 30 * mm, subtitle)
    c.setStrokeColor(colors.HexColor("#9db0c2")); c.line(14 * mm, 14 * mm, W - 14 * mm, 14 * mm)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 7); c.drawRightString(W - 14 * mm, 9 * mm, f"{code} - PÁGINA {page}/10 - REV ULTIMATE 1.0 - COTAS EN mm")


def box_title(c, x, y, w, title, color=BLUE):
    c.setFillColor(color); c.roundRect(x, y - 6 * mm, w, 8 * mm, 1.5 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 7.5); c.drawCentredString(x + w / 2, y - 3.5 * mm, title)


def note_box(c, x, y, w, h, title, lines, color=PALE):
    c.setFillColor(color); c.setStrokeColor(colors.HexColor("#aebdca")); c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 9); c.drawString(x + 5 * mm, y + h - 8 * mm, title)
    c.setFont("Helvetica", 7.5)
    yy = y + h - 16 * mm
    for line in lines:
        c.drawString(x + 5 * mm, yy, line)
        yy -= 6 * mm


def dimension(c, x1, y1, x2, y2, text, vertical=False):
    c.setStrokeColor(BLUE); c.setFillColor(BLUE); c.setLineWidth(0.7)
    c.line(x1, y1, x2, y2)
    if vertical:
        c.line(x1 - 2 * mm, y1, x1 + 2 * mm, y1); c.line(x2 - 2 * mm, y2, x2 + 2 * mm, y2)
        c.saveState(); c.translate(x1 - 2.5 * mm, (y1 + y2) / 2); c.rotate(90); c.setFont("Helvetica-Bold", 7); c.drawCentredString(0, 0, text); c.restoreState()
    else:
        c.line(x1, y1 - 2 * mm, x1, y1 + 2 * mm); c.line(x2, y2 - 2 * mm, x2, y2 + 2 * mm)
        c.setFont("Helvetica-Bold", 7); c.drawCentredString((x1 + x2) / 2, y1 + 2 * mm, text)


def draw_table(c, data, x, y_top, widths, row_h=8 * mm, font=6.5):
    processed = [[para(str(v), font, bold=(ri == 0)) for v in row] for ri, row in enumerate(data)]
    t = Table(processed, colWidths=widths, rowHeights=[row_h] * len(processed))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#a9b8c7")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    tw, th = t.wrap(sum(widths), H)
    t.drawOn(c, x, y_top - th)
    return th


def draw_module_plan(c, ox, oy, scale):
    c.setFillColor(colors.HexColor("#f8fafc")); c.setStrokeColor(INK); c.rect(ox, oy, 800 * scale, 520 * scale, fill=1, stroke=1)
    for name, x, y, w, d, fill in MODULES:
        X, Y = ox + x * scale, oy + y * scale
        c.setFillColor(fill); c.setStrokeColor(INK); c.rect(X, Y, w * scale, d * scale, fill=1, stroke=1)
        # Mantener las etiquetas fuera del mobiliario para que la planta sea inequívoca.
        label_y = Y + 3.2 * mm if name == "Casa abierta" else Y + d * scale / 2
        c.setFillColor(INK); c.setFont("Helvetica-Bold", 6.5); c.drawCentredString(X + w * scale / 2, label_y, name.upper())
    # Zonas que no son piezas: depósito/bomba futuros.
    c.setDash(5, 3); c.setStrokeColor(PURPLE); c.setFillColor(colors.HexColor("#fbf5ff")); c.rect(ox + 20 * scale, oy + 52 * scale, 92 * scale, 92 * scale, fill=1, stroke=1); c.setDash()
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 5.5); c.drawCentredString(ox + 66 * scale, oy + 98 * scale, "HUECO DEPÓSITO")
    # Mobiliario físico de la casa.
    furniture = [(260,457.6,142.4,33.6,"COCINA"),(324,372,94.4,38.4,"ISLA"),(264,280,97.6,44,"SOFÁ"),(436,324,94.4,142.4,"CAMA"),(544,244,36,232,"BAÑO")]
    for x,y,w,d,label in furniture:
        c.setFillColor(colors.white); c.setStrokeColor(colors.HexColor("#7b8b9c")); c.rect(ox+x*scale,oy+y*scale,w*scale,d*scale,fill=1,stroke=1)
        c.setFillColor(INK); c.setFont("Helvetica",4.8); c.drawCentredString(ox+(x+w/2)*scale,oy+(y+d/2)*scale,label)


def page_cover(c):
    header(c, 1, "U-00", "PLANOS ULTIMATE - CONSTRUCCIÓN DE LA MAQUETA", "Documento exclusivo para cortar, perforar, ensamblar y terminar la estructura física")
    render = ROOT / "project_domus_render.png"
    if render.exists():
        c.drawImage(str(render), 15 * mm, 39 * mm, width=255 * mm, height=160 * mm, preserveAspectRatio=True, anchor="c", mask="auto")
    note_box(c, 283*mm, 128*mm, 122*mm, 72*mm, "QUÉ CONSTRUYE EL EQUIPO", [
        "- Base, faldón y tapas removibles.", "- Casa abierta, mobiliario y tabiques.",
        "- Porche, pasarela, jardineras e invernadero.", "- Bancales/macetas con forros removibles.",
        "- Carcasas vacías de Jarvis y gabinete.", "- Pasamuros cerrados y marcas futuras."
    ], colors.HexColor("#e8f1ff"))
    note_box(c, 283*mm, 47*mm, 122*mm, 67*mm, "QUÉ NO CONSTRUYE NI INSTALA", [
        "- No sensores, ESP32, relés o fuente.", "- No cables, conectores ni soldaduras.",
        "- No bomba, tubos ni depósito definitivo.", "- No luces ni paneles solares reales.",
        "- No abrir huecos de sensor sin medir la pieza."
    ], colors.HexColor("#fff0f0"))
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 11); c.drawString(18*mm, 28*mm, "BASE FINAL: 800 × 520 mm - REDUCCIÓN UNIFORME AL 80 % DEL DISEÑO ORIGINAL")
    c.showPage()


def page_layout(c):
    header(c, 2, "U-01", "IMPLANTACIÓN GENERAL Y EJES DE MONTAJE", "Origen X0/Y0 en la esquina frontal izquierda; el faldón PROJECT DOMUS define el frente")
    ox, oy, s = 20*mm, 31*mm, 0.37*mm
    draw_module_plan(c, ox, oy, s)
    dimension(c, ox, oy-8*mm, ox+800*s, oy-8*mm, "800")
    dimension(c, ox-8*mm, oy, ox-8*mm, oy+520*s, "520", True)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 8); c.drawCentredString(ox+400*s, oy-16*mm, "FRENTE / VISITANTE")
    side_x = 326*mm
    note_box(c, side_x, 153*mm, 79*mm, 65*mm, "COORDENADAS", [
        "Invernadero: X20 / Y184", "Casa: X240 / Y240", "Porche: X272 / Y57.6",
        "Jarvis: X600 / Y196", "Gabinete: X696 / Y188", "Depósito futuro: X20 / Y52"
    ])
    note_box(c, side_x, 82*mm, 79*mm, 58*mm, "REGLAS", [
        "1. Marcar todo antes de pegar.", "2. Presentar módulos en seco.",
        "3. No recentrar ningún módulo.", "4. Tolerancia de posición: ±0.5.", "5. Sólido = pieza; punteado = hueco."
    ])
    note_box(c, side_x, 31*mm, 79*mm, 38*mm, "ALTURAS DE PROYECTO", [
        "Casa: Z superior 254", "Invernadero: Z superior 225", "Jarvis: Z superior 302", "Gabinete: Z superior 269"
    ])
    c.showPage()


def page_base(c):
    header(c, 3, "U-02", "BASE, FALDÓN, CANAL VACÍO Y PASAMUROS", "Todas las perforaciones de esta lámina son mecánicas; se entregan sin cables")
    ox, oy, s = 18*mm, 41*mm, 0.34*mm
    c.setFillColor(colors.HexColor("#f7f9fb")); c.setStrokeColor(INK); c.rect(ox, oy, 800*s, 520*s, fill=1, stroke=1)
    # Canal y agujeros.
    c.setFillColor(colors.HexColor("#dbeafe")); c.rect(ox+228*s, oy+22.4*s, 552*s, 22.4*s, fill=1, stroke=1)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 6); c.drawCentredString(ox+(228+276)*s, oy+(22.4+11.2)*s, "CANAL VACÍO 552 × 22.4 - TAPA REMOVIBLE")
    holes=[("H1",120,196),("H2",400,250),("H3",372,205),("H4",642,205),("H5",740,200)]
    for label,x,y in holes:
        X,Y=ox+x*s,oy+y*s; c.setFillColor(colors.white); c.setStrokeColor(RED); c.circle(X,Y,6*s,fill=1,stroke=1); c.line(X-4*s,Y,X+4*s,Y); c.line(X,Y-4*s,X,Y+4*s); c.setFillColor(RED); c.setFont("Helvetica-Bold",5.5); c.drawString(X+4*mm,Y+2*mm,label+" Ø12")
    dimension(c,ox,oy-8*mm,ox+800*s,oy-8*mm,"800")
    dimension(c,ox-8*mm,oy,ox-8*mm,oy+520*s,"520",True)
    note_box(c, 303*mm, 149*mm, 102*mm, 69*mm, "DESPIECE BASE", [
        "B-01 MDF 12: 800 × 520", "B-02 Faldón 3: 800 × 75", "B-03 Tapa canal 3: 552 × 22.4",
        "Faldón: borde superior a Z12", "Borde inferior a Z-63", "Profundidad real del faldón: 3"
    ])
    note_box(c, 303*mm, 76*mm, 102*mm, 61*mm, "PERFORACIÓN", [
        "H1-H5: Ø12 pasante.", "Taladrar con madera apoyada.", "Avellanar: NO.",
        "Colocar tapón removible Ø12.", "No introducir cable ni conector.", "Desbarbar ambas caras."
    ], colors.HexColor("#fff4e8"))
    note_box(c, 303*mm, 31*mm, 102*mm, 33*mm, "ACABADO", ["Sellar MDF antes de pintar.", "Negro mate; no pintar zonas de adhesión.", "Comprobar planitud máxima 1 mm."])
    c.showPage()


def page_house(c):
    header(c, 4, "U-03", "CASA ABIERTA - PLANTA, MUROS Y TECHO", "Huella 344 × 260; frente completamente abierto; altura interior 225")
    ox, oy, s = 22*mm, 38*mm, 0.62*mm
    c.setFillColor(WOOD); c.setStrokeColor(INK); c.rect(ox,oy,344*s,260*s,fill=1,stroke=1)
    # Tabique y mobiliario.
    c.setStrokeColor(INK); c.setLineWidth(1.2); c.line(ox+185.6*s,oy+73.6*s,ox+185.6*s,oy+256*s)
    furn=[(20,217.6,142.4,33.6,"COCINA"),(84,132,94.4,38.4,"ISLA"),(24,40,97.6,44,"SOFÁ"),(196,84,94.4,142.4,"CAMA"),(304,4,36,232,"BAÑO")]
    for x,y,w,d,label in furn:
        c.setFillColor(colors.white); c.setStrokeColor(colors.HexColor("#66798c")); c.rect(ox+x*s,oy+y*s,w*s,d*s,fill=1,stroke=1); c.setFillColor(INK); c.setFont("Helvetica-Bold",5.5); c.drawCentredString(ox+(x+w/2)*s,oy+(y+d/2)*s,label)
    # Frente abierto.
    c.setStrokeColor(CYAN); c.setLineWidth(3); c.line(ox,oy,ox+344*s,oy); c.setFillColor(CYAN); c.setFont("Helvetica-Bold",7); c.drawCentredString(ox+172*s,oy-5*mm,"FRENTE ABIERTO 344")
    dimension(c,ox,oy-12*mm,ox+344*s,oy-12*mm,"344")
    dimension(c,ox-8*mm,oy,ox-8*mm,oy+260*s,"260",True)
    # Elevación/corte.
    ex,ey,es=257*mm,119*mm,.38*mm
    c.setFillColor(WOOD);c.setStrokeColor(INK);c.rect(ex,ey,344*es,225*es,fill=1,stroke=1)
    c.setFillColor(NAVY);c.rect(ex-6.4*es,ey+225*es,356.8*es,10*es,fill=1,stroke=0)
    c.setFillColor(colors.white);c.rect(ex+8*es,ey+15*es,70*es,40*es,fill=1,stroke=1)
    c.setFillColor(INK);c.setFont("Helvetica-Bold",6);c.drawCentredString(ex+43*es,ey+32*es,"HATCH 70 × 40")
    dimension(c,ex,ey-7*mm,ex+344*es,ey-7*mm,"344")
    dimension(c,ex-7*mm,ey,ex-7*mm,ey+225*es,"225",True)
    note_box(c, 257*mm, 38*mm, 148*mm, 65*mm, "PIEZAS Y PERFORACIONES", [
        "Piso: 344 × 260 × 3 sobre bastidor 7 × 7.", "Posterior: 344 × 225 × 3.", "Laterales: 260 × 225 × 3 (2).",
        "Techo removible: 356.8 × 272.8 × 3.", "Hatch posterior: 70 × 40; reutilizar recorte.",
        "4 alojamientos de imán Ø8 × 4 prof., a 8 de cada borde.", "No abrir perforaciones de sensor en paredes."
    ], colors.HexColor("#e8f1ff"))
    c.showPage()


def page_interior(c):
    header(c, 5, "U-04", "INTERIOR DE LA CASA - MOBILIARIO Y TABIQUES", "Las piezas interiores son parte visual de la maqueta; pueden fabricarse como volúmenes huecos")
    data=[["Código","Elemento","Cantidad","Medida exterior","Material / criterio"],
          ["F-01","Mueble bajo cocina",1,"142.4 × 33.6 × 68","Plywood 3; caja hueca"],
          ["F-02","Encimera cocina",1,"147.2 × 38.4 × 7","Madera 3 + separadores"],
          ["F-03","Refrigerador",1,"38.4 × 52.8 × 138","Foamboard 3; volumen hueco"],
          ["F-04","Isla",1,"94.4 × 38.4 × 70","Plywood 3; tapa 102.4 × 46.4"],
          ["F-05","Sofá",1,"97.6 × 44 × 52","Foamboard + tela/EVA"],
          ["F-06","Mesa sala",1,"56 × 38.4 × 31","Madera 2-3"],
          ["F-07","Cama",1,"94.4 × 142.4 × 61","Base 37 + colchón 24"],
          ["F-08","Mesa de noche",1,"30.4 × 30.4 × 42","Madera 2-3"],
          ["F-09","Baño esquemático",1,"36 × 232 de zona","Acrílico/blanco; sin tubería"],
          ["F-10","Tabique dormitorio",1,"182.4 × 188 × 3","Plywood 3; removible"]]
    draw_table(c,data,18*mm,H-39*mm,[24*mm,58*mm,24*mm,56*mm,88*mm],row_h=13*mm,font=7)
    note_box(c, 280*mm, 118*mm, 125*mm, 84*mm, "POSICIONES LOCALES DESDE CASA X0/Y0", [
        "Cocina: X20 / Y217.6", "Isla: X84 / Y132", "Sofá: X24 / Y40",
        "Cama: X196 / Y84", "Baño: X304 / Y4", "Tabique: X185.6 / Y73.6",
        "Puerta: ancho 57.6; alto 174", "Mantener pasillo central mínimo 24."
    ])
    note_box(c, 280*mm, 39*mm, 125*mm, 64*mm, "CRITERIO DE CONSTRUCCIÓN", [
        "- Se permite simplificar tiradores y textiles.", "- No cambiar huellas ni posiciones.",
        "- Ningún mueble debe ocultar H-02.", "- Baño decorativo: no conectar agua.",
        "- Presentar en seco antes de fijar.", "- Tolerancia de mobiliario: ±1 mm."
    ], colors.HexColor("#f3f7fb"))
    c.showPage()


def page_porch(c):
    header(c, 6, "U-05", "PORCHE, PASARELA Y JARDINERAS", "Plataforma 200 × 156; cubierta 212.8 × 168; cubierta inferior en Z154")
    ox,oy,s=27*mm,55*mm,.78*mm
    c.setFillColor(colors.HexColor("#dbeafe"));c.setStrokeColor(INK);c.rect(ox,oy,200*s,156*s,fill=1,stroke=1)
    c.setFillColor(WOOD_DARK);c.rect(ox+80*s,oy-40*s,46.4*s,88*s,fill=1,stroke=1)
    # planters
    for x in (16,152):
        c.setFillColor(GREEN);c.rect(ox+x*s,oy+16*s,30.4*s,108*s,fill=1,stroke=1)
        c.setFillColor(INK);c.setFont("Helvetica-Bold",5);c.saveState();c.translate(ox+(x+15.2)*s,oy+70*s);c.rotate(90);c.drawCentredString(0,0,"JARDINERA 30.4 × 108");c.restoreState()
    for x in (4,188):
        c.setFillColor(WOOD_DARK);c.rect(ox+x*s,oy+2*s,8*s,8*s,fill=1,stroke=1)
    dimension(c,ox,oy-8*mm,ox+200*s,oy-8*mm,"200")
    dimension(c,ox-7*mm,oy,ox-7*mm,oy+156*s,"156",True)
    # section
    sx,sy=245*mm,132*mm
    c.setFillColor(WOOD_DARK);c.rect(sx,sy,200*.55*mm,3*mm,fill=1,stroke=1)
    c.rect(sx+4*.55*mm,sy+3*mm,8*.55*mm,134*.55*mm,fill=1,stroke=1);c.rect(sx+188*.55*mm,sy+3*mm,8*.55*mm,134*.55*mm,fill=1,stroke=1)
    c.setFillColor(NAVY);c.rect(sx-6.4*.55*mm,sy+137*.55*mm,212.8*.55*mm,3*mm,fill=1,stroke=1)
    dimension(c,sx-7*mm,sy,sx-7*mm,sy+134*.55*mm,"134 libre",True)
    note_box(c, 245*mm, 48*mm, 160*mm, 62*mm, "JARDINERAS (2 UNIDADES)", [
        "Exterior: 30.4 × 108 × 26; PVC 2 mm.", "Interior útil: 26.4 × 104 × 22.",
        "Altura máxima de tierra: 18; dejar 4 libres.", "Forro PET removible; no pegar al cajón.",
        "Marcar 2 centros Ø3 en el forro, sin perforar aún.", "Volumen de tierra recomendado: 45-50 mL cada una."
    ], colors.HexColor("#edf8f1"))
    c.showPage()


def page_greenhouse(c):
    header(c, 7, "U-06", "INVERNADERO Y BANCALES PARA TIERRA", "Huella 200 × 280; cumbrera Z225; paneles transparentes sin sensores ni tuberías")
    # Front elevation
    ox,oy,s=25*mm,105*mm,.82*mm
    c.setStrokeColor(INK);c.setLineWidth(1.2);c.setFillColor(GLASS)
    c.line(ox,oy,ox,oy+165*s);c.line(ox,oy+165*s,ox+100*s,oy+206*s);c.line(ox+100*s,oy+206*s,ox+200*s,oy+165*s);c.line(ox+200*s,oy+165*s,ox+200*s,oy);c.line(ox,oy,ox+200*s,oy)
    # beds
    for x in (18.4,104):
        c.setFillColor(colors.HexColor("#7b4a2d"));c.rect(ox+x*s,oy,60.8*s,42*s,fill=1,stroke=1)
    dimension(c,ox,oy-8*mm,ox+200*s,oy-8*mm,"200")
    dimension(c,ox-8*mm,oy,ox-8*mm,oy+206*s,"206 al apoyo",True)
    c.setFillColor(INK);c.setFont("Helvetica-Bold",7);c.drawCentredString(ox+100*s,oy+214*s,"CUMBRERA SUPERIOR Z225")
    # Top plan
    px,py,ps=220*mm,90*mm,.58*mm
    c.setFillColor(GREEN);c.rect(px,py,200*ps,280*ps,fill=1,stroke=1)
    for x in (18.4,104):
        c.setFillColor(colors.HexColor("#8a5230"));c.rect(px+x*ps,py+28*ps,60.8*ps,224*ps,fill=1,stroke=1)
    c.setFillColor(colors.white);c.rect(px+79.2*ps,py+28*ps,24.8*ps,224*ps,fill=1,stroke=1)
    c.setFillColor(INK);c.setFont("Helvetica-Bold",5.5);c.saveState();c.translate(px+91.6*ps,py+140*ps);c.rotate(90);c.drawCentredString(0,0,"PASILLO 24.8");c.restoreState()
    dimension(c,px,py-8*mm,px+200*ps,py-8*mm,"200")
    dimension(c,px-8*mm,py,px-8*mm,py+280*ps,"280",True)
    note_box(c, 337*mm, 134*mm, 68*mm, 82*mm, "DESPIECE", [
        "Base: 200 × 280 × 3", "Laterales: 280 × 165 × 1.5 (2)", "Posterior: 200 × 165 × 1.5",
        "Techo: 280 × 108.1 × 1.5 (2)", "Pendiente: 22.3°", "Postes ext.: 7 × 7 × 165 (4)",
        "Postes cumbrera: 7 × 7 × 206 (2)", "Viga: 8 × 8 × 280"
    ])
    note_box(c, 337*mm, 43*mm, 68*mm, 76*mm, "BANCAL / MACETA (2)", [
        "Exterior: 60.8 × 224 × 42", "Pared/fondo: PVC 2", "Interior: 56.8 × 220 × 38",
        "Tierra máxima: 30 de alto", "Volumen aprox.: 0.375 L cada uno", "Inserto removible: 16 × 16",
        "Marcar Ø8 para futura sonda", "No perforar hasta medir sensor"
    ], colors.HexColor("#edf8f1"))
    c.showPage()


def page_boxes(c):
    header(c, 8, "U-07", "CARCASAS VACÍAS: JARVIS Y GABINETE", "Se construyen y entregan sin pantalla, placa, relés, altavoz, cables ni perforaciones definitivas")
    # Jarvis front and side.
    jx,jy,js=28*mm,44*mm,.58*mm
    c.setFillColor(NAVY);c.setStrokeColor(INK);c.rect(jx,jy,84*js,290*js,fill=1,stroke=1)
    c.setFillColor(BLUE);c.rect(jx+12.8*js,jy+43*js,58.4*js,220*js,fill=1,stroke=0)
    c.setDash(4,3);c.setStrokeColor(PURPLE);c.setFillColor(colors.Color(1,1,1,alpha=.1));
    for x,y,w,h,label in [(12,190,60,32,"PANTALLA"),(24,125,37,37,"ALTAVOZ"),(30,60,25,25,"BOTÓN")]:
        c.rect(jx+x*js,jy+y*js,w*js,h*js,fill=0,stroke=1);c.setFillColor(colors.white);c.setFont("Helvetica-Bold",4.5);c.drawCentredString(jx+(x+w/2)*js,jy+(y+h/2)*js,label)
    c.setDash();dimension(c,jx,jy-8*mm,jx+84*js,jy-8*mm,"84");dimension(c,jx-8*mm,jy,jx-8*mm,jy+290*js,"290",True)
    note_box(c, 90*mm, 125*mm, 108*mm, 88*mm, "JARVIS - DESPIECE", [
        "Frente/fondo: 84 × 290 × 3 (2)", "Laterales: 88.4 × 290 × 3 (2)", "Tapa y base interior: 78 × 88.4 × 3 (2)",
        "Panel azul decorativo: 58.4 × 220 × 1.5", "Frente fijado con 4 tornillos M2 o imanes.",
        "Contornos morados: grabar/marcar 0.3 prof.", "NO cortar pantalla, micrófono, altavoz o botón.", "Altura de proyecto desde Z0: 302."
    ], colors.HexColor("#e8f1ff"))
    # Cabinet.
    gx,gy,gs=220*mm,55*mm,.62*mm
    c.setFillColor(GLASS);c.setStrokeColor(INK);c.rect(gx,gy,88*gs,250*gs,fill=1,stroke=1)
    c.setDash(4,3);c.setStrokeColor(PURPLE);c.rect(gx+8*gs,gy+10*gs,72*gs,225*gs,fill=0,stroke=1);c.setDash()
    dimension(c,gx,gy-8*mm,gx+88*gs,gy-8*mm,"88");dimension(c,gx-8*mm,gy,gx-8*mm,gy+250*gs,"250",True)
    note_box(c, 292*mm, 120*mm, 113*mm, 93*mm, "GABINETE - DESPIECE", [
        "Base: 88 × 120 × 7", "Fondo: 88 × 250 × 3", "Laterales: 120 × 250 × 3 (2)",
        "Frente removible: 88 × 250 × 3", "Interior útil aprox.: 82 × 114 × 244", "No instalar bandeja electrónica.",
        "No taladrar ventilación todavía.", "Dejar 4 puntos de fijación M2 marcados.", "Altura de proyecto desde Z0: 269."
    ])
    note_box(c, 220*mm, 43*mm, 185*mm, 58*mm, "REGLA DE ENTREGA", [
        "Las dos carcasas deben abrirse sin herramientas especiales y quedar completamente vacías.",
        "Las marcas moradas no son agujeros: indican zonas sacrificables para la integración posterior.",
        "Proteger el acrílico durante el armado y retirar la película solo al final."
    ], colors.HexColor("#fff4e8"))
    c.showPage()


def page_holes(c):
    header(c, 9, "U-08", "PERFORACIONES, INSERTOS Y PIEZAS REMOVIBLES", "Diferenciar claramente: TALADRAR AHORA, MARCAR SOLAMENTE y NO PERFORAR")
    table=[["ID","Ubicación","Centro / referencia","Acción","Entrega"]]+HOLES
    draw_table(c,table,16*mm,H-40*mm,[22*mm,65*mm,62*mm,52*mm,85*mm],row_h=13*mm,font=7)
    note_box(c, 302*mm, 139*mm, 103*mm, 74*mm, "TALADRAR AHORA", [
        "- H-01 a H-05: Ø12 pasante.", "- H-06: alojamientos Ø8 × 4 prof.", "- H-07: hatch 70 × 40.",
        "- Desbarbar, sellar y probar tapas.", "- Entregar H-01 a H-05 con tapón.", "- No pasar ningún cable."
    ], colors.HexColor("#edf8f1"))
    note_box(c, 302*mm, 70*mm, 103*mm, 56*mm, "MARCAR SOLAMENTE", [
        "- Ø8 en insertos de bancales.", "- Zonas de pantalla/micrófono/altavoz.",
        "- Puntos M2 del gabinete.", "- Centros de drenaje Ø3 en forros.", "- Usar línea fina morada o grabado suave."
    ], colors.HexColor("#fbf5ff"))
    note_box(c, 302*mm, 31*mm, 103*mm, 27*mm, "NO PERFORAR", ["Paneles transparentes del invernadero, muebles, baño ni fachadas visibles.", "Toda apertura variable se confirma con el componente físico."] , colors.HexColor("#fff0f0"))
    c.showPage()


def page_schedules(c):
    header(c, 10, "U-09", "MATERIALES, LISTA DE CORTE Y CONTROL DE CALIDAD", "Comprar por espesor; verificar el calibre real con pie de rey antes de cortar")
    mat=[['ID','Material','Espesor/sección','Cantidad','Uso']]+MATERIALS
    draw_table(c,mat,14*mm,H-39*mm,[20*mm,52*mm,34*mm,64*mm,80*mm],row_h=9.6*mm,font=6.2)
    checks=[
        "□ Base 800 × 520, plana y escuadrada.", "□ Módulos en las coordenadas U-01.",
        "□ Casa de una planta y frente abierto.", "□ Techo, hatch y frentes removibles.",
        "□ Bancales y jardineras con forro removible.", "□ Invernadero sin grietas ni tensión.",
        "□ H-01 a H-05 cerrados con tapones.", "□ Marcas futuras visibles pero sin cortar.",
        "□ Jarvis y gabinete completamente vacíos.", "□ Sin sensores, cables, bomba o conexiones.",
    ]
    note_box(c, 278*mm, 75*mm, 127*mm, 102*mm, "CONTROL DE CALIDAD ANTES DE ENTREGAR", checks, colors.HexColor("#edf8f1"))
    note_box(c, 278*mm, 31*mm, 127*mm, 32*mm, "ARCHIVOS COMPLEMENTARIOS", ["Lista de corte completa: lista_corte_ultimate.csv", "Perforaciones: perforaciones_y_accesos.csv", "Materiales: materiales_ultimate.csv"])
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 8); c.drawString(16*mm, 58*mm, "TOLERANCIAS")
    c.setFont("Helvetica", 7.3); c.drawString(16*mm, 49*mm, "Corte estructural ±0.5 - Mobiliario ±1.0 - Perforaciones ±0.3 - Escuadra máxima 0.5 por 300 - Planitud base máxima 1.0")
    c.drawString(16*mm, 38*mm, "Orden obligatorio: marcar → presentar en seco → perforar → sellar cantos → pegar → probar removibles → pintar → inspeccionar.")
    c.showPage()


def main():
    write_csv(ROOT / "materiales_ultimate.csv", ["id","material","espesor_seccion","cantidad_estimada","uso"], MATERIALS)
    write_csv(ROOT / "lista_corte_ultimate.csv", ["codigo","pieza","cantidad","material","medida_mm","observacion"], CUTS)
    write_csv(ROOT / "perforaciones_y_accesos.csv", ["id","ubicacion","centro_referencia_mm","accion","entrega"], HOLES)
    c = canvas.Canvas(str(PDF_OUT), pagesize=landscape(A3), pageCompression=1)
    c.setTitle("PROJECT DOMUS - Planos Ultimate de construcción de maqueta")
    for fn in (page_cover, page_layout, page_base, page_house, page_interior, page_porch, page_greenhouse, page_boxes, page_holes, page_schedules):
        fn(c)
    c.save()
    print(PDF_OUT)


if __name__ == "__main__":
    main()
