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
    rx: float = 0
    ry: float = 0
    rz: float = 0


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


def p(name, x, y, z, w, d, h, material, layer, note="", rx=0, ry=0, rz=0):
    return Part(name, x, y, z, w, d, h, material, layer, note, rx, ry, rz)


def build_parts() -> list[Part]:
    t = 3
    parts = [
        # Base y frente de presentación.
        p("Base negra 1000x650", 0, 0, 0, 1000, 650, 12, "base", "base", "MDF 12 mm pintado negro"),
        p("Frente rotulado PROJECT DOMUS", 0, 0, 12, 1000, 22, 75, "roof", "base", "Letras de vinilo o acrílico"),
        p("Canal técnico oculto", 285, 28, 12, 690, 28, 16, "blue", "systems", "Canaleta con tapa removible"),

        # Vivienda de UNA sola planta, abierta al frente como en la referencia.
        p("Piso vivienda", 300, 300, 12, 430, 325, 7, "floor", "house", "Plywood 3 mm sobre bastidor"),
        p("Muro posterior vivienda", 300, 622, 19, 430, t, 225, "wood_light", "house"),
        p("Muro lateral izquierdo", 300, 300, 19, t, 325, 225, "wood_light", "house"),
        p("Muro lateral derecho", 727, 300, 19, t, 325, 225, "wood_light", "house"),
        p("Techo plano removible", 292, 292, 244, 446, 341, 10, "roof", "roof", "Se retira para mantenimiento"),
        p("Alero frontal", 285, 280, 238, 460, 22, 14, "wood", "roof"),

        # Cocina y sala integradas, lado izquierdo.
        p("Mueble bajo cocina", 325, 572, 19, 178, 42, 68, "wood", "furniture"),
        p("Encimera cocina", 322, 568, 87, 184, 48, 7, "wood_light", "furniture"),
        p("Gabinete alto cocina", 325, 594, 130, 130, 24, 72, "wood", "furniture"),
        p("Refrigerador", 515, 548, 19, 48, 66, 138, "metal", "furniture"),
        p("Isla cocina", 405, 465, 19, 118, 48, 70, "wood", "furniture"),
        p("Cubierta isla", 400, 460, 89, 128, 58, 6, "wood_light", "furniture"),
        p("Sofá sala", 330, 350, 19, 122, 55, 52, "blue", "furniture"),
        p("Mesa sala", 462, 370, 19, 70, 48, 31, "wood", "furniture"),

        # Dormitorio central-derecho y baño transparente a la derecha.
        p("Cama base", 545, 405, 19, 118, 178, 37, "wood", "furniture"),
        p("Colchón", 550, 410, 56, 108, 168, 24, "white", "furniture"),
        p("Cabecero", 542, 567, 19, 124, 10, 86, "wood", "furniture"),
        p("Mesa de noche", 675, 520, 19, 38, 38, 42, "wood", "furniture"),
        p("Mampara baño", 680, 305, 19, 3, 290, 190, "glass", "bath"),
        p("Ducha piso", 688, 500, 19, 34, 94, 8, "glass", "bath"),
        p("Lavamanos", 689, 430, 19, 32, 48, 62, "white", "bath"),
        p("Inodoro", 690, 340, 19, 30, 52, 43, "white", "bath"),

        # Dos paneles solares visibles sobre el techo.
        p("Panel solar izquierdo", 355, 380, 255, 145, 105, 7, "solar", "solar", "Panel didáctico 5 V"),
        p("Panel solar derecho", 535, 380, 255, 145, 105, 7, "solar", "solar", "Panel didáctico 5 V"),

        # Entrada, porche y jardín frontal.
        p("Plataforma porche", 340, 72, 12, 250, 195, 8, "floor", "porch"),
        p("Cubierta porche", 332, 62, 154, 266, 210, 9, "roof", "porch"),
        p("Poste porche izquierdo", 345, 75, 20, 8, 8, 134, "wood", "porch"),
        p("Poste porche derecho", 575, 75, 20, 8, 8, 134, "wood", "porch"),
        p("Pasarela", 440, 22, 12, 58, 110, 6, "wood_light", "porch"),
        p("Jardinera izquierda", 360, 92, 20, 38, 135, 26, "soil", "landscape"),
        p("Jardinera derecha", 530, 92, 20, 38, 135, 26, "soil", "landscape"),
        p("PIR entrada", 605, 235, 60, 28, 15, 28, "white", "sensors", "Detección local de presencia"),

        # Depósito y bombeo al extremo izquierdo, lejos de la electrónica.
        p("Depósito de agua", 25, 65, 12, 92, 92, 100, "water", "water"),
        p("Mini bomba 5V", 130, 95, 12, 48, 34, 31, "blue", "water"),
        p("Tubería a invernadero", 105, 170, 40, 150, 10, 10, "blue_light", "water"),
        p("Sensor nivel depósito", 68, 80, 50, 7, 7, 74, "metal", "sensors"),
    ]

    # Invernadero frontal-izquierdo de estructura visible y cubierta transparente.
    parts += [
        p("Base invernadero", 25, 230, 12, 250, 350, 7, "wood", "greenhouse"),
        p("Bancal izquierdo", 48, 265, 19, 76, 280, 42, "soil", "greenhouse"),
        p("Bancal derecho", 155, 265, 19, 76, 280, 42, "soil", "greenhouse"),
        p("Panel transparente izquierdo", 25, 230, 19, 3, 350, 165, "glass", "greenhouse"),
        p("Panel transparente derecho", 272, 230, 19, 3, 350, 165, "glass", "greenhouse"),
        p("Panel transparente posterior", 25, 577, 19, 250, 3, 165, "glass", "greenhouse"),
        p("Cubierta inclinada izquierda", 26, 230, 176, 134, 350, 3, "glass", "greenhouse", ry=-22),
        p("Cubierta inclinada derecha", 140, 230, 176, 134, 350, 3, "glass", "greenhouse", ry=22),
        p("Viga cumbrera", 146, 230, 225, 8, 350, 8, "metal", "greenhouse"),
    ]
    for x in (25, 150, 272):
        for y in (230, 577):
            parts.append(p(f"Poste invernadero {x}-{y}", x, y, 19, 7, 7, 170, "metal", "greenhouse"))
    for x in (48, 88, 172, 212):
        parts.append(p(f"Planta {x}", x, 330, 61, 10, 10, 58, "green", "plants"))
    parts += [
        p("Sensor humedad suelo", 105, 410, 56, 8, 8, 70, "metal", "sensors"),
        p("Línea de riego izquierda", 84, 270, 70, 7, 270, 7, "blue_light", "water"),
        p("Línea de riego derecha", 190, 270, 70, 7, 270, 7, "blue_light", "water"),
    ]

    # Torre Jarvis, separada de la casa y completamente local.
    parts += [
        p("Torre Jarvis cuerpo", 750, 245, 12, 105, 118, 290, "roof", "jarvis"),
        p("Panel azul central", 766, 239, 55, 73, 7, 220, "blue", "jarvis"),
        p("Pantalla de estado", 773, 236, 82, 60, 7, 32, "blue_light", "jarvis"),
        p("Botón físico MIC OFF", 790, 233, 38, 25, 12, 25, "red", "jarvis", "Corte físico del micrófono"),
        p("Micrófono INMP441", 799, 235, 222, 9, 6, 9, "electronics", "sensors"),
        p("Altavoz local", 784, 235, 160, 37, 7, 37, "metal", "jarvis"),
    ]
    for i in range(16):
        angle = 2 * math.pi * i / 16
        parts.append(p(f"LED aro {i + 1}", 802 + math.cos(angle) * 36 - 3, 232, 225 + math.sin(angle) * 36 - 3, 7, 7, 7, "blue_light", "jarvis"))

    # Gabinete electrónico transparente, último módulo a la derecha.
    parts += [
        p("Gabinete técnico base", 870, 235, 12, 110, 150, 7, "metal", "electronics"),
        p("Gabinete fondo", 870, 382, 19, 110, 3, 250, "wood", "electronics"),
        p("Gabinete lateral izquierdo", 870, 235, 19, 3, 150, 250, "glass", "electronics"),
        p("Gabinete lateral derecho", 977, 235, 19, 3, 150, 250, "glass", "electronics"),
        p("Gabinete frontal removible", 870, 235, 19, 110, 3, 250, "glass", "electronics"),
        p("ESP32-S3 N16R8", 887, 335, 55, 43, 23, 72, "electronics", "boards"),
        p("Módulo relés 4 canales", 937, 330, 55, 30, 30, 105, "relay", "boards"),
        p("Fusible 3A", 887, 292, 55, 30, 18, 22, "red", "boards"),
        p("Distribuidor 5V-GND", 927, 292, 55, 40, 18, 22, "metal", "boards"),
        p("Regleta de terminales", 887, 252, 55, 80, 18, 20, "blue", "boards"),
        p("Interruptor general", 944, 229, 222, 22, 12, 26, "red", "electronics"),
    ]
    # Sensores de ambiente colocados en la vivienda.
    parts += [
        p("DHT11 interior", 570, 610, 145, 20, 12, 28, "white", "sensors"),
        p("LDR bajo alero", 704, 286, 208, 16, 10, 16, "green", "sensors"),
        p("LED sala", 425, 520, 220, 18, 18, 6, "blue_light", "lights"),
        p("LED dormitorio", 615, 520, 220, 18, 18, 6, "blue_light", "lights"),
        p("LED invernadero", 142, 420, 218, 18, 18, 6, "blue_light", "lights"),
    ]
    return parts


