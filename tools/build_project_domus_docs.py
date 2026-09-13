from __future__ import annotations

import os
from pathlib import Path
from datetime import date

from PIL import Image, ImageDraw, ImageFont, ImageColor
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ROOT / "documentos"
QA = ROOT / "qa_docx"
OUT.mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)

BLUE = "1459C7"
BLUE_DARK = "0B2B57"
CYAN = "39BDEB"
INK = "18212E"
MUTED = "5D6B7A"
PALE = "EAF2FF"
PALE2 = "F3F7FC"
WOOD = "B77B48"
GREEN = "2E8B57"
RED = "BC3B3B"
WHITE = "FFFFFF"
BLACK = "111111"

# Pillow expects a leading '#', while python-docx expects six hexadecimal
# characters. Register the shared palette as valid Pillow color names so the
# same tokens can safely be used by both renderers.
for _hex in (BLUE, BLUE_DARK, CYAN, INK, MUTED, PALE, PALE2, WOOD, GREEN, RED, WHITE, BLACK):
    ImageColor.colormap[_hex.lower()] = "#" + _hex


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/aptos.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    if bold:
        candidates = [
            Path("C:/Windows/Fonts/aptos-bold.ttf"),
            Path("C:/Windows/Fonts/calibrib.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
        ] + candidates
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def rounded(draw, xy, radius=18, fill=WHITE, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def line_arrow(draw, start, end, fill=BLUE_DARK, width=4):
    draw.line([start, end], fill=fill, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) > abs(y2 - y1):
        s = 1 if x2 > x1 else -1
        pts = [(x2, y2), (x2 - 12*s, y2 - 7), (x2 - 12*s, y2 + 7)]
    else:
        s = 1 if y2 > y1 else -1
        pts = [(x2, y2), (x2 - 7, y2 - 12*s), (x2 + 7, y2 - 12*s)]
    draw.polygon(pts, fill=fill)


def make_plan_v2(path: Path):
    im = Image.new("RGB", (1800, 1260), "white")
    d = ImageDraw.Draw(im)
    f_title, f_sub, f_label, f_small = font(54, True), font(30, True), font(24, True), font(20)
    d.text((70, 42), "PROJECT DOMUS · PLANTA TÉCNICA DEFINITIVA", font=f_title, fill=BLUE_DARK)
    d.text((70, 108), "Base 100 × 70 cm · vivienda compacta modular · cotas orientativas", font=f_sub, fill=MUTED)

    x0, y0, scale = 180, 220, 13
    w, h = 100*scale, 70*scale
    d.rectangle((x0, y0, x0+w, y0+h), fill="#F7F1E9", outline=INK, width=5)
    # Zones in centimeters mapped to pixels.
    def zone(x, y, zw, zh, fill, title, subtitle=""):
        box = (x0+x*scale, y0+y*scale, x0+(x+zw)*scale, y0+(y+zh)*scale)
        d.rectangle(box, fill=fill, outline=INK, width=4)
        d.text((box[0]+18, box[1]+14), title, font=f_label, fill=INK)
        if subtitle:
            d.text((box[0]+18, box[1]+50), subtitle, font=f_small, fill=MUTED)
        return box

    greenhouse = zone(2, 10, 30, 45, "#D8F2E3", "INVERNADERO", "30 × 45 cm")
    house = zone(34, 2, 60, 35, "#E9DFD1", "CASA", "60 × 35 cm · techo removible")
    tower = zone(67, 38, 15, 28, "#DCE8FA", "JARVIS", "15 × 28 cm")
    bay = zone(83, 38, 15, 28, "#E4E7EC", "SERVICIO", "huella 15 × 28 cm")
    # Interior optimized after selecting the final design.
    def inner(x, y, zw, zh, title, fill):
        box = (x0+x*scale, y0+y*scale, x0+(x+zw)*scale, y0+(y+zh)*scale)
        d.rectangle(box, fill=fill, outline="#80715F", width=2)
        d.text((box[0]+8, box[1]+7), title, font=font(16, True), fill=INK)
        return box
    inner(35, 14, 22, 22, "SALA", "#E8DED1")
    inner(35, 3, 24, 10, "COCINA + BARRA", "#E4D2BA")
    inner(60, 8, 22, 28, "DORMITORIO · CAMA DOBLE", "#F0E2D2")
    inner(83, 3, 10, 16, "BAÑO", "#E5ECEF")

    courtyard = (x0+34*scale, y0+39*scale, x0+65*scale, y0+64*scale)
    d.rounded_rectangle(courtyard, radius=24, fill="#E8D6B6", outline=WOOD, width=4)
    d.text((courtyard[0]+35, courtyard[1]+82), "ENTRADA CUBIERTA", font=f_label, fill=INK)
    d.text((courtyard[0]+60, courtyard[1]+126), "31 × 25 cm + rampa", font=f_small, fill=MUTED)

    # Cable trench.
    d.line([(x0+34*scale, y0+67*scale), (x0+98*scale, y0+67*scale)], fill=BLUE, width=12)
    d.text((x0+41*scale, y0+64*scale), "canal de cables 5 cm", font=f_small, fill=BLUE_DARK)

    points = [
        (greenhouse[0]+90, greenhouse[1]+180, "H", "Humedad de suelo"),
        (greenhouse[0]+145, greenhouse[3]-90, "A", "Nivel de agua / bomba"),
        (x0+49*scale, y0+24*scale, "T", "DHT11 ventilado"),
        (x0+60*scale, y0+37*scale, "P", "PIR en acceso"),
        (x0+76*scale, y0+2*scale, "L", "LDR bajo alero"),
        (tower[0]+95, tower[1]+110, "J", "Micrófono + aro + altavoz"),
        (bay[0]+90, bay[1]+150, "E", "ESP32 + relés + fusible"),
    ]
    for px, py, code, label in points:
        d.ellipse((px-22, py-22, px+22, py+22), fill=BLUE, outline=WHITE, width=3)
        tw = d.textbbox((0, 0), code, font=f_label)[2]
        d.text((px-tw/2, py-16), code, font=f_label, fill=WHITE)

    # Dimensions.
    d.line((x0, y0-42, x0+w, y0-42), fill=INK, width=3)
    d.line((x0, y0-58, x0, y0-25), fill=INK, width=3)
    d.line((x0+w, y0-58, x0+w, y0-25), fill=INK, width=3)
    d.text((x0+w/2-60, y0-82), "100 cm", font=f_label, fill=INK)
    d.line((x0-45, y0, x0-45, y0+h), fill=INK, width=3)
    d.line((x0-60, y0, x0-26, y0), fill=INK, width=3)
    d.line((x0-60, y0+h, x0-26, y0+h), fill=INK, width=3)
    d.text((x0-145, y0+h/2-15), "70 cm", font=f_label, fill=INK)

    # Legend.
    lx, ly = 1500, 230
    d.text((lx, ly), "LEYENDA", font=f_sub, fill=BLUE_DARK)
    for i, (_, _, code, label) in enumerate(points):
        yy = ly + 55 + i*55
        d.ellipse((lx, yy, lx+34, yy+34), fill=BLUE)
        d.text((lx+10, yy+5), code, font=font(18, True), fill=WHITE)
        d.text((lx+48, yy+3), label, font=f_small, fill=INK)
    d.text((lx, ly+465), "Seguridad", font=f_sub, fill=RED)
    safety = ["Solo 5 V/USB en exposición", "Agua a ≥25 cm de electrónica", "Techos y paneles removibles", "Batería accesible y con fusible"]
    for i, t in enumerate(safety):
        d.text((lx, ly+515+i*43), "• " + t, font=f_small, fill=INK)
    im.save(path, quality=95)


def make_plan_v1(path: Path):
    im = Image.new("RGB", (1800, 1260), "white")
    d = ImageDraw.Draw(im)
    f_title, f_sub, f_label, f_small = font(54, True), font(30, True), font(24, True), font(20)
    d.text((70, 42), "PROJECT DOMUS · ALZADO TÉCNICO — OPCIÓN A", font=f_title, fill=BLUE_DARK)
    d.text((70, 108), "Casa elevada sobre invernadero · base común 100 × 70 cm", font=f_sub, fill=MUTED)
    bx, by = 150, 1020
    d.rectangle((bx, by, 1430, by+70), fill="#6C4B33", outline=INK, width=4)
    # lower greenhouse
    d.rectangle((300, 690, 1040, 1020), fill="#D8F2E3", outline=INK, width=5)
    d.text((535, 820), "INVERNADERO 55 × 35 × 22 cm", font=f_label, fill=INK)
    # upper house
    d.rectangle((355, 365, 1135, 690), fill="#E9DFD1", outline=INK, width=5)
    d.polygon([(315, 365), (745, 145), (1175, 365)], fill="#4A5564", outline=INK)
    d.text((565, 475), "CASA 60 × 35 cm", font=f_label, fill=INK)
    d.text((560, 520), "muros 25 cm · techo removible", font=f_small, fill=MUTED)
    # service panel
    d.rectangle((1180, 555, 1540, 1020), fill="#E4E7EC", outline=INK, width=5)
    d.text((1230, 625), "PANEL DE", font=f_label, fill=INK)
    d.text((1210, 665), "SERVICIO", font=f_label, fill=INK)
    d.text((1225, 710), "25 × 35 cm", font=f_small, fill=MUTED)
    # solar
    d.polygon([(690, 205), (965, 270), (885, 345), (610, 280)], fill="#214E9B", outline=INK)
    d.text((720, 250), "PANEL SOLAR", font=f_small, fill=WHITE)
    # points
    pts = [
        (430, 755, "H", "Humedad tierra"), (770, 740, "T", "DHT11"),
        (935, 930, "A", "Agua/bomba"), (465, 430, "P", "PIR"),
        (1060, 385, "L", "LDR"), (1280, 500, "J", "Jarvis"),
        (1370, 840, "E", "ESP32/relés")]
    for x, y, code, _ in pts:
        d.ellipse((x-22, y-22, x+22, y+22), fill=BLUE, outline=WHITE, width=3)
        d.text((x-9, y-16), code, font=f_label, fill=WHITE)
    # dimensions
    d.line((250, 1125, 1550, 1125), fill=INK, width=3)
    d.line((250, 1108, 250, 1142), fill=INK, width=3)
    d.line((1550, 1108, 1550, 1142), fill=INK, width=3)
    d.text((830, 1142), "100 cm", font=f_label, fill=INK)
    d.line((1600, 145, 1600, 1090), fill=INK, width=3)
    d.text((1620, 590), "≈72 cm", font=f_label, fill=INK)
    lx, ly = 90, 180
    d.text((lx, ly), "CLAVE", font=f_sub, fill=BLUE_DARK)
    for i, (_, _, c, lab) in enumerate(pts):
        d.text((lx, ly+50+i*38), f"{c}  {lab}", font=f_small, fill=INK)
    d.text((1180, 1080), "No sellar el panel de servicio.", font=f_small, fill=RED)
    im.save(path, quality=95)


def make_architecture(path: Path):
    im = Image.new("RGB", (1800, 950), "white")
    d = ImageDraw.Draw(im)
    ft, fh, fb, fs = font(52, True), font(28, True), font(23, True), font(19)
    d.text((65, 35), "ARQUITECTURA LOCAL DE PROJECT DOMUS", font=ft, fill=BLUE_DARK)
    stages = [
        ("SENSORES", "DHT11 · suelo · LDR\nPIR · nivel de agua"),
        ("ESP32-S3", "validación · reglas\ndespachador seguro"),
        ("ACTUADORES", "luces · bomba\nventilador · pantalla"),
    ]
    xs = [80, 650, 1220]
    for x, (title, sub) in zip(xs, stages):
        rounded(d, (x, 190, x+430, 390), 22, PALE2, BLUE, 4)
        d.text((x+30, 220), title, font=fh, fill=BLUE_DARK)
        d.multiline_text((x+30, 275), sub, font=fs, fill=INK, spacing=10)
    line_arrow(d, (510, 290), (630, 290), BLUE_DARK, 5)
    line_arrow(d, (1080, 290), (1200, 290), BLUE_DARK, 5)

    rounded(d, (300, 520, 1500, 810), 28, "#EAF6FF", BLUE, 4)
    d.text((340, 550), "JARVIS LOCAL (FASE DE VOZ)", font=fh, fill=BLUE_DARK)
    flow = ["INMP441", "‘Jarvis’", "TinyML", "orden segura", "PicoTTS", "MAX98357A"]
    fx = 350
    for i, label in enumerate(flow):
        rounded(d, (fx, 640, fx+150, 715), 16, WHITE, CYAN, 3)
        tw = d.textbbox((0,0), label, font=fb)[2]
        d.text((fx+75-tw/2, 663), label, font=fb, fill=INK)
        if i < len(flow)-1:
            line_arrow(d, (fx+153, 677), (fx+185, 677), BLUE_DARK, 3)
        fx += 190
    d.text((420, 755), "Modelos y voz en flash · audio y tensores temporales en PSRAM · no requiere microSD", font=fs, fill=MUTED)
    d.text((80, 865), "Wi‑Fi es opcional: MQTT, Home Assistant, panel local, OTA y control de Spotify mediante un reproductor autorizado.", font=fs, fill=INK)
    im.save(path, quality=95)


def make_wall_plan(path: Path):
    """Deterministic cutting/elevation sheet for the selected one-level house."""
    im = Image.new("RGB", (1800, 1260), "white")
    d = ImageDraw.Draw(im)
    ft, fh, fb, fs = font(48, True), font(28, True), font(21, True), font(18)
    d.text((65, 38), "PROJECT DOMUS · DESPIECE DE CASA", font=ft, fill=BLUE_DARK)
    d.text((65, 98), "Cotas en centímetros · comprobar el espesor del material antes de pegar", font=fh, fill=MUTED)

    pieces = [
        ("H-W1 · muro trasero", "60 × 25", 60, 25, [(12, 12, 8, 6), (37, 12, 10, 7), (53, 17, 5, 5)]),
        ("H-W2 · lateral izquierdo", "35 × 25", 35, 25, []),
        ("H-W3 · lateral derecho", "35 × 25", 35, 25, [(15, 16, 5, 5)]),
        ("H-P1 · sala/dormitorio", "22 × 25", 22, 25, [(2, 0, 7, 20)]),
        ("H-P2 · cocina/dormitorio", "10 × 25", 10, 25, []),
        ("H-P3 · frente de baño", "10 × 25", 10, 25, [(2, 0, 6, 20)]),
        ("H-P4 · dormitorio/baño", "17 × 25", 17, 25, []),
    ]
    positions = [(70, 205), (850, 205), (70, 565), (650, 565), (1040, 565), (1240, 565), (1480, 565)]
    scales = [10, 13, 13, 13, 13, 13, 10]
    for (title, dims, pw, ph, openings), (x, y), sc in zip(pieces, positions, scales):
        short_id = title.split(" · ", 1)[0]
        d.text((x, y - 38), f"{short_id} · {dims}", font=fb, fill=INK)
        box = (x, y, x + pw * sc, y + ph * sc)
        d.rectangle(box, fill="#E8DED1", outline=INK, width=4)
        for ox, oy, ow, oh in openings:
            ob = (x + ox*sc, y + (ph-oy-oh)*sc, x + (ox+ow)*sc, y + (ph-oy)*sc)
            d.rectangle(ob, fill="white", outline=BLUE, width=3)
    d.text((1390, 150), "Contorno azul = abertura", font=fs, fill=MUTED)
    d.text((70, 945), "PIEZAS COMPLEMENTARIAS", font=fh, fill=BLUE_DARK)
    notes = [
        "H-F1  piso: 60 × 35",
        "H-R1  techo removible: 64 × 39",
        "H-W4  dintel frontal: 60 × 4",
        "H-C1/C2  postes: 2 × 25 (2 unidades)",
        "Frente abierto para exposición; acrílico 60 × 22 opcional.",
        "Ventanas: cocina 8×6, dormitorio 10×7, baño 5×5.",
        "Puertas interiores: 7×20; baño: 6×20.",
    ]
    for i, note in enumerate(notes):
        col = 0 if i < 4 else 1
        row = i if i < 4 else i - 4
        d.text((70 + col*800, 1000 + row*42), "• " + note, font=fs, fill=INK)
    im.save(path, quality=95)


def make_modules_plan(path: Path):
    im = Image.new("RGB", (1800, 1100), "white")
    d = ImageDraw.Draw(im)
    ft, fh, fb, fs = font(48, True), font(27, True), font(20, True), font(18)
    d.text((65, 38), "PROJECT DOMUS · MÓDULOS AUXILIARES", font=ft, fill=BLUE_DARK)
    d.text((65, 98), "Invernadero, torre Jarvis, bahía técnica y acceso", font=fh, fill=MUTED)

    cards = [
        (70, 190, 820, 505, "INVERNADERO · 30 × 45 × 25", [
            "Piso 30×45; zócalos laterales 45×6 (2)",
            "zócalos frontal/trasero 30×6 (2)",
            "costillas transparentes 45×18 (2)",
            "testeros 30×25 (2); cubierta 47×20 (2)",
            "depósito en esquina frontal izquierda; bomba junto a él",
            "sonda de suelo al centro; electrónica sobre el zócalo seco",
        ]),
        (930, 190, 1730, 505, "TORRE JARVIS · 15 × 28 × 32", [
            "laterales 28×32 (2); frente/fondo 15×32 (2)",
            "tapa y base 15×28", "micrófono: abertura 8–12 mm a 25 cm de altura",
            "aro WS2812 bajo el micrófono", "altavoz: recorte según pieza, 12–15 cm más abajo",
            "botón MIC OFF accesible; sin LCD1602 en esta torre",
        ]),
        (70, 590, 820, 980, "BAHÍA DE SERVICIO", [
            "huella real 15×28; altura sugerida 28 cm",
            "panel transparente frontal 22×28 puede sobresalir 7 cm",
            "LCD1602, ESP32, relés, fusible e interruptor aquí",
            "USB y fusible accesibles; ventilación superior",
            "no colocar depósito, bomba ni tuberías encima",
        ]),
        (930, 590, 1730, 980, "ENTRADA · 31 × 25", [
            "plataforma 31×25; cubierta 31×18",
            "rampa 8×24; pasillo libre mínimo 6 cm",
            "4 postes de 1×1×18; baranda de 4 cm de alto",
            "PIR sobre el dintel, a 20 cm del piso de la maqueta",
            "canal de cables de 5 cm detrás de Jarvis y servicio",
        ]),
    ]
    for x1, y1, x2, y2, title, notes in cards:
        rounded(d, (x1, y1, x2, y2), 22, PALE2, BLUE, 4)
        d.text((x1+28, y1+25), title, font=fh, fill=BLUE_DARK)
        for i, note in enumerate(notes):
            d.text((x1+35, y1+88+i*39), "• " + note, font=fs, fill=INK)
    im.save(path, quality=95)


PLAN_V2 = ASSETS / "plano_tecnico_domus_opcion_b.png"
PLAN_V1 = ASSETS / "plano_tecnico_domus_opcion_a.png"
ARCH = ASSETS / "arquitectura_project_domus.png"
WALL_PLAN = ASSETS / "plano_despiece_paredes_domus.png"
MODULES_PLAN = ASSETS / "plano_modulos_domus.png"
make_plan_v2(PLAN_V2)
make_plan_v1(PLAN_V1)
make_architecture(ARCH)
make_wall_plan(WALL_PLAN)
make_modules_plan(MODULES_PLAN)


def shade_cell(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = tcPr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tcPr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_text(cell, text, bold=False, color=INK, size=9):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(str(text))
    r.bold = bold
    r.font.name = "Calibri"
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_repeat_table_header(row):
    trPr = row._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)


def prevent_row_split(row):
    trPr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    cant_split.set(qn("w:val"), "true")
    trPr.append(cant_split)


def add_table(doc, headers, rows, widths=None, font_size=8.5):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    hdr = table.rows[0]
    set_repeat_table_header(hdr)
    prevent_row_split(hdr)
    for i, h in enumerate(headers):
        set_cell_text(hdr.cells[i], h, True, WHITE, 9)
        shade_cell(hdr.cells[i], BLUE_DARK)
    for ri, row in enumerate(rows):
        cells = table.add_row().cells
        prevent_row_split(table.rows[-1])
        for i, v in enumerate(row):
            set_cell_text(cells[i], v, False, INK, font_size)
            if ri % 2:
                shade_cell(cells[i], PALE2)
    if widths:
        for row in table.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def set_cell_margins(cell, top=70, start=70, bottom=70, end=70):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = tcPr.first_child_found_in("w:tcMar")
    if tcMar is None:
        tcMar = OxmlElement("w:tcMar")
        tcPr.append(tcMar)
    for m, val in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tcMar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tcMar.append(node)
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")


def page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("PROJECT DOMUS  ·  ")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor.from_string(MUTED)
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)


def configure(doc: Document, subtitle: str):
    sec = doc.sections[0]
    sec.top_margin = Inches(0.65)
    sec.bottom_margin = Inches(0.65)
    sec.left_margin = Inches(0.72)
    sec.right_margin = Inches(0.72)
    sec.header_distance = Inches(0.3)
    sec.footer_distance = Inches(0.3)
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(9.5)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.08
    for sty, sz, color, before, after in [
        ("Title", 30, BLUE_DARK, 0, 8),
        ("Subtitle", 13, MUTED, 0, 10),
        ("Heading 1", 18, BLUE_DARK, 15, 7),
        ("Heading 2", 13, BLUE, 11, 5),
        ("Heading 3", 10.5, INK, 8, 3),
    ]:
        s = styles[sty]
        s.font.name = "Calibri"
        s.font.size = Pt(sz)
        s.font.bold = sty != "Subtitle"
        s.font.color.rgb = RGBColor.from_string(color)
        s.paragraph_format.space_before = Pt(before)
        s.paragraph_format.space_after = Pt(after)
        s.paragraph_format.keep_with_next = True
    if "Callout" not in styles:
        s = styles.add_style("Callout", WD_STYLE_TYPE.PARAGRAPH)
        s.font.name = "Calibri"
        s.font.size = Pt(9.5)
        s.font.color.rgb = RGBColor.from_string(BLUE_DARK)
        s.paragraph_format.left_indent = Inches(0.18)
        s.paragraph_format.right_indent = Inches(0.18)
        s.paragraph_format.space_before = Pt(4)
        s.paragraph_format.space_after = Pt(7)
    hp = sec.header.paragraphs[0]
    hp.text = subtitle.upper()
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.runs[0].font.size = Pt(8)
    hp.runs[0].font.bold = True
    hp.runs[0].font.color.rgb = RGBColor.from_string(BLUE)
    page_number(sec.footer.paragraphs[0])


def cover(doc, kicker, title, subtitle, hero: Path | None, status):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(kicker.upper())
    r.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor.from_string(CYAN)
    p = doc.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(title)
    p = doc.add_paragraph(style="Subtitle")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(subtitle)
    if hero and hero.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(hero), width=Inches(6.65))
    t = doc.add_table(rows=1, cols=3)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c in t.rows[0].cells:
        shade_cell(c, PALE)
        set_cell_margins(c, 90, 120, 90, 120)
    vals = [("PLATAFORMA", "ESP32‑S3 N16R8"), ("PRINCIPIO", "Local primero"), ("ESTADO", status)]
    for c, (a, b) in zip(t.rows[0].cells, vals):
        c.text = ""
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(a + "\n")
        r.bold = True; r.font.size = Pt(8); r.font.color.rgb = RGBColor.from_string(BLUE)
        r = p.add_run(b)
        r.bold = True; r.font.size = Pt(10); r.font.color.rgb = RGBColor.from_string(INK)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Documento actualizado · 1 de septiembre de 2026 · Honduras")
    r.font.size = Pt(8.5); r.font.color.rgb = RGBColor.from_string(MUTED)
    doc.add_page_break()


