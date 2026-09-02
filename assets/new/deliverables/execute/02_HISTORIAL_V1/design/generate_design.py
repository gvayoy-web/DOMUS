"""Genera los entregables técnicos y 3D de PROJECT DOMUS.

Modelo en milímetros. No requiere conexión de red. El OBJ se construye con
prismas modulares sencillos para que sea editable en cualquier programa 3D.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, asdict, replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


ROOT = Path(__file__).resolve().parent


@dataclass
class Part:
    name: str
    x: float
    y: float
    z: float
    w: float
    d: float
    h: float
    material: str
    layer: str
    note: str = ""


MATERIALS = {
    "base": (0.12, 0.15, 0.20, 1.0),
    "wood": (0.64, 0.43, 0.24, 1.0),
    "wood_light": (0.84, 0.70, 0.49, 1.0),
    "floor": (0.44, 0.27, 0.13, 1.0),
    "roof": (0.08, 0.10, 0.14, 1.0),
    "glass": (0.35, 0.78, 0.89, 0.24),
    "soil": (0.22, 0.11, 0.05, 1.0),
    "water": (0.08, 0.46, 0.78, 0.65),
    "blue": (0.03, 0.25, 0.63, 1.0),
    "blue_light": (0.08, 0.55, 0.95, 1.0),
    "electronics": (0.05, 0.22, 0.16, 1.0),
    "relay": (0.06, 0.34, 0.72, 1.0),
    "metal": (0.52, 0.58, 0.64, 1.0),
    "red": (0.78, 0.08, 0.08, 1.0),
    "green": (0.10, 0.55, 0.22, 1.0),
    "white": (0.92, 0.93, 0.95, 1.0),
    "solar": (0.02, 0.10, 0.28, 1.0),
}


def p(name, x, y, z, w, d, h, material, layer, note=""):
    return Part(name, x, y, z, w, d, h, material, layer, note)


def build_parts() -> list[Part]:
    t = 3
    parts = [
        p("Base 1000x700", 0, 0, 0, 1000, 700, 9, "base", "base", "Plywood/MDF 9 mm"),
        p("Canal principal de cables", 330, 20, 9, 640, 30, 15, "blue", "systems", "Tapa removible"),
        p("Entrada cubierta", 350, 55, 9, 270, 205, 8, "wood", "ground"),
        p("Rampa de acceso", 350, 15, 9, 95, 40, 5, "wood_light", "ground"),
        p("Piso planta baja", 350, 290, 9, 620, 380, 6, "floor", "ground"),
        # Planta baja: envolvente con frente abierto para exposición.
        p("PB muro posterior", 350, 667, 15, 620, t, 220, "wood_light", "ground"),
        p("PB muro lateral izquierdo", 350, 290, 15, t, 380, 220, "wood_light", "ground"),
        p("PB muro lateral derecho", 967, 290, 15, t, 380, 220, "wood_light", "ground"),
        p("PB frente izquierdo", 350, 290, 15, 70, t, 220, "wood_light", "ground"),
        p("PB frente central", 610, 290, 15, 55, t, 220, "wood_light", "ground"),
        p("PB frente derecho", 910, 290, 15, 60, t, 220, "wood_light", "ground"),
        p("División sala-cocina", 350, 500, 15, 430, t, 160, "wood_light", "ground"),
        p("Barra cocina", 650, 520, 15, 35, 120, 80, "wood", "furniture"),
        p("Mueble cocina", 390, 610, 15, 230, 45, 75, "wood", "furniture"),
        p("Sofá sala", 440, 350, 15, 150, 65, 55, "blue", "furniture"),
        p("Mesa sala", 610, 380, 15, 80, 55, 35, "wood", "furniture"),
        # Entrepiso y segunda planta.
        p("Entrepiso removible", 350, 290, 235, 620, 380, 6, "floor", "upper"),
        p("PA muro posterior", 350, 667, 241, 620, t, 210, "wood_light", "upper"),
        p("PA muro lateral izquierdo", 350, 290, 241, t, 380, 210, "wood_light", "upper"),
        p("PA muro lateral derecho", 967, 290, 241, t, 380, 210, "wood_light", "upper"),
        p("PA frente izquierdo", 350, 290, 241, 80, t, 210, "wood_light", "upper"),
        p("PA frente central", 700, 290, 241, 55, t, 210, "wood_light", "upper"),
        p("PA frente derecho", 920, 290, 241, 50, t, 210, "wood_light", "upper"),
        p("División dormitorio-baño", 760, 290, 241, t, 380, 210, "wood_light", "upper"),
        p("Cama dormitorio", 450, 390, 241, 220, 150, 45, "white", "furniture"),
        p("Ducha", 800, 520, 241, 120, 110, 18, "glass", "furniture"),
        p("Techo removible", 340, 280, 451, 640, 400, 8, "roof", "roof"),
        p("Panel solar único", 545, 390, 460, 240, 140, 8, "solar", "roof", "Panel didáctico; medir antes de prometer autonomía"),
        # Escalera compacta: 12 peldaños.
    ]

    for i in range(12):
        parts.append(p(f"Escalón {i + 1}", 805 + i * 12, 330, 15 + i * 18, 12, 75, 18, "wood", "ground"))

    # Invernadero y riego.
    parts += [
        p("Invernadero base", 25, 220, 9, 290, 450, 8, "wood", "greenhouse"),
        p("Cama de cultivo", 60, 285, 17, 220, 310, 55, "soil", "greenhouse"),
        p("Invernadero pared izquierda", 25, 220, 17, 3, 450, 225, "glass", "greenhouse"),
        p("Invernadero pared derecha", 312, 220, 17, 3, 450, 225, "glass", "greenhouse"),
        p("Invernadero frente", 25, 220, 17, 290, 3, 225, "glass", "greenhouse"),
        p("Invernadero fondo", 25, 667, 17, 290, 3, 225, "glass", "greenhouse"),
        p("Cubierta invernadero A", 25, 220, 242, 145, 450, 3, "glass", "greenhouse"),
        p("Cubierta invernadero B", 170, 220, 242, 145, 450, 3, "glass", "greenhouse"),
        p("Depósito de agua", 55, 90, 9, 110, 95, 120, "water", "systems"),
        p("Mini bomba", 180, 125, 9, 50, 35, 35, "blue", "systems"),
        p("Tubería principal", 135, 175, 45, 155, 12, 12, "blue_light", "systems"),
        p("Sensor humedad suelo", 155, 420, 72, 12, 12, 85, "metal", "sensors"),
        p("Sensor nivel", 95, 105, 65, 8, 8, 85, "metal", "sensors"),
    ]

    # Torre Jarvis completamente local.
    parts += [
        p("Torre Jarvis cuerpo", 650, 40, 9, 140, 220, 320, "roof", "jarvis"),
        p("Torre panel azul izquierdo", 654, 36, 80, 35, 5, 205, "blue", "jarvis"),
        p("Torre panel azul derecho", 751, 36, 80, 35, 5, 205, "blue", "jarvis"),
        p("Altavoz frontal", 690, 35, 175, 60, 6, 60, "metal", "jarvis"),
        p("LCD estado", 675, 34, 95, 90, 6, 45, "blue_light", "jarvis"),
        p("Botón MIC OFF", 705, 30, 45, 30, 12, 30, "red", "jarvis"),
        p("INMP441", 715, 34, 280, 10, 6, 8, "electronics", "sensors"),
    ]
    # Aro azul como 12 pequeños módulos alrededor del micrófono.
    for i in range(12):
        angle = 2 * math.pi * i / 12
        parts.append(
            p(
                f"LED aro {i + 1}",
                715 + math.cos(angle) * 38 - 4,
                31,
                280 + math.sin(angle) * 38 - 4,
                8,
                5,
                8,
                "blue_light",
                "jarvis",
            )
        )

    # Bahía electrónica aislada del agua.
    parts += [
        p("Bahía técnica base", 810, 40, 9, 160, 220, 8, "metal", "service"),
        p("Bahía técnica fondo", 810, 255, 17, 160, 3, 280, "wood", "service"),
        p("Bahía lateral izquierda", 810, 40, 17, 3, 220, 280, "glass", "service"),
        p("Bahía lateral derecha", 967, 40, 17, 3, 220, 280, "glass", "service"),
        p("Bahía frente removible", 810, 40, 17, 160, 3, 280, "glass", "service"),
        p("ESP32-S3 N16R8", 835, 195, 55, 60, 35, 85, "electronics", "electronics"),
        p("Relé bomba", 910, 195, 55, 40, 35, 45, "relay", "electronics"),
        p("Relé 4 canales", 835, 125, 55, 115, 45, 55, "relay", "electronics"),
        p("Fusible 3A", 835, 82, 55, 45, 25, 25, "red", "electronics"),
        p("Barra 5V/GND", 895, 82, 55, 55, 25, 25, "metal", "electronics"),
        p("LCD1602 técnico", 835, 38, 190, 110, 6, 40, "blue_light", "service"),
        p("Interruptor general", 900, 37, 245, 30, 8, 30, "red", "service"),
        p("DHT11 ventilado", 620, 655, 145, 25, 15, 35, "white", "sensors"),
        p("LDR bajo alero", 940, 282, 185, 18, 12, 18, "green", "sensors"),
        p("PIR entrada", 575, 260, 65, 30, 18, 30, "white", "sensors"),
    ]
    return parts


def box_vertices(part: Part):
    x, y, z, w, d, h = part.x, part.y, part.z, part.w, part.d, part.h
    return [
        (x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z),
        (x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h),
    ]


FACES = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7)]


def write_obj(parts: list[Part]) -> None:
    obj = ["mtllib project_domus.mtl", "# PROJECT DOMUS two-storey offline model"]
    index = 1
    for part in parts:
        safe = "_".join(part.name.replace("/", "-").split())
        obj += [f"o {safe}", f"usemtl {part.material}"]
        for vertex in box_vertices(part):
            obj.append("v %.3f %.3f %.3f" % vertex)
        for face in FACES:
            obj.append("f " + " ".join(str(index + i) for i in face))
        index += 8
    (ROOT / "project_domus.obj").write_text("\n".join(obj) + "\n", encoding="utf-8")

    mtl = []
    for name, rgba in MATERIALS.items():
        r, g, b, a = rgba
        mtl += [f"newmtl {name}", f"Kd {r:.3f} {g:.3f} {b:.3f}", f"d {a:.3f}", "illum 2", ""]
    (ROOT / "project_domus.mtl").write_text("\n".join(mtl), encoding="utf-8")


def draw_dimension(svg, x1, y1, x2, y2, text, offset=0, vertical=False):
    if vertical:
        x = x1 + offset
        svg.append(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" class="dim"/>')
        svg.append(f'<line x1="{x-8}" y1="{y1}" x2="{x+8}" y2="{y1}" class="dim"/>')
        svg.append(f'<line x1="{x-8}" y1="{y2}" x2="{x+8}" y2="{y2}" class="dim"/>')
        svg.append(f'<text x="{x-12}" y="{(y1+y2)/2}" class="dt" transform="rotate(-90 {x-12} {(y1+y2)/2})">{text}</text>')
    else:
        y = y1 + offset
        svg.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" class="dim"/>')
        svg.append(f'<line x1="{x1}" y1="{y-8}" x2="{x1}" y2="{y+8}" class="dim"/>')
        svg.append(f'<line x1="{x2}" y1="{y-8}" x2="{x2}" y2="{y+8}" class="dim"/>')
        svg.append(f'<text x="{(x1+x2)/2}" y="{y-7}" class="dt">{text}</text>')


def write_svg() -> None:
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1120" viewBox="0 0 1600 1120">',
        '<style>text{font-family:Arial,sans-serif;fill:#102a56}.title{font-size:38px;font-weight:bold}.sub{font-size:18px;fill:#53657e}.h{font-size:20px;font-weight:bold}.lbl{font-size:14px}.small{font-size:12px}.outline{fill:none;stroke:#14233a;stroke-width:3}.wall{fill:#e8d8bd;stroke:#14233a;stroke-width:2}.module{fill:#d8e7f7;stroke:#205ec8;stroke-width:2}.greenhouse{fill:#dff4ea;stroke:#1f7a4d;stroke-width:2}.service{fill:#e4e8ed;stroke:#14233a;stroke-width:2}.jarvis{fill:#dce8ff;stroke:#123d8d;stroke-width:2}.dim{stroke:#26364a;stroke-width:1.5;marker-start:url(#a);marker-end:url(#a)}.dt{font-size:13px;text-anchor:middle;fill:#26364a}.cut{stroke:#cf2d2d;stroke-width:1.5;stroke-dasharray:6 4;fill:none}.note{font-size:13px;fill:#8a2a2a}.room{font-size:16px;font-weight:bold;text-anchor:middle}</style>',
        '<defs><marker id="a" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto"><path d="M0,3 L6,0 L6,6 Z" fill="#26364a"/></marker></defs>',
        '<rect width="1600" height="1120" fill="white"/>',
        '<text x="60" y="60" class="title">PROJECT DOMUS · PLANO TÉCNICO ACOTADO</text>',
        '<text x="60" y="92" class="sub">Maqueta de dos pisos · sistema 100 % local · cotas en milímetros · escala gráfica 1:10</text>',
    ]

    # Planta general, escala 0.72.
    ox, oy, sc = 80, 190, 0.72
    def rect(x, y, w, h, cls, label=""):
        sx, sy, sw, sh = ox + x * sc, oy + (700 - y - h) * sc, w * sc, h * sc
        svg.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" class="{cls}"/>')
        if label:
            svg.append(f'<text x="{sx+sw/2}" y="{sy+sh/2}" class="room">{label}</text>')
        return sx, sy, sw, sh

    svg.append('<text x="80" y="155" class="h">A · PLANTA GENERAL / PLANTA BAJA</text>')
    rect(0, 0, 1000, 700, "outline")
    rect(25, 220, 290, 450, "greenhouse", "INVERNADERO")
    rect(350, 290, 620, 380, "wall", "CASA · PB")
    rect(350, 55, 270, 205, "module", "ENTRADA")
    rect(650, 40, 140, 220, "jarvis", "JARVIS")
    rect(810, 40, 160, 220, "service", "SERVICIO")
    rect(55, 90, 110, 95, "module", "DEPÓSITO")
    # Rooms PB.
    svg.append(f'<line x1="{ox+350*sc}" y1="{oy+(700-500)*sc}" x2="{ox+780*sc}" y2="{oy+(700-500)*sc}" class="outline"/>')
    svg.append(f'<text x="{ox+570*sc}" y="{oy+(700-600)*sc}" class="lbl" text-anchor="middle">COCINA + BARRA</text>')
    svg.append(f'<text x="{ox+560*sc}" y="{oy+(700-390)*sc}" class="lbl" text-anchor="middle">SALA / ESCALERA</text>')
    draw_dimension(svg, ox, oy + 700 * sc, ox + 1000 * sc, oy + 700 * sc, "1000", 30)
    draw_dimension(svg, ox, oy, ox, oy + 700 * sc, "700", -35, True)
    draw_dimension(svg, ox + 350 * sc, oy + (700-290) * sc, ox + 970 * sc, oy + (700-290) * sc, "620", -18)
    draw_dimension(svg, ox + 25 * sc, oy + (700-220) * sc, ox + 315 * sc, oy + (700-220) * sc, "290", -18)

    # Segunda planta.
    x2, y2, s2 = 900, 205, 0.9
    svg.append('<text x="900" y="155" class="h">B · SEGUNDA PLANTA</text>')
    svg.append(f'<rect x="{x2}" y="{y2}" width="{620*s2}" height="{380*s2}" class="wall"/>')
    split = x2 + 410 * s2
    svg.append(f'<line x1="{split}" y1="{y2}" x2="{split}" y2="{y2+380*s2}" class="outline"/>')
    svg.append(f'<text x="{x2+205*s2}" y="{y2+190*s2}" class="room">DORMITORIO</text>')
    svg.append(f'<text x="{split+105*s2}" y="{y2+190*s2}" class="room">BAÑO / DUCHA</text>')
    svg.append(f'<rect x="{x2+55*s2}" y="{y2+120*s2}" width="{220*s2}" height="{150*s2}" class="module"/>')
    svg.append(f'<rect x="{split+35*s2}" y="{y2+210*s2}" width="{120*s2}" height="{110*s2}" class="greenhouse"/>')
    draw_dimension(svg, x2, y2 + 380 * s2, x2 + 620 * s2, y2 + 380 * s2, "620", 28)
    draw_dimension(svg, x2, y2, x2, y2 + 380 * s2, "380", -28, True)
    draw_dimension(svg, x2, y2, split, y2, "410 dormitorio", -20)
    draw_dimension(svg, split, y2, x2 + 620 * s2, y2, "210 baño", -20)

    # Elevación frontal.
    ex, ey, esc = 80, 1040, 0.52
    svg.append('<text x="80" y="770" class="h">C · ELEVACIÓN FRONTAL</text>')
    svg.append(f'<rect x="{ex}" y="{ey}" width="{1000*esc}" height="{9*esc}" class="outline"/>')
    # greenhouse, house, Jarvis, service silhouettes
    svg.append(f'<rect x="{ex+25*esc}" y="{ey-225*esc}" width="{290*esc}" height="{225*esc}" class="greenhouse"/>')
    svg.append(f'<rect x="{ex+350*esc}" y="{ey-440*esc}" width="{620*esc}" height="{440*esc}" class="wall"/>')
    svg.append(f'<line x1="{ex+350*esc}" y1="{ey-220*esc}" x2="{ex+970*esc}" y2="{ey-220*esc}" class="outline"/>')
    svg.append(f'<rect x="{ex+650*esc}" y="{ey-320*esc}" width="{140*esc}" height="{320*esc}" class="jarvis"/>')
    svg.append(f'<rect x="{ex+810*esc}" y="{ey-280*esc}" width="{160*esc}" height="{280*esc}" class="service"/>')
    svg.append(f'<rect x="{ex+545*esc}" y="{ey-460*esc}" width="{240*esc}" height="{10*esc}" fill="#08245f"/>')
    draw_dimension(svg, ex + 350 * esc, ey, ex + 350 * esc, ey - 220 * esc, "220 PB", -25, True)
    draw_dimension(svg, ex + 350 * esc, ey - 220 * esc, ex + 350 * esc, ey - 430 * esc, "210 PA", -25, True)
    draw_dimension(svg, ex, ey, ex, ey - 460 * esc, "≈460 total", -45, True)

    # Technical notes.
    nx = 880
    svg += [
        f'<text x="{nx}" y="765" class="h">D · COTAS Y CONSTRUCCIÓN</text>',
        f'<text x="{nx}" y="800" class="lbl">Base: 1000 × 700 × 9 · casa: 620 × 380 · frente abierto para exposición</text>',
        f'<text x="{nx}" y="828" class="lbl">PB: 220 de altura · PA: 210 · paredes/entrepiso: plywood 3</text>',
        f'<text x="{nx}" y="856" class="lbl">Invernadero: 290 × 450 × 225 · acrílico/acetato 1–2</text>',
        f'<text x="{nx}" y="884" class="lbl">Jarvis: 140 × 220 × 320 · servicio: 160 × 220 × 280</text>',
        f'<text x="{nx}" y="912" class="lbl">Canal técnico: 30 de ancho · electrónica elevada y separada del agua</text>',
        f'<text x="{nx}" y="952" class="h">Arquitectura local</text>',
        f'<text x="{nx}" y="982" class="lbl">ESP32-S3 N16R8 · LCD1602 · botones · sensores · 5 relés · Jarvis local</text>',
        f'<text x="{nx}" y="1010" class="note">SIN Bluetooth · SIN Wi-Fi · SIN teléfono · SIN nube · solo 5 V DC</text>',
        f'<text x="{nx}" y="1050" class="small">Tolerancia inicial de corte: ±0.5 mm. Medir espesor real del material antes de generar pestañas.</text>',
        '<text x="60" y="1090" class="small">PROJECT DOMUS · revisión offline 1.0 · plano conceptual de fabricación sujeto a verificación física de componentes</text>',
        '</svg>',
    ]
    (ROOT / "plano_tecnico_domus.svg").write_text("\n".join(svg), encoding="utf-8")


def write_parts_csv(parts: list[Part]) -> None:
    with (ROOT / "piezas_modelo.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(parts[0]).keys()))
        writer.writeheader()
        for part in parts:
            writer.writerow(asdict(part))


def render_one(parts: list[Part], filename: str, title: str, elev: float, azim: float) -> None:
    fig = plt.figure(figsize=(16, 10), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    ordered = sorted(parts, key=lambda item: item.material == "glass")
    for part in ordered:
        vertices = box_vertices(part)
        faces = [[vertices[i] for i in face] for face in FACES]
        rgba = MATERIALS[part.material]
        poly = Poly3DCollection(faces, facecolors=[rgba], edgecolors=(0.08, 0.12, 0.18, 0.55), linewidths=0.25)
        ax.add_collection3d(poly)
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 700)
    ax.set_zlim(0, 520)
    ax.set_box_aspect((1000, 700, 520))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=18, pad=18)
    fig.patch.set_facecolor("#f4f6f8")
    ax.set_facecolor("#f4f6f8")
    plt.tight_layout()
    fig.savefig(ROOT / filename, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def render_png(parts: list[Part]) -> None:
    render_one(
        parts,
        "project_domus_render.png",
        "PROJECT DOMUS · modelo 3D montado · dos pisos · sistema offline",
        28,
        -58,
    )
    cutaway = [part for part in parts if part.layer != "roof"]
    render_one(
        cutaway,
        "project_domus_cutaway.png",
        "PROJECT DOMUS · vista sin techo para inspección interior",
        31,
        -112,
    )
    exploded = []
    for part in parts:
        dz = 0
        if part.layer == "upper":
            dz = 180
        elif part.layer == "roof":
            dz = 360
        exploded.append(replace(part, z=part.z + dz))
    render_one(
        exploded,
        "project_domus_exploded.png",
        "PROJECT DOMUS · vista 3D explotada por niveles",
        25,
        -58,
    )


def write_viewer(parts: list[Part]) -> None:
    data = json.dumps([asdict(part) for part in parts], ensure_ascii=False)
    colors = json.dumps({key: value[:3] for key, value in MATERIALS.items()})
    html = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PROJECT DOMUS · modelo 3D offline</title>
<style>
:root{{color-scheme:dark;background:#0c111b;color:#e8edf7;font-family:system-ui,sans-serif}}body{{margin:0;display:grid;grid-template-columns:270px 1fr;min-height:100vh}}aside{{padding:18px;background:#121a28}}h1{{font-size:20px;margin:0 0 8px}}p{{color:#9eacc2;font-size:13px}}label{{display:block;margin:9px 0}}button{{padding:9px 12px;background:#1f5fd1;color:white;border:0;border-radius:7px;cursor:pointer}}input[type=range]{{width:100%}}canvas{{width:100%;height:100vh;display:block;background:radial-gradient(circle at 50% 40%,#26354d,#080c13 72%)}}.layers{{display:grid;grid-template-columns:1fr 1fr;font-size:12px}}.badge{{display:inline-block;padding:4px 8px;background:#173a75;border-radius:99px;font-size:12px}}@media(max-width:760px){{body{{grid-template-columns:1fr}}canvas{{height:70vh}}}}
</style></head><body><aside><h1>PROJECT DOMUS</h1><span class="badge">100 % offline</span><p>Arrastra sobre el modelo para girarlo. Usa la rueda para acercar. El visor no realiza conexiones de red.</p>
<label>Rotación <input id="rot" type="range" min="-180" max="180" value="-35"></label>
<label>Elevación <input id="elev" type="range" min="10" max="70" value="30"></label>
<label>Zoom <input id="zoom" type="range" min="0.45" max="1.4" step="0.01" value="0.78"></label>
<button id="reset">Restablecer vista</button><h2>Capas</h2><div id="layers" class="layers"></div>
<p>Base 1000 × 700 mm<br>Casa 620 × 380 mm<br>PB 220 mm · PA 210 mm<br>Jarvis y servicio removibles</p></aside><canvas id="c"></canvas>
<script>
const parts={data}; const colors={colors}; const canvas=document.getElementById('c'),ctx=canvas.getContext('2d');
const layerNames=[...new Set(parts.map(p=>p.layer))], visible=Object.fromEntries(layerNames.map(x=>[x,true]));
const layerBox=document.getElementById('layers'); layerNames.forEach(layer=>{{const l=document.createElement('label');const i=document.createElement('input');i.type='checkbox';i.checked=true;i.onchange=()=>{{visible[layer]=i.checked;draw()}};l.append(i,document.createTextNode(' '+layer));layerBox.append(l)}});
let rot=-35,elev=30,zoom=.78,drag=false,lastX=0,lastY=0;
function size(){{const d=devicePixelRatio||1;canvas.width=canvas.clientWidth*d;canvas.height=canvas.clientHeight*d;ctx.setTransform(d,0,0,d,0,0);draw()}}
function project(v){{let a=rot*Math.PI/180,e=elev*Math.PI/180,x=v[0]-500,y=v[1]-350,z=v[2]-180;let xr=x*Math.cos(a)-y*Math.sin(a),yr=x*Math.sin(a)+y*Math.cos(a);let yy=yr*Math.sin(e)-z*Math.cos(e),depth=yr*Math.cos(e)+z*Math.sin(e);let s=Math.min(canvas.clientWidth/1150,canvas.clientHeight/780)*zoom;return [canvas.clientWidth/2+xr*s,canvas.clientHeight/2+yy*s,depth]}}
const faces=[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[4,0,3,7]];
function verts(p){{let x=p.x,y=p.y,z=p.z,w=p.w,d=p.d,h=p.h;return [[x,y,z],[x+w,y,z],[x+w,y+d,z],[x,y+d,z],[x,y,z+h],[x+w,y,z+h],[x+w,y+d,z+h],[x,y+d,z+h]]}}
function draw(){{ctx.clearRect(0,0,canvas.clientWidth,canvas.clientHeight);let polys=[];parts.filter(p=>visible[p.layer]).forEach(p=>{{let vv=verts(p).map(project);faces.forEach((f,fi)=>{{let pts=f.map(i=>vv[i]);polys.push({{pts,depth:pts.reduce((s,q)=>s+q[2],0)/4,p,fi}})}})}});polys.sort((a,b)=>a.depth-b.depth);polys.forEach(o=>{{let c=colors[o.p.material]||[.5,.5,.5],shade=.62+o.fi*.045;ctx.beginPath();o.pts.forEach((q,i)=>i?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]));ctx.closePath();ctx.fillStyle=`rgba(${{c.map(v=>Math.round(v*255*shade)).join(',')}},${{o.p.material==='glass'?.22:.96}})`;ctx.fill();ctx.strokeStyle='rgba(5,12,24,.32)';ctx.lineWidth=.55;ctx.stroke()}})}}
document.getElementById('rot').oninput=e=>{{rot=+e.target.value;draw()}};
document.getElementById('elev').oninput=e=>{{elev=+e.target.value;draw()}};
document.getElementById('zoom').oninput=e=>{{zoom=+e.target.value;draw()}};
canvas.onpointerdown=e=>{{drag=true;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture(e.pointerId)}};canvas.onpointermove=e=>{{if(!drag)return;rot+=(e.clientX-lastX)*.4;elev=Math.max(10,Math.min(70,elev-(e.clientY-lastY)*.25));lastX=e.clientX;lastY=e.clientY;document.getElementById('rot').value=rot;document.getElementById('elev').value=elev;draw()}};canvas.onpointerup=()=>drag=false;canvas.onwheel=e=>{{e.preventDefault();zoom=Math.max(.45,Math.min(1.4,zoom-e.deltaY*.0008));document.getElementById('zoom').value=zoom;draw()}};
document.getElementById('reset').onclick=()=>{{rot=-35;elev=30;zoom=.78;document.getElementById('rot').value=rot;document.getElementById('elev').value=elev;document.getElementById('zoom').value=zoom;draw()}};addEventListener('resize',size);size();
</script></body></html>'''
    (ROOT / "modelo_3d_interactivo.html").write_text(html, encoding="utf-8")


def main() -> None:
    parts = build_parts()
    write_obj(parts)
    write_svg()
    write_parts_csv(parts)
    render_png(parts)
    write_viewer(parts)
    print(f"Generados {len(parts)} elementos del modelo en {ROOT}")


if __name__ == "__main__":
    main()