def box_vertices(part: Part):
    x, y, z, w, d, h = part.x, part.y, part.z, part.w, part.d, part.h
    vertices = [
        (x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z),
        (x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h),
    ]
    if not (part.rx or part.ry or part.rz):
        return vertices
    cx, cy, cz = x + w / 2, y + d / 2, z + h / 2
    rx, ry, rz = map(math.radians, (part.rx, part.ry, part.rz))
    transformed = []
    for vx, vy, vz in vertices:
        vx, vy, vz = vx - cx, vy - cy, vz - cz
        vy, vz = vy * math.cos(rx) - vz * math.sin(rx), vy * math.sin(rx) + vz * math.cos(rx)
        vx, vz = vx * math.cos(ry) + vz * math.sin(ry), -vx * math.sin(ry) + vz * math.cos(ry)
        vx, vy = vx * math.cos(rz) - vy * math.sin(rz), vx * math.sin(rz) + vy * math.cos(rz)
        transformed.append((vx + cx, vy + cy, vz + cz))
    return transformed


FACES = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7)]


def write_obj(parts: list[Part]) -> None:
    obj = ["mtllib project_domus.mtl", "# PROJECT DOMUS one-storey cutaway offline model"]
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
        '<style>text{font-family:Arial,sans-serif;fill:#10233f}.title{font-size:36px;font-weight:bold}.sub{font-size:18px;fill:#52657c}.h{font-size:20px;font-weight:bold}.lbl{font-size:14px}.small{font-size:12px}.outline{fill:none;stroke:#14233a;stroke-width:3}.wall{fill:#ead7b8;stroke:#14233a;stroke-width:2}.module{fill:#d8e7f7;stroke:#205ec8;stroke-width:2}.greenhouse{fill:#dff4ea;fill-opacity:.65;stroke:#1f7a4d;stroke-width:2}.service{fill:#e4e8ed;stroke:#14233a;stroke-width:2}.jarvis{fill:#dce8ff;stroke:#123d8d;stroke-width:2}.roomfill{fill:#fff8eb;stroke:#8c6b39;stroke-width:1.5}.bath{fill:#e2f5fa;stroke:#24738b;stroke-width:1.5}.dim{stroke:#26364a;stroke-width:1.4;marker-start:url(#a);marker-end:url(#a)}.dt{font-size:13px;text-anchor:middle;fill:#26364a}.note{font-size:14px;fill:#a12525;font-weight:bold}.room{font-size:15px;font-weight:bold;text-anchor:middle}.dash{fill:none;stroke:#66778b;stroke-width:1.4;stroke-dasharray:6 4}</style>',
        '<defs><marker id="a" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto"><path d="M0,3 L6,0 L6,6 Z" fill="#26364a"/></marker></defs>',
        '<rect width="1600" height="1120" fill="white"/>',
        '<text x="55" y="55" class="title">PROJECT DOMUS · PLANO TÉCNICO ACOTADO</text>',
        '<text x="55" y="86" class="sub">Casa de una sola planta abierta al frente · cotas en milímetros · sistema totalmente local</text>',
    ]

    # A: Planta general. Se invierte Y para que el frente quede abajo.
    ox, oy, sc = 70, 155, 0.70
    def rect(x, y, w, h, cls, label=""):
        sx, sy, sw, sh = ox + x * sc, oy + (650 - y - h) * sc, w * sc, h * sc
        svg.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" class="{cls}"/>')
        if label:
            svg.append(f'<text x="{sx+sw/2}" y="{sy+sh/2}" class="room">{label}</text>')
        return sx, sy, sw, sh

    svg.append('<text x="70" y="125" class="h">A · PLANTA GENERAL</text>')
    rect(0, 0, 1000, 650, "outline")
    rect(25, 230, 250, 350, "greenhouse", "INVERNADERO")
    rect(300, 300, 430, 325, "wall")
    rect(305, 305, 225, 315, "roomfill", "COCINA + SALA")
    rect(530, 305, 150, 315, "roomfill", "DORMITORIO")
    rect(680, 305, 45, 315, "bath", "BAÑO")
    rect(340, 72, 250, 195, "module", "PORCHE / ENTRADA")
    rect(750, 245, 105, 118, "jarvis", "JARVIS")
    rect(870, 235, 110, 150, "service", "GABINETE")
    rect(25, 65, 92, 92, "module", "AGUA")
    # Equipamiento interior esquemático.
    rect(325, 572, 178, 42, "service", "COCINA")
    rect(405, 465, 118, 48, "module", "ISLA")
    rect(330, 350, 122, 55, "jarvis", "SOFÁ")
    rect(545, 405, 118, 178, "module", "CAMA")
    draw_dimension(svg, ox, oy + 650 * sc, ox + 1000 * sc, oy + 650 * sc, "1000", 28)
    draw_dimension(svg, ox, oy, ox, oy + 650 * sc, "650", -34, True)
    hy = oy + (650 - 300) * sc
    draw_dimension(svg, ox + 300 * sc, hy, ox + 730 * sc, hy, "430 casa", -18)
    draw_dimension(svg, ox + 25 * sc, oy + (650 - 230) * sc, ox + 275 * sc, oy + (650 - 230) * sc, "250", -18)
    draw_dimension(svg, ox + 340 * sc, oy + (650 - 72) * sc, ox + 590 * sc, oy + (650 - 72) * sc, "250 porche", 18)

    # B: Elevación frontal; muestra la composición modular de la referencia.
    ex, ey, es = 845, 455, 0.66
    svg.append('<text x="845" y="125" class="h">B · ELEVACIÓN FRONTAL</text>')
    svg.append(f'<rect x="{ex}" y="{ey}" width="{1000*es}" height="{12*es}" class="outline"/>')
    # invernadero con techo a dos aguas
    gx = ex + 25 * es
    svg.append(f'<path d="M {gx} {ey} L {gx} {ey-165*es} L {gx+125*es} {ey-225*es} L {gx+250*es} {ey-165*es} L {gx+250*es} {ey} Z" class="greenhouse"/>')
    # vivienda, Jarvis y gabinete
    svg.append(f'<rect x="{ex+300*es}" y="{ey-244*es}" width="{430*es}" height="{244*es}" class="wall"/>')
    svg.append(f'<rect x="{ex+292*es}" y="{ey-254*es}" width="{446*es}" height="{10*es}" fill="#152133"/>')
    svg.append(f'<rect x="{ex+355*es}" y="{ey-263*es}" width="{145*es}" height="{7*es}" fill="#08245f"/>')
    svg.append(f'<rect x="{ex+535*es}" y="{ey-263*es}" width="{145*es}" height="{7*es}" fill="#08245f"/>')
    svg.append(f'<rect x="{ex+750*es}" y="{ey-302*es}" width="{105*es}" height="{302*es}" class="jarvis"/>')
    svg.append(f'<rect x="{ex+870*es}" y="{ey-269*es}" width="{110*es}" height="{269*es}" class="service"/>')
    draw_dimension(svg, ex + 300 * es, ey, ex + 300 * es, ey - 254 * es, "254 casa", -24, True)
    draw_dimension(svg, ex + 750 * es, ey, ex + 750 * es, ey - 302 * es, "302 Jarvis", -22, True)
    draw_dimension(svg, ex + 25 * es, ey, ex + 25 * es, ey - 225 * es, "225 invernadero", -20, True)
    svg.append(f'<text x="{ex+515*es}" y="{ey+42}" class="lbl" text-anchor="middle">Frente abierto: interior visible sin desmontar una fachada</text>')

    # C: Elevación lateral simplificada.
    sx, sy, ss = 70, 1020, 0.72
    svg.append('<text x="70" y="705" class="h">C · ELEVACIÓN LATERAL DERECHA</text>')
    svg.append(f'<rect x="{sx}" y="{sy}" width="{650*ss}" height="{12*ss}" class="outline"/>')
    svg.append(f'<rect x="{sx+300*ss}" y="{sy-244*ss}" width="{325*ss}" height="{244*ss}" class="wall"/>')
    svg.append(f'<rect x="{sx+292*ss}" y="{sy-254*ss}" width="{341*ss}" height="{10*ss}" fill="#152133"/>')
    svg.append(f'<rect x="{sx+72*ss}" y="{sy-154*ss}" width="{195*ss}" height="{154*ss}" class="module"/>')
    draw_dimension(svg, sx, sy, sx + 650 * ss, sy, "650 fondo total", 28)
    draw_dimension(svg, sx + 300 * ss, sy, sx + 625 * ss, sy, "325 vivienda", 50)

    # D: Tabla de medidas y criterios.
    nx = 650
    svg += [
        f'<text x="{nx}" y="705" class="h">D · MEDIDAS PRINCIPALES</text>',
        f'<text x="{nx}" y="742" class="lbl">Base negra: 1000 × 650 × 12</text>',
        f'<text x="{nx}" y="770" class="lbl">Vivienda: 430 × 325 × 254 total · interior libre 225 de alto</text>',
        f'<text x="{nx}" y="798" class="lbl">Invernadero: 250 × 350 × 225 · panel transparente 1–2</text>',
        f'<text x="{nx}" y="826" class="lbl">Porche: 250 × 195 × 154 · pasarela frontal de 58</text>',
        f'<text x="{nx}" y="854" class="lbl">Torre Jarvis: 105 × 118 × 302 · gabinete: 110 × 150 × 269</text>',
        f'<text x="{nx}" y="900" class="h">E · CRITERIOS DE MONTAJE</text>',
        f'<text x="{nx}" y="934" class="lbl">• Una sola planta; no existe escalera ni entrepiso.</text>',
        f'<text x="{nx}" y="962" class="lbl">• Techo removible; fachada abierta; gabinete electrónico desmontable.</text>',
        f'<text x="{nx}" y="990" class="lbl">• Depósito y bomba al extremo opuesto del ESP32-S3.</text>',
        f'<text x="{nx}" y="1018" class="lbl">• Cableado por canaleta inferior; alimentación general de 5 V DC.</text>',
        f'<text x="{nx}" y="1054" class="note">SIN Wi-Fi · SIN Bluetooth/BLE · SIN teléfono · SIN nube</text>',
        '<text x="55" y="1092" class="small">Revisión 2.0 · tolerancia inicial ±0.5 mm · verificar dimensiones físicas de cada módulo antes del corte definitivo</text>',
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
    all_faces = []
    face_colors = []
    for part in ordered:
        vertices = box_vertices(part)
        faces = [[vertices[i] for i in face] for face in FACES]
        rgba = MATERIALS[part.material]
        all_faces.extend(faces)
        face_colors.extend([rgba] * len(faces))
    poly = Poly3DCollection(all_faces, facecolors=face_colors, edgecolors=(0.08, 0.12, 0.18, 0.48), linewidths=0.25)
    ax.add_collection3d(poly)
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 650)
    ax.set_zlim(0, 390)
    ax.set_box_aspect((1000, 650, 390))
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
        "PROJECT DOMUS · maqueta de una planta · sistema 100 % local",
        25,
        -62,
    )
    cutaway = [part for part in parts if part.layer not in {"roof", "solar"}]
    render_one(
        cutaway,
        "project_domus_cutaway.png",
        "PROJECT DOMUS · vista interior sin techo",
        32,
        -68,
    )
    exploded = []
    for part in parts:
        dx = dz = 0
        if part.layer == "roof":
            dz = 105
        elif part.layer == "solar":
            dz = 155
        elif part.layer in {"electronics", "boards"}:
            dx = 45
        elif part.layer == "greenhouse":
            dx = -20
        exploded.append(replace(part, x=part.x + dx, z=part.z + dz))
    render_one(
        exploded,
        "project_domus_exploded.png",
        "PROJECT DOMUS · vista explotada de módulos removibles",
        25,
        -62,
    )