def callout(doc, title, text, color=BLUE):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    shade_cell(cell, PALE if color == BLUE else "FFF4E5")
    set_cell_margins(cell, 100, 140, 100, 140)
    p = cell.paragraphs[0]
    r = p.add_run(title + "\n")
    r.bold = True; r.font.size = Pt(10); r.font.color.rgb = RGBColor.from_string(color)
    r = p.add_run(text)
    r.font.size = Pt(9.5); r.font.color.rgb = RGBColor.from_string(INK)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def bullets(doc, items, level=0):
    for item in items:
        p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
        p.paragraph_format.space_after = Pt(2)
        p.add_run(item)


def numbered(doc, items):
    for index, item in enumerate(items, start=1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.22)
        p.paragraph_format.first_line_indent = Inches(-0.18)
        p.paragraph_format.space_after = Pt(3)
        p.add_run(f"{index}.  {item}")


def add_picture(doc, path, width=6.7, caption=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(width))
    if caption:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(caption)
        r.italic = True; r.font.size = Pt(8); r.font.color.rgb = RGBColor.from_string(MUTED)


def add_toc_note(doc):
    callout(doc, "Cómo usar este documento", "Corresponde al diseño modular definitivo de un nivel. Las cotas son de fabricación para la maqueta; verifica el espesor real del cartón o plywood y presenta como pendiente cualquier módulo que todavía no hayas comprado o validado.")


def build_technical():
    doc = Document()
    configure(doc, "Documento técnico")
    hero = ASSETS / "project_domus_diseno_definitivo.png"
    cover(doc, "Identidad y memoria técnica", "PROJECT DOMUS", "Casa inteligente local, modular y demostrable", hero, "Diseño modular definitivo")
    add_toc_note(doc)

    doc.add_heading("1. Resumen ejecutivo", 1)
    doc.add_paragraph("PROJECT DOMUS es una maqueta escolar de casa inteligente gobernada por un ESP32‑S3 N16R8. Integra medición ambiental, iluminación, ventilación y riego. Las funciones críticas se ejecutan localmente: si no hay teléfono, Wi‑Fi o internet, la automatización básica continúa.")
    callout(doc, "Promesa honesta", "El firmware doméstico y las pruebas aisladas de micrófono y síntesis de voz ya existen. Jarvis local todavía requiere comprar el hardware de audio, entrenar los modelos en español y validarlos en la placa; por eso permanece deshabilitado en el firmware principal.", RED)

    doc.add_heading("2. Identidad del proyecto", 1)
    add_table(doc, ["Elemento", "Definición"], [
        ("Nombre", "PROJECT DOMUS"),
        ("Idea central", "Una casa que automatiza tareas y conserva el control local."),
        ("Lema recomendado", "Inteligencia local. Hogar responsable."),
        ("Paleta", "Azul cobalto, azul claro, negro técnico, blanco y madera reciclada."),
        ("Tono", "Tecnológico, claro, responsable y sin promesas de ciencia ficción."),
        ("Mensaje de banner", "PROJECT DOMUS · Automatización, voz local y energía responsable."),
    ], widths=[1.4, 5.2])
    doc.add_paragraph("El símbolo ‘D’ azul puede mantenerse como monograma. En banners debe acompañarse del nombre completo para que el público recuerde el proyecto y no solamente el logotipo.")

    doc.add_heading("3. Problema, objetivo y alcance", 1)
    doc.add_heading("Problema", 2)
    doc.add_paragraph("El uso ineficiente de agua y electricidad, la falta de supervisión y la dependencia de servicios externos dificultan una vivienda realmente resiliente. La maqueta demuestra una alternativa económica, explicable y ampliable.")
    doc.add_heading("Objetivo general", 2)
    doc.add_paragraph("Construir y demostrar una casa inteligente segura que mida su entorno, controle cargas de baja tensión y reciba órdenes locales específicas en español mediante un ESP32‑S3.")
    doc.add_heading("Alcance demostrable", 2)
    bullets(doc, [
        "Lectura de temperatura, humedad ambiental, humedad de suelo, luz y nivel de agua.",
        "Control de luces, bomba y ventilador con prioridad entre modo manual y automático.",
        "Corte independiente de la bomba después de dos minutos continuos.",
        "Pantalla y aro WS2812 como retroalimentación visual.",
        "BLE para diagnóstico o control de respaldo.",
        "Voz local en español como fase de integración: palabra ‘Jarvis’, intenciones TinyML y respuesta PicoTTS.",
        "Wi‑Fi opcional para MQTT, panel local, Home Assistant, OTA y Spotify mediante un reproductor autorizado.",
    ])
    doc.add_heading("Fuera de alcance", 2)
    bullets(doc, [
        "No es un LLM conversacional general ni una réplica de la IA de Iron Man.",
        "No reproduce el catálogo de Spotify directamente desde el ESP32.",
        "No controla tensión de red en la exposición; todas las cargas serán de baja tensión.",
        "No se afirmará autonomía solar hasta medir consumo, carga y duración real.",
    ])

    doc.add_heading("4. Arquitectura del sistema", 1)
    add_picture(doc, ARCH, 6.8, "Flujo principal: sensores → decisiones seguras → actuadores; voz y Wi‑Fi son capas separadas.")
    doc.add_heading("Cómo funcionará Jarvis", 2)
    numbered(doc, [
        "El INMP441 captura audio mono a 16 kHz.",
        "Un modelo pequeño detecta la palabra de activación ‘Jarvis’.",
        "Se abre una ventana breve y un clasificador TinyML identifica una intención permitida.",
        "La intención pasa por el mismo despachador seguro que usa el control manual y la automatización.",
        "El firmware construye una respuesta a partir del resultado real: ‘He apagado…’, ‘Ya estaba…’ o ‘No pude…’.",
        "PicoTTS sintetiza la frase en español; MAX98357A y el altavoz la reproducen.",
        "Mientras habla, el micrófono se pausa para evitar autoactivación.",
    ])
    callout(doc, "Dónde se guarda", "Flash: firmware, modelos TinyML y recursos de PicoTTS. PSRAM: audio, características y tensores temporales. NVS: calibraciones y credenciales. La microSD es opcional para registros o efectos; no almacena la ‘inteligencia’ principal.")

    doc.add_heading("5. Estado real del desarrollo", 1)
    add_table(doc, ["Área", "Estado", "Evidencia / siguiente paso"], [
        ("Firmware doméstico", "Implementado", "Relés, sensores, BLE, automatización y manejo seguro."),
        ("Bomba", "Implementado", "Corte máximo continuo de 120 s."),
        ("Despachador", "Implementado", "Unifica voz, manual, automático y futuro Wi‑Fi."),
        ("INMP441", "PoC preparado", "Falta módulo y validación física a 16 kHz."),
        ("PicoTTS", "PoC preparado", "Falta MAX98357A, altavoz y prueba española en placa."),
        ("Wake word", "Pendiente", "Recolectar muestras y entrenar detector ‘Jarvis’."),
        ("Intenciones", "Pendiente", "Entrenar conjunto limitado de órdenes españolas."),
        ("Wi‑Fi / MQTT", "Pendiente opcional", "Añadir después de estabilizar el núcleo local."),
        ("Solar", "Pendiente de medición", "Probar primero con fuente regulada; dimensionar después."),
    ], widths=[1.2, 1.15, 4.4])

    doc.add_heading("6. Inventario confirmado", 1)
    doc.add_paragraph("Se toma como autoridad la lista más reciente proporcionada. Los elementos mencionados en documentos antiguos, pero ausentes de esta lista, se consideran pendientes de compra.")
    add_table(doc, ["Grupo", "Disponible"], [
        ("Control", "ESP32‑S3 N16R8, Raspberry Pi Pico, ESP8266."),
        ("Sensores", "DHT11/DHT22, HC‑SR04, PIR, MPU6050, nivel de agua, humedad de suelo resistiva, LDR, Reed, termistor e inclinación."),
        ("Actuadores", "Relé 1 canal, SG90, bomba+tubo, motor+aspa, L293D, LEDs y WS2812."),
        ("Interfaz", "LCD1602 + I2C, RC522, IR, keypad, joystick, matriz y displays."),
        ("Audio", "DFPlayer Mini, buzzer activo y pasivo. No hay micrófono I2S, amplificador I2S ni altavoz confirmado."),
        ("Montaje y herramientas", "Protoboard, jumpers M/M y H/M, rígidos U‑Shape, resistencias, transistores, diodos, capacitores pequeños y multímetro."),
        ("Energía", "Dos TP4056 USB‑C protegidos. No se confirma panel, 18650, portabatería, CN3065 ni regulador de 5 V."),
    ], widths=[1.15, 5.6])

    doc.add_heading("7. Lista de compras priorizada", 1)
    doc.add_heading("A. Esencial para una demostración estable", 2)
    add_table(doc, ["Compra", "Cant.", "Por qué", "Referencia / costo"], [
        ("Fuente regulada 5 V / 3 A USB‑C con switch", "1", "Alimenta ESP32, LED, relés y audio; incorpora apagado físico.", "C&D variante exacta: L350. La USB‑C sin switch cuesta L250; L248 corresponde a micro‑USB."),
        ("Módulo relé 4 canales, 5 V/10 A", "1", "Con el relé de 1 canal que ya tienes cubre cinco cargas.", "C&D: L250. Variantes: 1ch L80, 2ch L170, 4ch L250, 8ch L395."),
        ("Portafusible de panel + fusible cerámico 3 A, 5×20 mm", "1 + 2 repuestos", "Protección frente a corto; respetar el mismo tamaño físico.", "C&D: portafusible L40; cada fusible L15."),
        ("JST/PCT y cable 22 AWG", "1 lote", "Conexiones firmes y desmontables.", "C&D: 3 pares JST L45; 4 PCT L40; cable 22 AWG desde L35. Confirmar existencias."),
        ("Capacitor electrolítico 1000 µF, ≥10 V", "1", "Reduce caídas por bomba, audio y LED.", "C&D: paquete de 5 por L35. El valor 1000 µF es suficiente; no exigir 2200 µF."),
    ], widths=[1.55, .45, 2.55, 2.05], font_size=8)
    callout(doc, "Subtotal esencial verificado", "L770 con fuente USB‑C con switch, relé de 4 canales, portafusible, un fusible, JST, cable y capacitores. No incluye envío, PCT opcional, fusibles de repuesto ni materiales de maqueta.")
    doc.add_heading("B. Voz local de Jarvis", 2)
    add_table(doc, ["Compra", "Cant.", "Decisión técnica", "Referencia / costo"], [
        ("INMP441", "1", "Micrófono digital I2S; no sustituir por KY‑037 analógico.", "No encontrado en catálogos locales consultados; pedir/importar."),
        ("MAX98357A", "1", "I2S a altavoz, evita DAC analógico externo.", "C&D: L130, stock indicado por el sitio."),
        ("Altavoz 4 Ω / 3 W", "1", "Potencia adecuada al MAX98357A.", "C&D: L90."),
        ("74AHCT125 o 74HCT14", "1", "Eleva datos de WS2812 de 3.3 V a 5 V.", "No encontrado localmente; pedir/importar."),
        ("Aro WS2812 de 8 LED", "0", "Ya tienes tira; puede doblarse o montarse como arco.", "Comprar aro solo por estética."),
    ], widths=[1.45, .4, 2.75, 2.05], font_size=8)
    doc.add_heading("C. Fase solar — comprar después de medir", 2)
    doc.add_paragraph("La capacidad se dimensiona desde la carga real de 5 V, no desde el número de módulos: C[mAh] = (5 V × Ipromedio × 2 h ÷ 3.7 V ÷ 0.85) × 1.25. Se supone 85 % de eficiencia del elevador y 25 % de reserva por envejecimiento, temperatura y picos.")
    add_table(doc, ["Consumo medio a 5 V", "Capacidad calculada", "Decisión para 2 h"], [
        ("0.40 A · electrónica ligera", "≈3,180 mAh", "Una celda de 2,500–2,800 mAh no alcanza con margen; usar ≥4,000 mAh."),
        ("0.70 A · demostración realista", "≈5,560 mAh", "Mínimo práctico 6,000 mAh; medir antes de comprar."),
        ("1.00 A · bomba/voz/LED frecuentes", "≈7,950 mAh", "Objetivo 7,500–8,000 mAh y convertidor probado para los picos."),
    ], widths=[2.1, 1.55, 3.1], font_size=8)
    callout(doc, "Respuesta directa: autonomía", "Para prometer dos horas sin reinicios, diseña para 6,000 mAh como mínimo y para 7,500–8,000 mAh si la bomba, el amplificador o varios LEDs funcionarán con frecuencia. Una sola 18650 de 2,500–2,800 mAh no es suficiente. La cifra final se confirma midiendo la corriente media y el pico con la maqueta completa.")
    callout(doc, "Panel de la captura: no comprar esa variante", "El panel seleccionado de 3 V/110 mA entrega solo 0.33 W en condiciones nominales. No alcanza la entrada mínima de 4.4 V del CN3065 y tampoco puede sostener la casa. En C&D sí aparece una variante 5 V/1,100 mA por L280; la página mezcla 1,100 mA con 4.5 W, por lo que se debe confirmar la etiqueta y medir voltaje/corriente antes de conectarlo.", RED)

    doc.add_heading("Arquitectura eléctrica correcta", 3)
    doc.add_paragraph("Panel 5–6 V → CN3065 → paquete 1S en paralelo → BMS 1S → fusible → interruptor general → elevador estable a 5 V → capacitor y distribución de cargas. El panel nunca se conecta directamente a la batería. La batería tampoco se conecta directamente al ESP32 ni al panel.")
    add_table(doc, ["Elemento / opción", "Tienda y precio visto", "Decisión exacta"], [
        ("Panel 5 V / 1,100 mA", "C&D · L280", "Opción local preferida para CN3065; comprobar que bajo sol mantenga ≥4.4 V. La corriente disponible puede exceder 500 mA: el CN3065 limita la carga."),
        ("2 × 18650 Steren 2,800 mAh", "Steren HN · 2 × L249 = L498", "Pack 1S2P de 5,600 mAh: solo aceptarlo si la medición media es ≤0.65 A; queda justo para 2 h."),
        ("3 × 18650 BAK 2,500 mAh", "C&D · 3 × L180 = L540", "Pack 1S3P de 7,500 mAh: opción con más margen. Usar celdas nuevas, idénticas y al mismo voltaje."),
        ("Portacelda 18650 individual", "C&D · L55 c/u", "Preferible para construir 1S2P/1S3P verificable. El portador doble con tapa e interruptor cuesta L110, pero no se compra hasta confirmar con multímetro que sea paralelo, no serie."),
        ("BMS 1S 20 A", "C&D · L85", "Protección del paquete frente a sobrecarga, sobredescarga y sobrecorriente. No sustituye al cargador solar."),
        ("CN3065", "C&D · L135", "Cargador solar para litio 1S, entrada 4.4–6 V y carga de hasta 500 mA. No sustituye al BMS."),
        ("MT3608 USB-C", "C&D · L90", "Eleva 3–4.2 V a 5 V. Usarlo solo si mantiene 5.0 V durante el pico real sin calentamiento excesivo; la cifra comercial de 2 A no garantiza 2 A continuos."),
        ("Módulo power-bank 5 V/2.1 A", "C&D · L120", "Alternativa más integrada con protección y salida USB. Es más cómoda para respaldo USB, pero no se considera controlador solar ni sistema con reparto de carga sin prueba/documentación adicional."),
        ("Interruptor KCD1-101 ON/OFF", "C&D · L25", "Es suficiente y económico como corte general entre P+ del BMS y el elevador."),
        ("Palanca SPST 82600, 15 A", "Steren HN · L55", "Alternativa mecánicamente más robusta. No mejora el voltaje: solo ofrece mejor montaje y accionamiento."),
        ("Capacitor 4,700 µF / 25 V", "C&D · L60", "Valor estándar cercano a 4,000 µF. Montarlo en la barra de 5 V respetando polaridad."),
        ("Capacitor 6,800 µF / 25 V", "C&D · L35", "Alternativa local de mayor capacidad y menor precio visto; confirmar tamaño físico y existencia."),
    ], widths=[1.65, 1.6, 3.5], font_size=7.4)

    callout(doc, "¿Sirve un capacitor de unos 4,000 µF?", "Sí, como apoyo frente a picos muy breves; 4,700 µF es el valor comercial cercano. A 1 A, 4,700 µF pierde ≈0.21 V en 1 ms y ≈1.06 V en 5 ms: no reemplaza una batería ni corrige un convertidor insuficiente. Añade también 100 nF junto a cada módulo y 10–100 µF cerca del ESP32 y del audio; separa bomba/relés en otra rama y usa cables cortos.")
    callout(doc, "Carga y uso simultáneos", "El módulo CN3065 consultado no documenta una salida con reparto de carga (power-path). Para la demostración segura, cargar con la casa apagada y después operar desde la batería. Si se desea funcionamiento continuo mientras carga, comprar un gestor solar 1S con power-path explícito; no asumir que cualquier placa power-bank lo incorpora.", RED)

    doc.add_heading("Baterías recicladas y pilas normales", 3)
    bullets(doc, [
        "No mezclar celdas recicladas de distinta marca, capacidad, edad o voltaje. Para una maqueta escolar se recomiendan celdas nuevas y auténticas; una celda reciclada solo se acepta tras medir capacidad, resistencia interna y autodescarga, y si no tiene golpes, óxido, calentamiento o deformación.",
        "No soldar con cautín directamente sobre una 18650 desnuda. Usar portaceldas o un paquete unido por soldadura por puntos por una persona con experiencia.",
        "Las alcalinas AA/9 V no son recargables y nunca se conectan al CN3065. La batería rectangular de 9 V tampoco entrega bien los picos de ESP32, relés, bomba y audio.",
        "Las NiMH recargables requieren cargador NiMH y otra regulación; una batería de plomo de 12 V requiere cargador de plomo y un convertidor reductor. Ninguna usa CN3065 ni BMS 1S.",
        "El fusible sigue siendo obligatorio aunque exista BMS. Verificar polaridad y ajustar el elevador a 5.0 V con multímetro antes de conectar el ESP32.",
    ])
    callout(doc, "Presupuesto solar orientativo", "Con 3 celdas BAK (7,500 mAh), panel, tres portaceldas, BMS, CN3065, MT3608, KCD1 y capacitor de 6,800 µF: L1,355 antes de fusible, cableado y envío. Con 2 celdas Steren (5,600 mAh) y dos portaceldas: L1,258, pero solo es válida si la medición demuestra ≤0.65 A de consumo medio.")
    doc.add_heading("D. Opcional", 2)
    doc.add_paragraph("La microSD es opcional para registros o efectos. Ya tienes DFPlayer Mini con ranura, así que no compres otro lector salvo que quieras registro independiente. El módulo C&D de L149 declara SDHC de hasta 32 GB; por eso una tarjeta de 64 GB no es una combinación garantizada. Busca 8–32 GB SDHC y confirma compatibilidad/formato FAT32.")
    callout(doc, "Envío a Choluteca", "C&D tiene venta en línea y publica una sección de entregas, pero el costo, plazo y cobertura exacta a Choluteca deben confirmarse por teléfono/WhatsApp o en el carrito antes de pagar. El inventario y los precios pueden cambiar.", RED)

    doc.add_heading("8. Diseño físico definitivo", 1)
    doc.add_paragraph("Se seleccionó la vivienda modular de un nivel sobre base de 100 × 70 cm. La revisión corrige la cama desproporcionada y el espacio frontal sin función: ahora la casa combina sala, cocina con barra, dormitorio con cama doble, baño compacto y una entrada cubierta con rampa y captación de lluvia demostrativa.")
    add_table(doc, ["Zona", "Medida", "Uso optimizado"], [
        ("Casa", "60 × 35 cm", "Techo removible y circulación continua."),
        ("Sala", "22 × 22 cm aprox.", "Sofá, TV y demostración de iluminación/presencia."),
        ("Cocina", "24 × 10 cm + barra", "Gabinetes, fregadero, cocina y comedor para dos."),
        ("Dormitorio", "22 × 28 cm", "Cama doble proporcional, mesas y armario poco profundo."),
        ("Baño", "10 × 16 cm", "Ducha y sanitario con partición corrediza."),
        ("Entrada", "31 × 25 cm", "Porche, rampa y punto de captación de lluvia."),
        ("Invernadero", "30 × 45 cm", "Cultivo, riego, depósito y sensores."),
    ], widths=[1.25, 1.45, 4.05])
    add_picture(doc, PLAN_V2, 6.75, "Planta definitiva: espacios domésticos útiles y módulos técnicos separados.")

    doc.add_heading("9. Planos, paredes y coordenadas de montaje", 1)
    doc.add_paragraph("Referencia de planta: origen (0,0) en la esquina trasera izquierda de la base; X aumenta hacia la derecha y Y hacia el frente. Todas las medidas son centímetros. La tolerancia de corte recomendada es ±2 mm en plywood y ±3 mm en cartón.")
    add_table(doc, ["Zona", "Coordenadas X", "Coordenadas Y", "Qué va allí"], [
        ("Invernadero", "2–32", "10–55", "Cultivo, depósito, bomba, nivel y humedad de suelo."),
        ("Casa", "34–94", "2–37", "Cocina, sala, dormitorio y baño."),
        ("Entrada", "34–65", "39–64", "Porche, rampa, PIR y circulación de demostración."),
        ("Jarvis", "67–82", "38–66", "INMP441, WS2812, MAX98357A, altavoz y MIC OFF."),
        ("Servicio", "83–98", "38–66", "Huella 15×28; LCD1602, ESP32, relés, fusible e interruptor."),
        ("Canal técnico", "34–98", "65–70", "Cableado desmontable; tapa de 5 cm."),
    ], widths=[1.3, 1.1, 1.1, 3.2], font_size=8.1)
    add_picture(doc, WALL_PLAN, 6.75, "Despiece de muros: el frente queda abierto para que el público vea el interior.")
    add_table(doc, ["ID", "Pieza terminada", "Aberturas / colocación"], [
        ("H‑W1", "Muro trasero 60×25", "Ventanas: cocina 8×6 desde x=12; dormitorio 10×7 desde x=37; ventilación de baño 5×5 desde x=53."),
        ("H‑W2", "Lateral izquierdo 35×25", "Sólido; recibe el borde izquierdo del techo."),
        ("H‑W3", "Lateral derecho 35×25", "Ventilación de baño 5×5; no tapar la bahía técnica."),
        ("H‑W4", "Dintel frontal 60×4 + dos postes 2×25", "Frente abierto; panel de acrílico 60×22 opcional y removible."),
        ("H‑P1", "Sala/dormitorio 22×25", "Puerta 7×20 junto al extremo frontal."),
        ("H‑P2", "Cocina/dormitorio 10×25", "Sólido; los gabinetes pueden ocultar el cableado."),
        ("H‑P3", "Frente de baño 10×25", "Abertura 6×20 o puerta corrediza."),
        ("H‑P4", "Dormitorio/baño 17×25", "Sólido; separa la zona húmeda del dormitorio."),
        ("H‑F1 / H‑R1", "Piso 60×35 / techo 64×39", "Techo único removible con voladizo de 2 cm."),
    ], widths=[.8, 2.15, 3.8], font_size=8)
    doc.add_heading("Posición de cada pared", 2)
    doc.add_paragraph("Para esta tabla usa un segundo origen en la esquina trasera izquierda del piso de la casa; X va a la derecha y Y al frente.")
    add_table(doc, ["ID", "Línea de colocación"], [
        ("H‑W1", "de (0,0) a (60,0)"), ("H‑W2", "de (0,0) a (0,35)"),
        ("H‑W3", "de (60,0) a (60,35)"), ("H‑W4", "de (0,35) a (60,35); solo dintel y postes"),
        ("H‑P1", "x=25, desde y=13 hasta y=35"), ("H‑P2", "x=25, desde y=0 hasta y=10"),
        ("H‑P3", "y=17, desde x=50 hasta x=60"), ("H‑P4", "x=50, desde y=0 hasta y=17"),
    ], widths=[1.1, 5.6], font_size=8.2)
    add_table(doc, ["Elemento interior", "Medida máxima", "Ubicación recomendada"], [
        ("Encimera de cocina", "24×5×7", "Contra H‑W1, sector x=1–25; deja ventilación al DHT."),
        ("Barra/comedor", "14×6×7", "Paralela a la encimera; paso libre mínimo de 6 cm."),
        ("Sofá / TV", "12×6×6 / 8×1×5", "Sala; piezas opuestas sin tapar el PIR."),
        ("Cama doble", "14×20×4", "Dormitorio, cabecera contra H‑W1; paso lateral mínimo de 4 cm."),
        ("Armario", "4×10×14", "Contra H‑P1 o H‑P4; no bloquear la puerta."),
        ("Ducha / sanitario", "6×8 / 4×6", "Baño; ducha al fondo, sanitario al frente; todo decorativo y seco."),
    ], widths=[1.55, 1.35, 3.9], font_size=8.1)
    add_picture(doc, MODULES_PLAN, 6.75, "Despiece y ocupación de los módulos auxiliares.")
    callout(doc, "Corrección de la bahía", "La huella que cabe en la base es 15×28 cm. El frente transparente puede medir 22×28 cm y sobresalir 7 cm hacia la torre; no debe describirse como una huella de 22×28 cm.")

    doc.add_heading("10. Ubicación de sensores y módulos", 1)
    add_table(doc, ["Elemento", "Ubicación", "Regla de montaje"], [
        ("INMP441", "Frente de torre Jarvis", "Rejilla abierta, lejos del ventilador y relés; 12–15 cm del altavoz."),
        ("Altavoz/MAX98357A", "Parte baja/frontal de Jarvis", "Salida hacia el público; cavidad rígida; half‑duplex."),
        ("WS2812", "Aro bajo/alrededor del micrófono", "330 Ω en datos y 470–1000 µF en 5 V; tierra común."),
        ("DHT11", "Interior ventilado a media altura", "Lejos de lámparas, sol directo, agua y corriente del ventilador."),
        ("LDR", "Exterior bajo alero", "Orientado a luz ambiente y protegido de los LED de la maqueta."),
        ("PIR", "Sobre la entrada", "Campo libre; orientar al recorrido del visitante."),
        ("Humedad de suelo", "Maceta/invernadero", "Solo la sonda toca tierra; comparador y conectores permanecen secos."),
        ("Nivel de agua", "Depósito inferior", "Bucle antigoteo; electrónica más alta y a ≥25 cm."),
        ("LCD1602/ESP32/relés/fusible", "Bahía transparente de servicio", "La pantalla grande disponible va aquí, no en la torre Jarvis; acceso USB, ventilación y nada de agua encima."),
        ("Panel solar", "Techo removible", "Conector polarizado; inclinación demostrativa y cable oculto."),
    ], widths=[1.25, 2.0, 3.5], font_size=8.2)

    doc.add_heading("11. Por qué cada tecnología", 1)
    add_table(doc, ["Tecnología", "Por qué se eligió", "Aplicación real"], [
        ("ESP32‑S3 N16R8", "Wi‑Fi/BLE, 16 MB flash, 8 MB PSRAM y aceleración útil para TinyML.", "Controlador de habitación, gateway o prototipo de producto."),
        ("TinyML", "Reconoce órdenes limitadas con poca memoria y sin nube.", "Comandos locales, alarmas acústicas y mantenimiento predictivo."),
        ("PicoTTS", "Genera frases nuevas; evita grabar miles de MP3.", "Avisos domésticos, accesibilidad y estados hablados."),
        ("INMP441 + I2S", "Audio digital menos sensible al ruido analógico del cableado.", "Intercomunicadores y nodos de voz."),
        ("MQTT", "Mensajes ligeros y desacoplados.", "Integración con Home Assistant, Node‑RED y múltiples habitaciones."),
        ("Relés", "Separan control lógico y carga.", "En una casa real se usarían módulos certificados dentro de un tablero."),
        ("Sensores", "Decisiones basadas en datos, no en temporizadores ciegos.", "Riego eficiente, iluminación y ventilación por demanda."),
        ("Energía solar", "Enseña generación, almacenamiento y regulación.", "Respaldo de sensores; un hogar completo requiere cálculo y equipo certificado."),
    ], widths=[1.25, 2.8, 2.7], font_size=8.1)

    doc.add_heading("12. Diferencia frente a proyectos más simples", 1)
    add_table(doc, ["Proyecto simple típico", "PROJECT DOMUS", "Ventaja demostrable"], [
        ("LED controlado por botón", "Órdenes pasan por un despachador con estado.", "Evita acciones contradictorias."),
        ("Riego por temporizador", "Riego por humedad, validación y corte máximo.", "Menos desperdicio y mayor seguridad."),
        ("Bluetooth dependiente de celular", "Núcleo autónomo; BLE es respaldo.", "Sigue operando sin teléfono."),
        ("Frases MP3 fijas", "Texto dinámico + PicoTTS local.", "Puede decir valores y estados nuevos."),
        ("‘IA’ que solo activa un relé", "Wake word + intención + confianza + confirmación.", "Arquitectura explicable y comprobable."),
        ("Panel solar decorativo", "Ruta panel–cargador–batería–regulador y medición.", "Explica energía con honestidad."),
    ], widths=[2.0, 2.65, 2.1], font_size=8.3)

    doc.add_heading("13. Demostración y exposición", 1)
    doc.add_heading("Secuencia recomendada", 2)
    numbered(doc, [
        "Encender y mostrar que las salidas comienzan apagadas.",
        "Mostrar temperatura y humedad en LCD.",
        "Simular tierra seca y activar riego; detenerlo manualmente.",
        "Mostrar que una orden manual no es anulada por la automatización.",
        "Si la voz ya está validada: decir una frase entrenada, mostrar aro azul, acción y respuesta.",
        "Desconectar Wi‑Fi y repetir una automatización local.",
        "Señalar fusible, canal de cables y separación entre agua y electrónica.",
    ])
    doc.add_heading("Guion corto", 2)
    doc.add_paragraph("“PROJECT DOMUS es una casa inteligente local. Sus sensores ayudan a ahorrar agua y energía; el ESP32 toma decisiones y controla cada salida con reglas de seguridad. Jarvis no es una IA ilimitada: reconoce órdenes domésticas específicas y puede generar una respuesta hablada sin depender de miles de audios. Wi‑Fi amplía el sistema, pero la casa no deja de funcionar cuando internet falla.”")
    doc.add_heading("Plan de respaldo", 2)
    bullets(doc, [
        "Si falla el micrófono: disparar la misma intención con botón o BLE y explicar el flujo.",
        "Si falla el altavoz: mostrar la respuesta en LCD/Monitor Serial.",
        "Si falla Wi‑Fi: continuar; es una demostración de diseño local.",
        "Llevar fuente de 5 V/3 A, cable USB, jumpers, cinta, destornillador, firmware y video corto de respaldo.",
    ])

    doc.add_heading("14. Criterios de aceptación", 1)
    bullets(doc, [
        "Cinco reinicios sin pulsos visibles en relés.",
        "Una orden causa como máximo una conmutación.",
        "La bomba se detiene siempre al límite de seguridad.",
        "Tres demostraciones completas consecutivas sin reinicio.",
        "La casa mantiene funciones básicas sin Wi‑Fi.",
        "Voz habilitada: ≥90 % a 50 cm, ≥80 % a 1 m y cero falsas activaciones en una hora.",
    ])

    doc.add_heading("15. Fuentes de compra consultadas", 1)
    sources = [
        "C&D · MAX98357A: https://sps.cdtechnologia.net/5855-modulo-amplificador-de-audio-i2s-max98357.html",
        "C&D · relé 4 canales L250: https://sps.cdtechnologia.net/2719-867-modulo-rele-5-24v-10a-1-8-canales.html#/609-tipo-4_canales_5v",
        "C&D · relé 8 canales L395: https://sps.cdtechnologia.net/2719-874-modulo-rele-5-24v-10a-1-8-canales.html#/610-tipo-8_canales_5v",
        "C&D · módulo microSD: https://sps.cdtechnologia.net/509-modulo-lector-y-escritor-de-tarjetas-micro-sd-compatible-con-arduino.html",
        "C&D · MT3608 USB‑C: https://sps.cdtechnologia.net/5077-estabilizador-regulador-ascendente-de-voltaje-dc-dc-mt3608-usb-c-2v-24v-a-5v-28v-2a.html",
        "C&D · fuente USB‑C 5 V/3 A con switch L350: https://sps.cdtechnologia.net/2985-1225-fuente-para-raspberry-pi3-pi4.html#/833-valor-5v_3a_usb_c_con_switch",
        "C&D · altavoz 4 Ω/3 W: https://sps.cdtechnologia.net/4094-parlante-4ohm-3w.html",
        "C&D · CN3065: https://sps.cdtechnologia.net/4804-modulo-de-carga-baterias-de-litio-cn3065.html",
        "CONSONANCE · hoja de datos CN3065 (entrada 4.4–6 V, litio 1S): https://files.seeedstudio.com/wiki/Lipo_Rider_Pro/res/DSE-CN3065.pdf",
        "C&D · 18650 EVE: https://test.cdtechnologia.net/baterias/4855-bateria-eve-18650-26v-2550mah-75a.html",
        "C&D · 18650 BAK 2500 mAh L180: https://sps.cdtechnologia.net/5255-bateria-recargable-bak-18650-36v-2500mah-30a.html",
        "C&D · panel solar, variante 5 V/1100 mA L280: https://sps.cdtechnologia.net/4506-panel-solar-3v-55v.html",
        "C&D · portacelda 18650 individual L55: https://sps.cdtechnologia.net/51-baterias",
        "C&D · módulo power-bank 5 V/2.1 A L120: https://sps.cdtechnologia.net/1926-modulo-de-carga-usb-para-baterias-18650-con-pantalla-bms.html",
        "C&D · capacitores 4700 µF L60 y 6800 µF L35: https://sps.cdtechnologia.net/1701-capacitores-electroliticos-de-1000uf-2200uf-3300uf-4700uf-o-10000uf-1-valor-1-unidad.html",
        "C&D · interruptor KCD1-101 L25: https://sps.cdtechnologia.net/1612-interruptor-de-corriente-250v-6a-kcd1-101.html",
        "C&D · portafusible L40: https://sps.cdtechnologia.net/110-fusibles?page=2",
        "C&D · fusible cerámico 3 A L15: https://sps.cdtechnologia.net/4176-fusible-ceramico-01-30a-250v-5x20-mm-1u.html",
        "C&D · BMS 1S L85: https://sps.cdtechnologia.net/51-baterias",
        "Steren Honduras · 18650 2800 mAh L249: https://www.steren.com.hn/bateria-recargable-li-ion-2800-mah-tipo-18650-1.html",
        "Steren Honduras · interruptor SPST 82600 L55: https://www.steren.com.hn/linea-estudiantil/switches-y-relevadores",
    ]
    bullets(doc, sources)
    doc.add_paragraph("Consulta realizada el 1 de septiembre de 2026. Precios, variantes, existencias y entrega deben reconfirmarse con la tienda antes de comprar.")

    path = OUT / "Proyecto_Tecnico_PROJECT_DOMUS_ACTUALIZADO.docx"
    doc.save(path)
    return path