def write_viewer(parts: list[Part]) -> None:
    data = json.dumps([asdict(part) for part in parts], ensure_ascii=False)
    colors = json.dumps({key: value[:3] for key, value in MATERIALS.items()})
    html = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PROJECT DOMUS · visor 3D local</title>
<style>
*{{box-sizing:border-box}}:root{{color-scheme:dark;background:#0a0f18;color:#edf4ff;font-family:Inter,system-ui,sans-serif}}body{{margin:0;display:grid;grid-template-columns:310px 1fr;min-height:100vh}}aside{{padding:18px;background:#111a29;border-right:1px solid #26344a;overflow:auto}}h1{{font-size:20px;margin:0 0 8px}}h2{{font-size:14px;margin:18px 0 8px;color:#bcd2f4}}p{{color:#9fb0c8;font-size:13px;line-height:1.45}}label{{display:block;margin:9px 0;font-size:13px}}button{{padding:8px 10px;background:#205fc9;color:white;border:1px solid #4380df;border-radius:7px;cursor:pointer}}button.secondary{{background:#1a2638;border-color:#364a66}}input[type=range]{{width:100%}}canvas{{width:100%;height:100vh;display:block;background:radial-gradient(circle at 50% 38%,#293c59,#070b12 72%);touch-action:none}}.layers{{display:grid;grid-template-columns:1fr 1fr;gap:2px;font-size:12px}}.badge{{display:inline-block;padding:4px 8px;background:#163d77;border-radius:99px;font-size:12px}}.buttons{{display:flex;flex-wrap:wrap;gap:6px}}#info{{min-height:84px;padding:10px;background:#0b1320;border:1px solid #2d3c53;border-radius:8px;color:#c9d8ec;font-size:12px;line-height:1.45}}#info strong{{color:white}}@media(max-width:760px){{body{{grid-template-columns:1fr}}aside{{border-right:0;border-bottom:1px solid #26344a}}canvas{{height:68vh}}}}
</style></head><body><aside><h1>PROJECT DOMUS</h1><span class="badge">UNA PLANTA · 100 % LOCAL</span><p>Arrastra para girar, usa la rueda para acercar y toca una pieza para ver sus medidas. Este archivo funciona sin Internet.</p>
<h2>Vistas rápidas</h2><div class="buttons"><button id="iso">Isométrica</button><button id="front" class="secondary">Frontal</button><button id="top" class="secondary">Superior</button><button id="inside" class="secondary">Interior</button></div>
<label>Rotación <input id="rot" type="range" min="-180" max="180" value="-35"></label>
<label>Elevación <input id="elev" type="range" min="10" max="70" value="30"></label>
<label>Zoom <input id="zoom" type="range" min="0.45" max="1.5" step="0.01" value="0.82"></label>
<button id="reset" class="secondary">Restablecer</button><h2>Capas</h2><div id="layers" class="layers"></div>
<h2>Pieza seleccionada</h2><div id="info" aria-live="polite">Toca cualquier elemento del modelo.</div>
<p><strong>Base:</strong> 1000 × 650 mm<br><strong>Casa:</strong> 430 × 325 mm<br><strong>Altura:</strong> una sola planta, 254 mm<br><strong>Módulos:</strong> invernadero, casa, porche, Jarvis y gabinete</p></aside><canvas id="c" aria-label="Modelo tridimensional interactivo de Project Domus"></canvas>
<script>
const parts={data}; const colors={colors}; const canvas=document.getElementById('c'),ctx=canvas.getContext('2d');
const names={{base:'base',systems:'sistema',house:'casa',roof:'techo',furniture:'muebles',bath:'baño',solar:'paneles',porch:'porche',landscape:'jardín',sensors:'sensores',water:'agua/riego',greenhouse:'invernadero',plants:'plantas',jarvis:'Jarvis',electronics:'gabinete',boards:'placas',lights:'luces'}};
const layerNames=[...new Set(parts.map(p=>p.layer))], visible=Object.fromEntries(layerNames.map(x=>[x,true]));
const layerBox=document.getElementById('layers'); layerNames.forEach(layer=>{{const l=document.createElement('label');const i=document.createElement('input');i.type='checkbox';i.checked=true;i.onchange=()=>{{visible[layer]=i.checked;draw()}};l.append(i,document.createTextNode(' '+layer));layerBox.append(l)}});
let rot=-35,elev=30,zoom=.82,drag=false,moved=false,lastX=0,lastY=0,centers=[];
function size(){{const d=devicePixelRatio||1;canvas.width=canvas.clientWidth*d;canvas.height=canvas.clientHeight*d;ctx.setTransform(d,0,0,d,0,0);draw()}}
function project(v){{let a=rot*Math.PI/180,e=elev*Math.PI/180,x=v[0]-500,y=v[1]-325,z=v[2]-145;let xr=x*Math.cos(a)-y*Math.sin(a),yr=x*Math.sin(a)+y*Math.cos(a);let yy=yr*Math.sin(e)-z*Math.cos(e),depth=yr*Math.cos(e)+z*Math.sin(e);let s=Math.min(canvas.clientWidth/1100,canvas.clientHeight/710)*zoom;return [canvas.clientWidth/2+xr*s,canvas.clientHeight/2+yy*s,depth]}}
const faces=[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[4,0,3,7]];
function verts(p){{let x=p.x,y=p.y,z=p.z,w=p.w,d=p.d,h=p.h,cx=x+w/2,cy=y+d/2,cz=z+h/2;let vs=[[x,y,z],[x+w,y,z],[x+w,y+d,z],[x,y+d,z],[x,y,z+h],[x+w,y,z+h],[x+w,y+d,z+h],[x,y+d,z+h]],rx=(p.rx||0)*Math.PI/180,ry=(p.ry||0)*Math.PI/180,rz=(p.rz||0)*Math.PI/180;return vs.map(v=>{{let X=v[0]-cx,Y=v[1]-cy,Z=v[2]-cz,q=Y*Math.cos(rx)-Z*Math.sin(rx);Z=Y*Math.sin(rx)+Z*Math.cos(rx);Y=q;q=X*Math.cos(ry)+Z*Math.sin(ry);Z=-X*Math.sin(ry)+Z*Math.cos(ry);X=q;q=X*Math.cos(rz)-Y*Math.sin(rz);Y=X*Math.sin(rz)+Y*Math.cos(rz);X=q;return [X+cx,Y+cy,Z+cz]}})}}
function draw(){{ctx.clearRect(0,0,canvas.clientWidth,canvas.clientHeight);let polys=[];centers=[];parts.filter(p=>visible[p.layer]).forEach(p=>{{let raw=verts(p),vv=raw.map(project);faces.forEach((f,fi)=>{{let pts=f.map(i=>vv[i]);polys.push({{pts,depth:pts.reduce((s,q)=>s+q[2],0)/4,p,fi}})}});let cc=project([p.x+p.w/2,p.y+p.d/2,p.z+p.h/2]);centers.push({{x:cc[0],y:cc[1],p}})}});polys.sort((a,b)=>a.depth-b.depth);polys.forEach(o=>{{let c=colors[o.p.material]||[.5,.5,.5],shade=.62+o.fi*.045;ctx.beginPath();o.pts.forEach((q,i)=>i?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]));ctx.closePath();ctx.fillStyle=`rgba(${{c.map(v=>Math.round(v*255*shade)).join(',')}},${{o.p.material==='glass'?.20:.96}})`;ctx.fill();ctx.strokeStyle='rgba(5,12,24,.35)';ctx.lineWidth=.55;ctx.stroke()}})}}
document.getElementById('rot').oninput=e=>{{rot=+e.target.value;draw()}};
document.getElementById('elev').oninput=e=>{{elev=+e.target.value;draw()}};
document.getElementById('zoom').oninput=e=>{{zoom=+e.target.value;draw()}};
function setView(r,e,z){{rot=r;elev=e;zoom=z;document.getElementById('rot').value=r;document.getElementById('elev').value=e;document.getElementById('zoom').value=z;draw()}}
canvas.onpointerdown=e=>{{drag=true;moved=false;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture(e.pointerId)}};canvas.onpointermove=e=>{{if(!drag)return;let dx=e.clientX-lastX,dy=e.clientY-lastY;if(Math.abs(dx)+Math.abs(dy)>2)moved=true;rot+=dx*.4;elev=Math.max(10,Math.min(70,elev-dy*.25));lastX=e.clientX;lastY=e.clientY;document.getElementById('rot').value=rot;document.getElementById('elev').value=elev;draw()}};canvas.onpointerup=e=>{{drag=false;if(moved)return;let r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top,best=null,dist=32;centers.forEach(c=>{{let d=Math.hypot(c.x-x,c.y-y);if(d<dist){{best=c.p;dist=d}}}});if(best)document.getElementById('info').innerHTML=`<strong>${{best.name}}</strong><br>${{best.w}} × ${{best.d}} × ${{best.h}} mm<br>Capa: ${{names[best.layer]||best.layer}}${{best.note?'<br>'+best.note:''}}`;}};canvas.onwheel=e=>{{e.preventDefault();zoom=Math.max(.45,Math.min(1.5,zoom-e.deltaY*.0008));document.getElementById('zoom').value=zoom;draw()}};
document.getElementById('iso').onclick=()=>setView(-35,30,.82);document.getElementById('front').onclick=()=>setView(0,18,.92);document.getElementById('top').onclick=()=>setView(0,70,.82);document.getElementById('inside').onclick=()=>{{visible.roof=false;visible.solar=false;[...layerBox.querySelectorAll('label')].forEach((l,i)=>l.querySelector('input').checked=visible[layerNames[i]]);setView(-20,32,.95)}};document.getElementById('reset').onclick=()=>{{layerNames.forEach(x=>visible[x]=true);layerBox.querySelectorAll('input').forEach(i=>i.checked=true);setView(-35,30,.82)}};addEventListener('resize',size);size();
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