def build_construction():
    doc = Document()
    configure(doc, "Guía de construcción")
    hero = ASSETS / "project_domus_diseno_definitivo.png"
    cover(doc, "Manual de maqueta", "CONSTRUCCIÓN · PROJECT DOMUS", "Medidas, cortes, sensores, cableado y montaje", hero, "Diseño modular definitivo")
    callout(doc, "Diseño confirmado", "La guía ya corresponde a la vivienda modular de un nivel: casa posterior, invernadero izquierdo, entrada cubierta al frente, torre Jarvis y bahía electrónica independiente.")

    doc.add_heading("1. Medidas generales", 1)
    add_table(doc, ["Elemento común", "Medida recomendada", "Tolerancia / nota"], [
        ("Base", "100 × 70 cm", "Plywood 6–9 mm o doble cartón corrugado cruzado."),
        ("Zócalo técnico", "10–12 cm de alto", "Permite depósito, fuente y cables; tapas removibles."),
        ("Canal de cables", "5 cm de ancho", "A lo largo del borde trasero y derecho."),
        ("Bahía electrónica", "huella 15 × 28 cm; panel 22 × 28 cm", "El panel puede sobresalir 7 cm; acceso sin desmontar la casa."),
        ("Torre Jarvis", "15 × 28 × 32 cm", "Frente acústico removible."),
        ("Separación agua/electrónica", "≥25 cm", "La electrónica siempre más alta que el depósito."),
    ], widths=[1.55, 1.7, 3.7])

    doc.add_heading("2. Diseño modular definitivo", 1)
    add_picture(doc, PLAN_V2, 6.75)
    add_table(doc, ["Módulo", "Dimensiones"], [
        ("Invernadero izquierdo", "30 × 45 cm; 25 cm de alto"),
        ("Casa posterior", "60 × 35 cm; muros de 25 cm; techo hasta aprox. 34 cm"),
        ("Torre Jarvis", "15 × 28 × 32 cm"),
        ("Entrada cubierta", "31 × 25 cm más rampa de acceso"),
        ("Bahía de servicio", "huella 15 × 28 cm; panel transparente vertical 22 × 28 cm"),
    ], widths=[2.4, 4.3])

    doc.add_heading("3. Materiales de construcción", 1)
    add_table(doc, ["Categoría", "Material", "Uso"], [
        ("Estructura", "Plywood 6–9 mm o cartón doble corrugado", "Base y paredes portantes."),
        ("Reutilizado", "Cajas limpias, cartón gris, tapas, palitos, malla y envases", "Muros, muebles, marcos, macetas y depósito."),
        ("Transparente", "Acetato de empaque o acrílico 1–2 mm", "Techo del invernadero y ventana de electrónica."),
        ("Unión", "Silicón caliente, cola blanca, cinta de pintor, tornillos pequeños", "Pegado provisional y definitivo."),
        ("Acabado", "Sellador, pintura acrílica, pinceles, lija, marcador blanco", "Color, limpieza visual y etiquetas."),
        ("Cableado", "Borneras/JST, termorretráctil, bridas, velcro", "Módulos desmontables y seguros."),
        ("Paisajismo", "Arena, aserrín teñido, musgo artificial, plantas y grava", "Patio e invernadero; mantener seco."),
    ], widths=[1.2, 2.45, 3.3], font_size=8.2)
    doc.add_paragraph("Para mañana, prioriza estructura limpia y módulos removibles. La pintura y el paisajismo deben aplicarse después de probar que cada cable puede retirarse sin romper la maqueta.")

    doc.add_heading("4. Planos, coordenadas y lista de cortes", 1)
    doc.add_paragraph("Traza primero una cuadrícula de 5 cm. Usa como origen la esquina trasera izquierda: X hacia la derecha, Y hacia el frente. Marca invernadero X2–32/Y10–55; casa X34–94/Y2–37; entrada X34–65/Y39–64; Jarvis X67–82/Y38–66; servicio X83–98/Y38–66 y canal X34–98/Y65–70.")
    add_picture(doc, WALL_PLAN, 6.2, "Plano de elevaciones y aberturas de la casa.")
    doc.add_page_break()
    doc.add_heading("Casa: despiece exacto", 2)
    add_table(doc, ["ID / pieza", "Cant.", "Medida y corte"], [
        ("H‑F1 piso", "1", "60 × 35 cm"),
        ("H‑W1 muro trasero", "1", "60 × 25; ventanas 8×6, 10×7 y ventilación 5×5 según plano"),
        ("H‑W2 lateral izquierdo", "1", "35 × 25; sólido"),
        ("H‑W3 lateral derecho", "1", "35 × 25; ventilación 5×5"),
        ("H‑W4 dintel frontal", "1", "60 × 4; frente abierto"),
        ("H‑C1/C2 postes frontales", "2", "2 × 25; refuerzo de esquinas"),
        ("H‑P1 sala/dormitorio", "1", "22 × 25; puerta 7×20"),
        ("H‑P2 cocina/dormitorio", "1", "10 × 25; sólido"),
        ("H‑P3 frente de baño", "1", "10 × 25; abertura 6×20"),
        ("H‑P4 dormitorio/baño", "1", "17 × 25; sólido"),
        ("H‑R1 techo removible", "1", "64 × 39; voladizo 2 cm por lado"),
    ], widths=[2.15, .65, 3.9], font_size=8.1)
    add_table(doc, ["ID", "Colocación sobre el piso de la casa"], [
        ("H‑W1/W2/W3", "perímetro trasero, izquierdo y derecho: (0,0)–(60,0), (0,0)–(0,35), (60,0)–(60,35)"),
        ("H‑W4", "borde frontal y=35; únicamente dintel y dos postes"),
        ("H‑P1", "x=25; y=13–35"), ("H‑P2", "x=25; y=0–10"),
        ("H‑P3", "y=17; x=50–60"), ("H‑P4", "x=50; y=0–17"),
    ], widths=[1.2, 5.5], font_size=8.1)
    doc.add_heading("Módulos auxiliares", 2)
    add_picture(doc, MODULES_PLAN, 6.75, "Dimensiones y ocupación de invernadero, Jarvis, servicio y acceso.")
    add_table(doc, ["Pieza", "Cantidad", "Medida"], [
        ("Base", "1", "100 × 70 cm"),
        ("Fajas del zócalo", "2 + 2", "100 × 10 cm y 70 × 10 cm"),
        ("Panel frontal de bahía", "1", "22 × 28 cm; huella del gabinete 15 × 28 cm"),
        ("Torre Jarvis · laterales", "2", "28 × 32 cm"),
        ("Torre Jarvis · frente/fondo", "2", "15 × 32 cm"),
        ("Torre Jarvis · tapa/base", "2", "15 × 28 cm"),
        ("Tapas de canal", "varias", "5 cm de ancho"),
    ], widths=[2.65, .8, 3.0])
    doc.add_heading("Invernadero y entrada", 2)
    add_table(doc, ["Pieza", "Cantidad", "Medida"], [
        ("Piso invernadero", "1", "30 × 45 cm"),
        ("Zócalos laterales", "2", "45 × 6 cm"),
        ("Zócalos frontal/trasero", "2", "30 × 6 cm"),
        ("Costillas transparentes", "2", "45 × 18 cm"),
        ("Testeros transparentes", "2", "30 × 25 cm; remate a dos aguas"),
        ("Cubierta transparente", "2", "47 × 20 cm; ajustar al ángulo real"),
        ("Plataforma de entrada", "1", "31 × 25 cm"),
        ("Cubierta de entrada", "1", "31 × 18 cm"),
        ("Postes de entrada", "4", "1 × 1 × 18 cm"),
        ("Rampa", "1", "8 × 24 cm"),
    ], widths=[2.65, .8, 3.0])
    callout(doc, "Antes de cortar", "Haz una plantilla de papel a escala 1:1 para ESP32, relés, LCD, depósito y altavoz. Añade 5 mm de holgura alrededor de conectores y 15 mm donde deba entrar un destornillador.")

    doc.add_heading("5. Orden de construcción", 1)
    numbered(doc, [
        "Dibuja la cuadrícula de 5 cm sobre la base y marca las coordenadas del plano definitivo.",
        "Construye el zócalo técnico, pero deja dos lados removibles con velcro o tornillos.",
        "Presenta en seco la bahía de servicio, depósito, bomba y canales; todavía no pegues.",
        "Construye la torre Jarvis y abre rejillas para micrófono y altavoz antes de pintar.",
        "Corta casa e invernadero. Refuerza esquinas con tiras internas de cartón o listón.",
        "Sella cantos, lija plywood y aplica imprimación. Pinta piezas por separado.",
        "Instala canaletas, borneras y conectores etiquetados.",
        "Monta sensores y actuadores de forma desmontable.",
        "Prueba cada módulo con fuente USB/5 V antes de conectarlo al ESP32.",
        "Integra todo con la alimentación apagada y ejecuta la lista de verificación.",
        "Añade techo removible, acrílicos, vegetación y rótulos al final.",
    ])

    doc.add_heading("6. Ubicación física y perforaciones", 1)
    add_table(doc, ["Módulo", "Hueco / soporte", "Precaución"], [
        ("LCD1602", "Ventana 72 × 25 mm aprox.; medir tu unidad", "Va en el panel de servicio, no en Jarvis; soporte removible."),
        ("PIR", "Orificio 24–26 mm", "No cubrir la lente Fresnel."),
        ("DHT11", "Rejilla 25 × 30 mm", "Aire libre; sin pintura sobre el sensor."),
        ("LDR", "Orificio 5–6 mm", "Crear pequeño visor que bloquee los LED internos."),
        ("INMP441", "Rejilla 8–12 mm", "Membrana hacia el exterior; espuma fina como antiviento."),
        ("Altavoz", "Rejilla según diámetro", "No sellar cono; caja rígida mejora volumen."),
        ("USB ESP32", "Ventana 14 × 8 mm aprox.", "Acceso directo sin retirar la placa."),
        ("Fusible/interruptor", "Ranura según pieza", "Visible y accesible desde el exterior."),
    ], widths=[1.15, 2.75, 2.9], font_size=8.2)

    doc.add_heading("7. Cableado y energía", 1)
    doc.add_heading("Reglas", 2)
    bullets(doc, [
        "Usa una tierra común para señales de 5 V/3.3 V, excepto aislamientos expresamente diseñados.",
        "No alimentes relés, bomba, WS2812 o altavoz desde el pin 3.3 V del ESP32.",
        "Separa cables de micrófono de relés, motor y bomba.",
        "Coloca el capacitor grande cerca de la distribución de 5 V y desacoplos cerca de módulos.",
        "Añade diodo de rueda libre a motores DC si no están detrás de un módulo que ya lo incluya.",
        "Marca +5 V, +3.3 V y GND con colores constantes. Usa rojo, naranja y negro respectivamente.",
        "Todos los cambios de cableado se hacen con la fuente apagada.",
    ])
    doc.add_heading("Distribución recomendada", 2)
    add_table(doc, ["Riel", "Cargas", "Protección"], [
        ("5 V lógica/visual", "ESP32 por USB/5 V, LCD, relés, WS2812", "Fusible 2–3 A; capacitor 1000–2200 µF."),
        ("5 V actuadores", "Bomba, ventilador, MAX98357A", "Idealmente ramal separado y conmutación adecuada."),
        ("3.3 V", "INMP441 y sensores compatibles", "Solo regulador del ESP32; revisar corriente total."),
    ], widths=[1.35, 3.05, 2.4])
    callout(doc, "Límite de exposición", "No conectes 110/120 V de red a la maqueta. La capacidad ‘10 A/250 V’ impresa en un relé no convierte el montaje escolar en una instalación doméstica certificada.", RED)

    doc.add_heading("8. Montaje de Jarvis", 1)
    numbered(doc, [
        "Ubica el INMP441 al frente y el altavoz 12–15 cm más abajo o detrás de un deflector.",
        "Monta el MAX98357A cerca del altavoz para mantener cortos los cables de potencia.",
        "Forma un aro con la tira WS2812 o instala un arco azul debajo del micrófono.",
        "Añade resistencia de 330 Ω en datos y capacitor de 470–1000 µF entre 5 V y GND del WS2812.",
        "Instala un botón físico de silencio y etiqueta ‘MIC OFF’.",
        "Prueba por separado micrófono, síntesis de voz y LED antes de cerrar la torre.",
    ])
    add_table(doc, ["Estado", "Color / animación"], [
        ("En espera", "Azul tenue fijo o pulso lento."),
        ("Escuchando", "Azul intenso giratorio."),
        ("Procesando", "Azul/cian intermitente breve."),
        ("Hablando", "Pulso azul sincronizado de forma aproximada."),
        ("Error / baja confianza", "Rojo breve; ninguna salida cambia."),
        ("Micrófono silenciado", "Ámbar fijo."),
    ], widths=[2.2, 4.55])

    doc.add_heading("9. Calibración", 1)
    numbered(doc, [
        "Humedad de suelo: registra lectura en tierra seca y recién regada; actualiza los dos extremos del firmware.",
        "LDR: registra oscuridad y luz del salón con los LED de la maqueta en ambos estados.",
        "DHT11: compara con otro termómetro; permite estabilización antes de leer.",
        "Nivel de agua: marca mínimo seguro para que la bomba no funcione en seco.",
        "PIR: espera calentamiento inicial y ajusta orientación para evitar activaciones del pasillo.",
        "Voz: captura muestras de varios compañeros y ruido real del aula; no entrenes solamente con una voz.",
    ])

    doc.add_heading("10. Pruebas antes de la exposición", 1)
    add_table(doc, ["Prueba", "Resultado esperado", "Hecho"], [
        ("Continuidad y cortos", "No hay corto entre 5 V y GND.", "☐"),
        ("Fuente sin cargas", "Salida estable dentro de tolerancia.", "☐"),
        ("Arranque ×5", "Todos los relés permanecen apagados.", "☐"),
        ("Cada salida", "Solo cambia el canal ordenado.", "☐"),
        ("Bomba", "Se detiene por orden, humedad o 120 s.", "☐"),
        ("Sensores desconectados", "No activan acciones peligrosas.", "☐"),
        ("Sin Wi‑Fi", "Automatización y control local siguen activos.", "☐"),
        ("Voz, si se habilita", "No se activa a sí misma y rechaza baja confianza.", "☐"),
        ("Ciclo completo ×3", "No hay reinicio, cables sueltos ni fugas.", "☐"),
    ], widths=[1.7, 4.45, .55], font_size=8.3)

    doc.add_heading("11. Presentación física", 1)
    bullets(doc, [
        "Coloca el banner detrás, no delante de la maqueta. El público debe ver sensores y actuadores.",
        "Etiqueta cada zona con nombre grande y cada cable solo en la bahía técnica.",
        "Muestra una ruta de energía con flechas: panel → cargador → batería → regulador → cargas.",
        "Prepara tarjetas pequeñas: ‘local’, ‘seguridad’, ‘ahorro de agua’, ‘voz dinámica’ y ‘Wi‑Fi opcional’.",
        "Deja una tapa transparente sobre relés y ESP32: enseña la ingeniería sin permitir que el público toque.",
        "Usa una bandeja impermeable bajo el depósito y lleva paños absorbentes.",
        "Transporta techo, torre y panel de servicio por separado; conecta con JST/borneras al llegar.",
    ])

    doc.add_heading("Kit de emergencia", 2)
    bullets(doc, [
        "Fuente 5 V/3 A, dos cables USB y extensión eléctrica.",
        "Jumpers, cinta aislante, cinta doble cara, bridas y silicón caliente.",
        "Destornillador, alicate, multímetro y fusibles.",
        "Agua en botella cerrada, jeringa/embudo y paño.",
        "Firmware, computadora y video de respaldo de 30–45 segundos.",
    ])
    doc.add_page_break()
    doc.add_heading("Compras verificadas en Honduras", 1)
    add_table(doc, ["Producto", "Tienda / precio visto", "Decisión"], [
        ("Fuente USB‑C 5 V/3 A con switch", "C&D · L350", "Variante recomendada. USB‑C sin switch L250; micro‑USB L248."),
        ("MAX98357A", "C&D · L130", "Comprar para voz local."),
        ("Altavoz 4 Ω/3 W", "C&D · L90", "Compatible con el amplificador."),
        ("Relé 4 canales 5 V/10 A", "C&D · L250", "Recomendado: junto al relé de 1 canal disponible cubre cinco cargas."),
        ("Relé 8 canales 5 V/10 A", "C&D · L395", "Solo si se prefieren tres salidas de expansión."),
        ("Portafusible + fusible cerámico 3 A", "C&D · L40 + L15", "Formato 5×20 mm; comprar repuestos iguales."),
        ("JST / PCT / cable 22 AWG", "C&D · L45 / L40 / desde L35", "Comprar según número de módulos; confirmar existencias."),
        ("Capacitor 1000 µF (5 unidades)", "C&D · L35", "Suficiente para desacoplo principal de 5 V."),
        ("CN3065", "C&D · L135", "Solo para fase solar 1S."),
        ("18650 EVE 2550 mAh", "C&D · L190", "Es sin protección: requiere protección externa."),
        ("BMS 1S 20 A", "C&D · L85", "Protección obligatoria si la celda no es protegida."),
        ("MT3608 USB‑C", "C&D · L90", "Validar corriente/temperatura; no prometer 2 A continuos."),
        ("Módulo microSD", "C&D · L149", "No hace falta: ya tienes DFPlayer; además declara ≤32 GB."),
        ("INMP441 / 74AHCT125", "Sin oferta local verificada", "Importar o consultar directamente; precio pendiente."),
    ], widths=[2.0, 2.1, 2.6], font_size=8)
    callout(doc, "Relés: decisión final", "Comprar el módulo C&D de 4 canales por L250 y usar además el relé de 1 canal ya disponible. El módulo de 8 canales cuesta L395 y solo conviene si se quieren salidas de expansión.")
    doc.add_paragraph("Consulta web: 31 de agosto de 2026. Existencia, variante y entrega a Choluteca deben confirmarse en carrito o por WhatsApp antes de pagar.")

    path = OUT / "Guia_Construccion_PROJECT_DOMUS_ACTUALIZADO.docx"
    doc.save(path)
    return path


if __name__ == "__main__":
    a = build_technical()
    b = build_construction()
    print(a)
    print(b)
