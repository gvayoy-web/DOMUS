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

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors as rl_colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdf_canvas


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
    "signal": (0.96, 0.55, 0.07, 1.0),
    "cable_power": (0.93, 0.16, 0.16, 1.0),
    "cable_ground": (0.08, 0.10, 0.14, 1.0),
    "acrylic": (0.65, 0.88, 0.94, 0.28),
    "magnet": (0.75, 0.79, 0.84, 1.0),
    "yellow": (0.96, 0.74, 0.08, 1.0),
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


def enhance_parts(parts: list[Part]) -> list[Part]:
    """Añade detalle constructivo legible sin cambiar la envolvente validada."""
    details = []

    # Modulación de tablones, divisiones y frentes de mobiliario.
    for x in range(310, 731, 42):
        details.append(p(f"Junta de tablón {x}", x, 621, 20, 1.4, 4, 222, "wood", "house", "Junta visual de panel"))
    details += [
        p("Tabique dormitorio", 532, 392, 19, 3, 228, 188, "wood_light", "house", "Panel interior desmontable"),
        p("Puerta interior", 529, 315, 19, 7, 72, 174, "wood", "house", "Hoja señalada en planta"),
        p("Frente cajón cocina 1", 340, 567, 36, 66, 4, 20, "wood_light", "furniture"),
        p("Frente cajón cocina 2", 410, 567, 36, 66, 4, 20, "wood_light", "furniture"),
        p("Fregadero", 452, 563, 94, 40, 30, 5, "metal", "furniture"),
        p("Grifo", 470, 594, 98, 5, 5, 30, "metal", "furniture"),
        p("Almohada", 563, 537, 80, 82, 34, 12, "white", "furniture"),
        p("Respaldo sofá", 330, 390, 55, 122, 14, 38, "blue", "furniture"),
        p("Lavamanos cubeta", 691, 435, 82, 27, 37, 8, "acrylic", "bath"),
        p("Ducha columna", 714, 566, 27, 6, 6, 138, "metal", "bath"),
    ]

    # Celdas solares y fijaciones removibles.
    for px in (355, 535):
        for row in range(4):
            for col in range(6):
                details.append(p(f"Celda solar {px}-{row}-{col}", px + 5 + col * 22.5, 386 + row * 24, 262.2, 18, 18, 1.2, "blue", "solar", "Retícula didáctica del panel"))
    for x, y in ((300, 300), (724, 300), (300, 620), (724, 620)):
        details.append(p(f"Imán techo {x}-{y}", x, y, 241, 8, 8, 4, "magnet", "removable", "Imán de alineación del techo"))
    details += [
        p("Bisagra gabinete izquierda", 872, 232, 72, 8, 7, 24, "magnet", "removable"),
        p("Bisagra gabinete derecha", 963, 232, 72, 8, 7, 24, "magnet", "removable"),
        p("Bandeja antiderrame", 18, 58, 10, 106, 106, 4, "blue_light", "water", "Bandeja separada de la electrónica"),
        p("Drenaje bandeja", 18, 109, 10, 22, 8, 6, "water", "water", "Salida hacia borde exterior"),
    ]

    # Plantas: tallos y hojas simples, visibles en render y OBJ.
    for x in (48, 88, 172, 212):
        details += [
            p(f"Tallo planta {x}", x + 3, 333, 61, 4, 4, 62, "green", "plants"),
            p(f"Hoja A planta {x}", x - 7, 327, 92, 20, 8, 5, "green", "plants", rz=28),
            p(f"Hoja B planta {x}", x + 1, 337, 108, 22, 8, 5, "green", "plants", rz=-24),
        ]

    # Rutas de baja tensión. Son guías de lectura, no un pinout.
    details += [
        p("Bus 5V canal técnico", 295, 38, 29, 670, 4, 4, "cable_power", "power", "Ruta 5 V DC; consultar tabla de cableado validada"),
        p("Bus GND canal técnico", 295, 46, 29, 670, 4, 4, "cable_ground", "power", "Retorno común GND"),
        p("Señal gabinete-casa", 705, 54, 31, 250, 4, 4, "signal", "signal", "Ruta lógica; sin asignar GPIO no verificado"),
        p("Señal sensores casa", 575, 60, 33, 4, 550, 4, "signal", "signal", "DHT11, LDR y PIR"),
        p("Alimentación invernadero", 245, 55, 31, 4, 445, 4, "cable_power", "power", "Bomba, humedad y luz"),
        p("Manguera depósito-bomba", 103, 111, 48, 30, 8, 8, "water", "water", "Línea de aspiración"),
        p("Manguera principal riego", 158, 130, 48, 8, 150, 8, "blue_light", "water", "Impulsión hacia invernadero"),
    ]

    # Lectura del gabinete: chips, bornes y separadores.
    details += [
        p("Chip ESP32-S3", 899, 343, 128, 19, 14, 5, "metal", "boards", "Procesamiento 100 % local"),
        p("Conector USB servicio", 902, 332, 70, 14, 7, 8, "metal", "boards", "Solo programación/mantenimiento"),
        p("Bornera 5V roja", 932, 289, 79, 13, 8, 8, "cable_power", "boards", "Bus protegido por fusible 3 A"),
        p("Bornera GND negra", 950, 289, 79, 13, 8, 8, "cable_ground", "boards", "Retorno común"),
    ]
    for i in range(4):
        details.append(p(f"Terminal relé CH{i+1}", 941, 326, 72 + i * 22, 22, 8, 7, "yellow", "boards", "Canal de actuador"))

    completed = parts + details
    technical_notes = {
        "ESP32-S3 N16R8": "Controlador central local; sin Wi-Fi, Bluetooth, teléfono ni nube. Consultar la tabla validada antes de asignar GPIO.",
        "Módulo relés 4 canales": "Conmuta actuadores de 5 V; verificar estado seguro al arranque y separación de rutas de señal.",
        "Depósito de agua": "Reserva 92 × 92 × 100 mm sobre bandeja de contención, separada del gabinete electrónico.",
        "Mini bomba 5V": "Riego local con bloqueo por nivel bajo y tiempo máximo continuo de 120 s.",
        "Fusible 3A": "Protección principal colocada antes del bus de distribución 5 V/GND.",
        "Sensor nivel depósito": "Inhibe la bomba cuando detecta nivel bajo; comprobar su actuación antes de exhibir.",
        "Sensor humedad suelo": "Solicita riego por debajo de 30 % y lo detiene al alcanzar 45 %.",
        "DHT11 interior": "Mide ambiente interior; ventilación activa a 29 °C y se detiene a 27 °C.",
        "LDR bajo alero": "Mide luz exterior protegido por el alero; control autónomo sin servicio remoto.",
        "PIR entrada": "Detección local de presencia en el acceso para iluminación y demostración.",
        "Distribuidor 5V-GND": "Punto de distribución de baja tensión; conservar polaridad y retorno común.",
        "Regleta de terminales": "Interfaz de servicio etiquetada; usar la tabla de cableado validada, sin inventar pines.",
    }
    for item in completed:
        if item.name in technical_notes:
            item.note = technical_notes[item.name]
        if item.note:
            continue
        family_notes = {
            "base": "Elemento de soporte y presentación; conservar escuadra, nivel y acceso a la canaleta.",
            "systems": "Canal técnico removible para ordenar baja tensión y señal durante montaje y mantenimiento.",
            "house": "Pieza estructural de la vivienda de una planta; presentar en seco antes de fijar.",
            "roof": "Elemento superior removible para inspección y mantenimiento del interior.",
            "furniture": "Mobiliario didáctico que ayuda a leer la distribución interior y la escala de la maqueta.",
            "bath": "Elemento del baño representado para lectura espacial; no forma parte del circuito hidráulico de riego.",
            "solar": "Detalle del conjunto solar didáctico sobre el techo removible; conservar acceso a sus conexiones.",
            "porch": "Pieza del acceso frontal; alinear con la pasarela y mantener libre la zona del PIR.",
            "landscape": "Elemento paisajístico de presentación sin función eléctrica o hidráulica activa.",
            "sensors": "Sensor local del sistema; confirmar orientación y conexión en la tabla de cableado validada.",
            "water": "Componente del recorrido de riego; revisar uniones y fugas lejos de la electrónica.",
            "greenhouse": "Pieza del invernadero; mantener paneles transparentes accesibles y bancales nivelados.",
            "plants": "Representación de cultivo para explicar la zona supervisada por humedad y riego.",
            "jarvis": "Elemento de la interfaz local Jarvis; no depende de red, teléfono ni nube.",
            "electronics": "Parte del gabinete técnico; mantener ventilación, etiquetado y acceso de servicio.",
            "boards": "Módulo electrónico de baja tensión; usar identificación y cableado previamente validados.",
            "lights": "Indicador o luminaria local de 5 V controlada por el sistema.",
            "power": "Ruta de alimentación de baja tensión; conservar polaridad, protección y separación física.",
            "signal": "Ruta lógica local; no implica un GPIO concreto y debe contrastarse con la tabla validada.",
            "removable": "Herraje o fijación de un componente removible para inspección sin dañar la maqueta.",
        }
        item.note = family_notes.get(item.layer, "Pieza geométrica documentada en el inventario del modelo.")
    return completed


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
    width, height = 2400, 1500
    image = Image.new("RGBA", (width, height), "#eef3f7")
    draw = ImageDraw.Draw(image, "RGBA")
    for x in range(0, width, 60):
        draw.line((x, 0, x, height), fill=(155, 175, 195, 35), width=1)
    for y in range(0, height, 60):
        draw.line((0, y, width, y), fill=(155, 175, 195, 35), width=1)
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 54)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 25)
    except OSError:
        font_title = ImageFont.load_default(); font_sub = ImageFont.load_default()
    draw.rectangle((0, 0, width, 150), fill="#08111f")
    draw.text((78, 38), title, font=font_title, fill="#ffffff")
    draw.text((82, 104), "GEMELO DIGITAL v3 · 100 % LOCAL · 5 V DC", font=font_sub, fill="#12b8d0")
    a, e = math.radians(azim), math.radians(elev)
    scale = min((width-160)/1200, (height-250)/820)
    def project3(v):
        x,y,z=v[0]-500,v[1]-325,v[2]-130
        xr=x*math.cos(a)-y*math.sin(a); yr=x*math.sin(a)+y*math.cos(a)
        yy=yr*math.sin(e)-z*math.cos(e); depth=yr*math.cos(e)+z*math.sin(e)
        return width/2+xr*scale, height/2+100+yy*scale, depth
    polygons=[]
    for part in parts:
        vv=[project3(v) for v in box_vertices(part)]
        for fi, face in enumerate(FACES):
            pts=[vv[i] for i in face]; polygons.append((sum(q[2] for q in pts)/4,pts,part,fi))
    polygons.sort(key=lambda x:x[0])
    for _, pts, part, fi in polygons:
        rgba=MATERIALS[part.material]; shade=.70+fi*.035
        col=tuple(max(0,min(255,round(v*255*shade))) for v in rgba[:3])
        alpha=65 if part.material in {"glass","acrylic"} else 238
        draw.polygon([(q[0],q[1]) for q in pts], fill=(*col,alpha), outline=(8,17,31,115))
    draw.rectangle((62,height-112,525,height-52),fill=(255,255,255,225),outline="#9db0c2",width=2)
    draw.text((82,height-98),"BASE 1000 × 650 mm  |  FRENTE ABIERTO  |  COTAS EN mm",font=font_sub,fill="#10233f")
    image.convert("RGB").save(ROOT / filename, quality=94)


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


def write_svg_v3() -> None:
    """Preview vectorial de la planta general, optimizado para lectura en pantalla."""
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1080" viewBox="0 0 1600 1080">']
    svg += [
        '<defs><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#dbe4ed" stroke-width="1"/></pattern><filter id="shadow"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-opacity=".12"/></filter></defs>',
        '<rect width="1600" height="1080" fill="#eef3f7"/><rect width="1600" height="1080" fill="url(#grid)"/>',
        '<style>text{font-family:Bahnschrift,Segoe UI,Arial,sans-serif;fill:#10233f}.k{font-size:15px;letter-spacing:2px;font-weight:700}.t{font-size:42px;font-weight:800}.s{font-size:17px;fill:#4c6177}.h{font-size:20px;font-weight:800}.l{font-size:14px;font-weight:650}.tiny{font-size:12px}.dim{stroke:#155eef;stroke-width:1.6}.axis{stroke:#10233f;stroke-width:2}.box{stroke:#10233f;stroke-width:2}.dash{fill:none;stroke:#697c90;stroke-width:1.4;stroke-dasharray:7 5}</style>',
        '<rect x="42" y="38" width="1516" height="1004" rx="2" fill="#fff" stroke="#b7c5d3" filter="url(#shadow)"/>',
        '<text x="82" y="88" class="k" fill="#155eef">GEMELO DIGITAL v3 · LÁMINA DE IMPLANTACIÓN</text>',
        '<text x="82" y="139" class="t">PROJECT DOMUS</text>',
        '<text x="82" y="171" class="s">Una planta · frente abierto · 100 % local · alimentación 5 V DC · cotas en mm</text>',
        '<rect x="1235" y="76" width="263" height="79" fill="#08111f"/><text x="1260" y="108" class="k" fill="#12b8d0">REV 3.0</text><text x="1260" y="137" class="l" fill="white">CONSTRUCCIÓN + FERIA</text>',
    ]
    ox, oy, sc = 110, 285, 1.18
    def r(x, y, w, h, fill, label, sub=""):
        sx, sy, sw, sh = ox + x * sc, oy + (650 - y - h) * sc, w * sc, h * sc
        svg.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="{fill}" class="box"/>')
        svg.append(f'<text x="{sx+sw/2}" y="{sy+sh/2-2}" text-anchor="middle" class="l">{label}</text>')
        if sub:
            svg.append(f'<text x="{sx+sw/2}" y="{sy+sh/2+18}" text-anchor="middle" class="tiny">{sub}</text>')
    svg.append(f'<rect x="{ox}" y="{oy}" width="{1000*sc}" height="{650*sc}" fill="#f8fafc" class="box"/>')
    r(25,230,250,350,"#dff4ea","INVERNADERO","250 × 350 × 225")
    r(300,300,430,325,"#f3dfbf","VIVIENDA ABIERTA","430 × 325 · techo removible")
    r(340,72,250,195,"#dbeafe","PORCHE","250 × 195 × 154")
    r(750,245,105,118,"#d6e4ff","JARVIS","105 × 118 × 302")
    r(870,235,110,150,"#e6edf3","GABINETE","110 × 150 × 269")
    r(25,65,92,92,"#c9effb","DEPÓSITO","92 × 92 × 100")
    # Interior y recorridos.
    for x,y,w,h,fill,label in [(325,572,178,42,'#c58a4a','COCINA'),(405,465,118,48,'#e7bd83','ISLA'),(330,350,122,55,'#8bb8ff','SOFÁ'),(545,405,118,178,'#eff3f7','CAMA'),(680,305,45,315,'#d8f3f7','BAÑO')]:
        r(x,y,w,h,fill,label)
    # Líneas de sistema.
    def path(points, color, width, dash=""):
        pts=' '.join(f'{ox+x*sc},{oy+(650-y)*sc}' for x,y in points)
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {dash}/>')
    path([(70,110),(160,110),(160,280),(190,280),(190,520)], '#1c9ee8', 7)
    path([(930,260),(930,45),(290,45),(290,500)], '#ef4444', 5)
    path([(930,275),(700,275),(575,580)], '#f59e0b', 4, 'stroke-dasharray="10 6"')
    svg += [
        f'<line x1="{ox}" y1="{oy+650*sc+44}" x2="{ox+1000*sc}" y2="{oy+650*sc+44}" class="dim"/><text x="{ox+500*sc}" y="{oy+650*sc+35}" text-anchor="middle" class="l" fill="#155eef">1000</text>',
        f'<text x="{ox+500*sc}" y="{oy+650*sc+76}" text-anchor="middle" class="k">FRENTE / VISITANTE ↓</text>',
        '<text x="1335" y="285" class="h">LEYENDA</text>',
        '<line x1="1335" y1="328" x2="1392" y2="328" stroke="#ef4444" stroke-width="6"/><text x="1410" y="334" class="l">Energía 5 V</text>',
        '<line x1="1335" y1="371" x2="1392" y2="371" stroke="#f59e0b" stroke-width="5" stroke-dasharray="10 6"/><text x="1410" y="377" class="l">Señal</text>',
        '<line x1="1335" y1="414" x2="1392" y2="414" stroke="#1c9ee8" stroke-width="7"/><text x="1410" y="420" class="l">Agua/riego</text>',
        '<circle cx="1362" cy="458" r="10" fill="#23a36d"/><text x="1410" y="464" class="l">Sensor</text>',
        '<rect x="1335" y="512" width="180" height="132" fill="#f7f9fb" stroke="#9aacbd"/><text x="1354" y="543" class="k">NORTE</text><path d="M1425 610V554M1425 554l-12 20M1425 554l12 20" class="axis"/><text x="1418" y="632" class="h">N</text>',
        '<text x="1335" y="710" class="h">CONTROL DE RIESGO</text>',
        '<text x="1335" y="744" class="l">• Agua aislada del gabinete.</text><text x="1335" y="773" class="l">• Fusible 3 A antes del bus.</text><text x="1335" y="802" class="l">• Bomba: máximo 120 s.</text><text x="1335" y="831" class="l">• Bloqueo por nivel bajo.</text>',
        '<text x="1335" y="890" class="h">ESCALA GRÁFICA</text><rect x="1335" y="916" width="80" height="14" fill="#10233f"/><rect x="1415" y="916" width="80" height="14" fill="white" stroke="#10233f"/><text x="1335" y="950" class="tiny">0</text><text x="1410" y="950" class="tiny">100</text><text x="1488" y="950" class="tiny">200 mm</text>',
        '<text x="82" y="1015" class="tiny">PL-01 · implantación general · verificar piezas físicas antes del corte definitivo · tolerancia inicial ±0.5 mm</text>',
        '</svg>'
    ]
    (ROOT / "plano_tecnico_domus.svg").write_text("\n".join(svg), encoding="utf-8")


def _pdf_header(c, page_no, code, title, subtitle=""):
    W, H = landscape(A3)
    c.setFillColor(rl_colors.HexColor('#ffffff')); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(rl_colors.HexColor('#08111f')); c.rect(0, H-24*mm, W, 24*mm, fill=1, stroke=0)
    c.setFillColor(rl_colors.HexColor('#12b8d0')); c.setFont('Helvetica-Bold', 9); c.drawString(16*mm, H-10*mm, 'PROJECT DOMUS · GEMELO DIGITAL v3')
    c.setFillColor(rl_colors.white); c.setFont('Helvetica-Bold', 20); c.drawString(16*mm, H-19*mm, title)
    if subtitle:
        c.setFillColor(rl_colors.HexColor('#4b6075')); c.setFont('Helvetica', 8); c.drawString(16*mm, H-30*mm, subtitle)
    c.setFillColor(rl_colors.HexColor('#10233f')); c.setFont('Helvetica-Bold', 8); c.drawRightString(W-16*mm, 10*mm, f'{code} · PÁGINA {page_no}/6 · REV 3.0')
    c.setStrokeColor(rl_colors.HexColor('#9db0c2')); c.line(16*mm, 14*mm, W-16*mm, 14*mm)
    return W, H


def _pdf_label(c, x, y, text, fill='#155eef'):
    c.setFillColor(rl_colors.HexColor(fill)); c.roundRect(x, y-5*mm, 28*mm, 7*mm, 1.5*mm, fill=1, stroke=0)
    c.setFillColor(rl_colors.white); c.setFont('Helvetica-Bold', 7); c.drawCentredString(x+14*mm, y-2.6*mm, text)


def _pdf_dim(c, x1, y1, x2, y2, text):
    c.setStrokeColor(rl_colors.HexColor('#155eef')); c.setLineWidth(.7)
    c.line(x1,y1,x2,y2); c.line(x1,y1-2*mm,x1,y1+2*mm); c.line(x2,y2-2*mm,x2,y2+2*mm)
    c.setFillColor(rl_colors.HexColor('#155eef')); c.setFont('Helvetica-Bold', 7); c.drawCentredString((x1+x2)/2, y1+2*mm, text)


def write_pdf_v3() -> Path:
    out = ROOT.parents[5] / 'output' / 'pdf' / 'planos_tecnicos_project_domus.pdf'
    out.parent.mkdir(parents=True, exist_ok=True)
    c = pdf_canvas.Canvas(str(out), pagesize=landscape(A3), pageCompression=1)
    W, H = landscape(A3)

    # 1 · Portada
    _pdf_header(c,1,'PL-00','JUEGO DE PLANOS TÉCNICOS','A3 apaisado · cotas en milímetros · maqueta educativa de baja tensión')
    render = ROOT/'project_domus_render.png'
    if render.exists(): c.drawImage(str(render), 18*mm, 30*mm, width=245*mm, height=154*mm, preserveAspectRatio=True, anchor='c', mask='auto')
    c.setFillColor(rl_colors.HexColor('#eef3f7')); c.rect(276*mm,30*mm,125*mm,154*mm,fill=1,stroke=0)
    c.setFillColor(rl_colors.HexColor('#10233f')); c.setFont('Helvetica-Bold',18); c.drawString(288*mm,168*mm,'ÍNDICE VISUAL')
    pages=[('01','Implantación y planta general'),('02','Elevaciones y sección'),('03','Baja tensión y control'),('04','Agua y riego seguro'),('05','Explosión, montaje y corte')]
    yy=150
    for n,t in pages:
        c.setFillColor(rl_colors.HexColor('#155eef')); c.circle(292*mm,yy*mm,5*mm,fill=1,stroke=0); c.setFillColor(rl_colors.white); c.setFont('Helvetica-Bold',7); c.drawCentredString(292*mm,yy*mm-2,n)
        c.setFillColor(rl_colors.HexColor('#10233f')); c.setFont('Helvetica-Bold',9); c.drawString(302*mm,yy*mm-2,t); yy-=22
    c.setFont('Helvetica-Bold',10); c.drawString(288*mm,47*mm,'DATOS PRINCIPALES')
    c.setFont('Helvetica',8); c.drawString(288*mm,39*mm,'Base 1000 × 650 × 12 · 5 V DC · local · sin radio ni nube')
    c.showPage()

    # 2 · Planta
    _pdf_header(c,2,'PL-01','IMPLANTACIÓN Y PLANTA GENERAL','Ejes, huellas y recorridos principales; el frente de exposición queda abajo')
    ox,oy,s=25*mm,34*mm,.29*mm
    c.setFillColor(rl_colors.HexColor('#f7f9fb')); c.setStrokeColor(rl_colors.HexColor('#10233f')); c.setLineWidth(1); c.rect(ox,oy,1000*s,650*s,fill=1,stroke=1)
    modules=[(25,230,250,350,'#dff4ea','INVERNADERO'),(300,300,430,325,'#f3dfbf','VIVIENDA'),(340,72,250,195,'#dbeafe','PORCHE'),(750,245,105,118,'#d6e4ff','JARVIS'),(870,235,110,150,'#e6edf3','GABINETE'),(25,65,92,92,'#c9effb','AGUA')]
    for x,y,w,h,col,label in modules:
        X,Y=ox+x*s,oy+y*s;c.setFillColor(rl_colors.HexColor(col));c.rect(X,Y,w*s,h*s,fill=1,stroke=1);c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica-Bold',7);c.drawCentredString(X+w*s/2,Y+h*s/2,label)
    _pdf_dim(c,ox,oy-8*mm,ox+1000*s,oy-8*mm,'1000');_pdf_dim(c,ox+300*s,oy+650*s+7*mm,ox+730*s,oy+650*s+7*mm,'430 VIVIENDA')
    c.saveState();c.translate(ox-8*mm,oy);c.rotate(90);_pdf_dim(c,0,0,650*s,0,'650');c.restoreState()
    c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica-Bold',9);c.drawCentredString(ox+500*s,oy-16*mm,'FRENTE / VISITANTE ↓')
    c.setFillColor(rl_colors.HexColor('#eef3f7'));c.rect(328*mm,34*mm,73*mm,188*mm,fill=1,stroke=0)
    _pdf_label(c,336*mm,210*mm,'HUELLAS')
    notes=['Invernadero 250 × 350 × 225','Casa 430 × 325 × 254 total','Porche 250 × 195 × 154','Jarvis 105 × 118 × 302','Gabinete 110 × 150 × 269','Depósito 92 × 92 × 100']
    c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica',8);yy=194
    for n in notes:c.drawString(336*mm,yy*mm,'• '+n);yy-=12
    c.setFont('Helvetica-Bold',9);c.drawString(336*mm,105*mm,'SEPARACIÓN FUNCIONAL')
    c.setFont('Helvetica',8);c.drawString(336*mm,94*mm,'Agua al extremo izquierdo.');c.drawString(336*mm,83*mm,'Control al extremo derecho.');c.drawString(336*mm,72*mm,'Canaleta inferior con tapa.');c.drawString(336*mm,61*mm,'Techo y gabinete removibles.')
    c.showPage()

    # 3 · Elevaciones y sección
    _pdf_header(c,3,'PL-02','ELEVACIONES Y SECCIÓN','Alturas totales y lectura del interior abierto')
    def elevation(x,y,scale):
        c.setStrokeColor(rl_colors.HexColor('#10233f'));c.setFillColor(rl_colors.HexColor('#f3dfbf'));c.rect(x+300*scale,y,430*scale,244*scale,fill=1,stroke=1)
        c.setFillColor(rl_colors.HexColor('#152133'));c.rect(x+292*scale,y+244*scale,446*scale,10*scale,fill=1,stroke=0)
        c.setFillColor(rl_colors.HexColor('#dff4ea'));c.setStrokeColor(rl_colors.HexColor('#23a36d'));c.line(x+25*scale,y,x+25*scale,y+165*scale);c.line(x+25*scale,y+165*scale,x+150*scale,y+225*scale);c.line(x+150*scale,y+225*scale,x+275*scale,y+165*scale);c.line(x+275*scale,y+165*scale,x+275*scale,y)
        c.setFillColor(rl_colors.HexColor('#d6e4ff'));c.setStrokeColor(rl_colors.HexColor('#10233f'));c.rect(x+750*scale,y,105*scale,302*scale,fill=1,stroke=1);c.setFillColor(rl_colors.HexColor('#e6edf3'));c.rect(x+870*scale,y,110*scale,269*scale,fill=1,stroke=1)
    _pdf_label(c,20*mm,218*mm,'FRONTAL'); elevation(20*mm,132*mm,.34*mm)
    _pdf_dim(c,20*mm+300*.34*mm,126*mm,20*mm+730*.34*mm,126*mm,'430');_pdf_dim(c,20*mm+750*.34*mm,120*mm,20*mm+855*.34*mm,120*mm,'105')
    _pdf_label(c,20*mm,104*mm,'SECCIÓN A-A')
    c.setFillColor(rl_colors.HexColor('#f8e7ca'));c.setStrokeColor(rl_colors.HexColor('#10233f'));c.rect(30*mm,35*mm,210*mm,62*mm,fill=1,stroke=1)
    for xx,label,w in [(40,'COCINA/SALA',85),(130,'DORMITORIO',66),(201,'BAÑO',30)]:c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica-Bold',8);c.drawCentredString((xx+w/2)*mm,62*mm,label)
    c.setStrokeColor(rl_colors.HexColor('#155eef'));c.setDash(5,4);c.rect(27*mm,100*mm,216*mm,5*mm,fill=0,stroke=1);c.setDash();c.setFillColor(rl_colors.HexColor('#155eef'));c.setFont('Helvetica-Bold',7);c.drawString(248*mm,100*mm,'TECHO REMOVIBLE')
    c.setFillColor(rl_colors.HexColor('#eef3f7'));c.rect(306*mm,35*mm,95*mm,183*mm,fill=1,stroke=0);_pdf_label(c,316*mm,205*mm,'COTAS Z')
    c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica',9);yy=187
    for n in ['302  torre Jarvis','269  gabinete','254  vivienda + techo','225  altura interior','225  invernadero','154  cubierta de porche','12  base estructural']:c.drawString(316*mm,yy*mm,n);yy-=17
    c.setFont('Helvetica-Bold',9);c.drawString(316*mm,61*mm,'ELEMENTOS REMOVIBLES');c.setFont('Helvetica',8);c.drawString(316*mm,50*mm,'Techo · frente de gabinete · paneles de servicio')
    c.showPage()

    # 4 · Eléctrico
    _pdf_header(c,4,'PL-03','PLANO ELÉCTRICO · BAJA TENSIÓN','Diagrama funcional; usar la tabla de cableado validada para GPIO concretos')
    nodes=[(24,165,55,24,'FUENTE 5 V','#155eef'),(103,165,48,24,'FUSIBLE 3 A','#ef4444'),(176,165,62,24,'BUS 5V / GND','#10233f'),(270,165,62,24,'ESP32-S3','#23a36d'),(356,165,43,24,'RELÉS x4','#155eef')]
    for x,y,w,h,label,col in nodes:
        c.setFillColor(rl_colors.HexColor('#f7f9fb'));c.setStrokeColor(rl_colors.HexColor(col));c.setLineWidth(2);c.roundRect(x*mm,y*mm,w*mm,h*mm,2*mm,fill=1,stroke=1);c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica-Bold',8);c.drawCentredString((x+w/2)*mm,(y+10)*mm,label)
    c.setStrokeColor(rl_colors.HexColor('#ef4444'));c.setLineWidth(3)
    for a,b in [((79,177),(103,177)),((151,177),(176,177)),((238,177),(270,177)),((332,177),(356,177))]:c.line(a[0]*mm,a[1]*mm,b[0]*mm,b[1]*mm)
    sensors=['DHT11 interior','LDR bajo alero','PIR entrada','Humedad suelo','Nivel de agua']
    actuators=['LED sala/dormitorio','LED invernadero','Ventilador','Mini bomba 5 V']
    for i,n in enumerate(sensors):
        y=127-i*19;c.setFillColor(rl_colors.HexColor('#fff7df'));c.setStrokeColor(rl_colors.HexColor('#f59e0b'));c.roundRect(45*mm,y*mm,65*mm,13*mm,2*mm,fill=1,stroke=1);c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica',7);c.drawCentredString(77.5*mm,(y+5)*mm,n);c.setStrokeColor(rl_colors.HexColor('#f59e0b'));c.setDash(4,3);c.line(110*mm,(y+6.5)*mm,270*mm,177*mm);c.setDash()
    for i,n in enumerate(actuators):
        y=125-i*22;c.setFillColor(rl_colors.HexColor('#eaf2ff'));c.setStrokeColor(rl_colors.HexColor('#155eef'));c.roundRect(325*mm,y*mm,69*mm,14*mm,2*mm,fill=1,stroke=1);c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica',7);c.drawCentredString(359.5*mm,(y+5.5)*mm,n);c.setStrokeColor(rl_colors.HexColor('#155eef'));c.line(378*mm,165*mm,359*mm,(y+14)*mm)
    c.setFillColor(rl_colors.HexColor('#eef3f7'));c.rect(145*mm,38*mm,150*mm,62*mm,fill=1,stroke=0);c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica-Bold',9);c.drawString(155*mm,88*mm,'CRITERIOS');c.setFont('Helvetica',8);c.drawString(155*mm,75*mm,'• Todo el control es local y de baja tensión.');c.drawString(155*mm,63*mm,'• No asignar GPIO no verificados (GPIO22 no existe).');c.drawString(155*mm,51*mm,'• No incluir sensor de viento inexistente.');c.drawString(155*mm,39*mm,'• MIC OFF conserva corte físico independiente.')
    c.showPage()

    # 5 · Hidráulico
    _pdf_header(c,5,'PL-04','PLANO HIDRÁULICO · RIEGO SEGURO','Depósito separado, lectura de nivel y bloqueo de bomba')
    cx=[(34,140,50,55,'DEPÓSITO\n92×92×100'),(126,152,52,30,'BOMBA 5 V'),(221,152,55,30,'COLECTOR'),(320,125,70,82,'BANCAL x2')]
    for x,y,w,h,label in cx:
        c.setFillColor(rl_colors.HexColor('#e2f5ff'));c.setStrokeColor(rl_colors.HexColor('#1c9ee8'));c.setLineWidth(2);c.roundRect(x*mm,y*mm,w*mm,h*mm,3*mm,fill=1,stroke=1);c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica-Bold',8)
        for j,line in enumerate(label.split('\n')):c.drawCentredString((x+w/2)*mm,(y+h/2-j*6)*mm,line)
    c.setStrokeColor(rl_colors.HexColor('#1c9ee8'));c.setLineWidth(5);c.line(84*mm,168*mm,126*mm,168*mm);c.line(178*mm,168*mm,221*mm,168*mm);c.line(276*mm,168*mm,320*mm,168*mm)
    c.setFillColor(rl_colors.HexColor('#23a36d'));c.circle(59*mm,186*mm,5*mm,fill=1,stroke=0);c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica-Bold',8);c.drawString(68*mm,184*mm,'SENSOR DE NIVEL')
    c.setFillColor(rl_colors.HexColor('#eef3f7'));c.rect(34*mm,35*mm,356*mm,66*mm,fill=1,stroke=0)
    c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica-Bold',10);c.drawString(48*mm,84*mm,'LÓGICA DE PROTECCIÓN');c.setFont('Helvetica',9);c.drawString(48*mm,69*mm,'1. Humedad < 30 % → solicitud de riego.');c.drawString(48*mm,56*mm,'2. Nivel bajo → bomba bloqueada y alarma local.');c.drawString(214*mm,69*mm,'3. Nivel suficiente → riego hasta 45 %.');c.drawString(214*mm,56*mm,'4. Tiempo máximo de bomba: 120 s.');c.setFillColor(rl_colors.HexColor('#b42318'));c.setFont('Helvetica-Bold',9);c.drawString(48*mm,42*mm,'Nunca ubicar agua o uniones de manguera sobre el gabinete electrónico.')
    c.showPage()

    # 6 · Explosión / montaje / corte
    _pdf_header(c,6,'PL-05','EXPLOSIÓN, MONTAJE Y CORTE','Secuencia de armado y criterios de tolerancia')
    img=ROOT/'project_domus_exploded.png'
    if img.exists():c.drawImage(str(img),18*mm,76*mm,width=225*mm,height=135*mm,preserveAspectRatio=True,anchor='c',mask='auto')
    c.setFillColor(rl_colors.HexColor('#eef3f7'));c.rect(255*mm,76*mm,146*mm,136*mm,fill=1,stroke=0);_pdf_label(c,267*mm,199*mm,'SECUENCIA')
    seq=['1 · Nivelar base 1000 × 650.','2 · Montar casa y tabiques.','3 · Armar porche e invernadero.','4 · Separar depósito y gabinete.','5 · Tender agua antes de energía.','6 · Cablear 5 V/GND y señales.','7 · Colocar techo/paneles removibles.','8 · Probar bloqueos antes de exhibir.']
    c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica',8);yy=180
    for n in seq:c.drawString(269*mm,yy*mm,n);yy-=13
    c.setFont('Helvetica-Bold',9);c.drawString(269*mm,84*mm,'TOLERANCIA INICIAL ±0.5 mm');c.setFont('Helvetica',7);c.drawString(269*mm,76*mm,'Presentar en seco antes de adhesivo definitivo.')
    c.setFillColor(rl_colors.white);c.setStrokeColor(rl_colors.HexColor('#9db0c2'));c.rect(18*mm,28*mm,383*mm,38*mm,fill=1,stroke=1)
    cols=[('BASE','1000×650×12','1'),('CASA','430×325','1 set'),('INVERNADERO','250×350×225','1'),('PORCHE','250×195×154','1'),('JARVIS','105×118×302','1'),('GABINETE','110×150×269','1')]
    for i,(a,b,q) in enumerate(cols):
        x=(25+i*62)*mm;c.setFillColor(rl_colors.HexColor('#155eef'));c.setFont('Helvetica-Bold',7);c.drawString(x,55*mm,a);c.setFillColor(rl_colors.HexColor('#10233f'));c.setFont('Helvetica',7);c.drawString(x,45*mm,b);c.drawString(x,36*mm,'Cant. '+q)
    c.save()
    (ROOT / 'plano_tecnico_domus.pdf').write_bytes(out.read_bytes())
    return out


def write_viewer_v3(parts: list[Part]) -> None:
    data=json.dumps([asdict(x) for x in parts],ensure_ascii=False,separators=(',',':'))
    colors=json.dumps({k:v[:3] for k,v in MATERIALS.items()},separators=(',',':'))
    tpl=r'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><title>PROJECT DOMUS · gemelo digital v3</title><style>
*{box-sizing:border-box} :root{--ink:#e9f2ff;--muted:#91a6bd;--panel:#0d192b;--panel2:#111f34;--line:#2a405c;--blue:#155eef;--cyan:#12b8d0;--work:#eef3f7;--dark:#08111f;font-family:Bahnschrift,"Arial Narrow","Segoe UI",sans-serif;color:var(--ink);background:var(--dark)}body{margin:0;height:100vh;overflow:hidden;background:var(--dark)}button,input{font:inherit}button{border:1px solid var(--line);background:#13243b;color:var(--ink);min-height:34px;padding:7px 10px;cursor:pointer;font-weight:650;letter-spacing:.02em}button:hover,button[aria-pressed=true]{background:#155eef;border-color:#5b8dff}button:focus-visible,input:focus-visible{outline:3px solid #12b8d0;outline-offset:2px}.app{height:100vh;display:grid;grid-template:58px 1fr 104px/286px 1fr 244px}.top{grid-column:1/-1;display:flex;align-items:center;padding:0 18px;background:#08111f;border-bottom:1px solid var(--line);gap:15px}.brand{font-weight:900;letter-spacing:.08em;font-size:18px}.version{font-size:11px;color:#12b8d0;letter-spacing:.12em}.status{margin-left:auto;display:flex;gap:8px}.pill{border:1px solid #2b9f91;color:#9dfff0;background:#0b2d2b;padding:5px 9px;font-size:11px}.left,.right{background:var(--panel);overflow:auto}.left{border-right:1px solid var(--line);padding:14px}.right{border-left:1px solid var(--line);padding:14px}.viewport{position:relative;overflow:hidden;background:var(--work)}canvas{width:100%;height:100%;display:block;touch-action:none}.section{margin-bottom:18px}.eyebrow{font-size:10px;letter-spacing:.14em;color:#79a8ff;font-weight:800;margin-bottom:8px}.views{display:grid;grid-template-columns:1fr 1fr;gap:6px}.views button{font-size:11px;text-align:left}.views .wide{grid-column:1/-1}.layer-tools{display:flex;gap:5px;margin-bottom:9px;flex-wrap:wrap}.layer-tools button{font-size:10px;padding:4px 7px;min-height:30px}.layers{display:grid;gap:4px}.layer{display:flex;align-items:center;gap:10px;min-height:42px;padding:7px 8px;font-size:11px;border:1px solid transparent;background:#0a1525;cursor:pointer}.layer:hover{border-color:#3d5878;background:#12233a}.swatch{width:12px;height:12px;border-radius:1px;flex:0 0 12px}.layer input{accent-color:#155eef;width:20px;height:20px;flex:0 0 20px}.search{width:100%;background:#08111f;border:1px solid var(--line);color:white;padding:9px;margin-bottom:8px}.legend{display:grid;gap:8px;font-size:11px}.legend span{display:flex;align-items:center;gap:9px}.line{height:4px;width:30px}.work-label{position:absolute;left:18px;top:16px;color:#10233f;background:rgba(255,255,255,.86);border-left:4px solid #155eef;padding:8px 11px;pointer-events:none}.work-label b{display:block;font-size:13px}.work-label small{font-size:10px;color:#50657a}.compass{position:absolute;right:18px;top:18px;color:#10233f;text-align:center;font-size:10px;font-weight:bold}.north{font-size:25px;color:#155eef}.scale{position:absolute;right:18px;bottom:18px;color:#10233f;font-size:9px}.scale i{display:block;width:110px;height:7px;border:1px solid #10233f;background:linear-gradient(90deg,#10233f 0 50%,#fff 50%)}.hint{position:absolute;left:18px;bottom:18px;color:#10233f;font-size:10px;background:rgba(255,255,255,.8);padding:6px 8px}.right h2{font-size:15px;margin:0 0 5px}.right p{font-size:11px;line-height:1.45;color:var(--muted)}.metric{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin:12px 0}.metric div{background:#08111f;border:1px solid var(--line);padding:8px}.metric b{font-size:15px;display:block}.metric small{color:var(--muted);font-size:9px}.inspector{grid-column:1/-1;background:#08111f;border-top:1px solid var(--line);display:grid;grid-template-columns:286px 1fr 244px;align-items:center}.inspector-toggle{display:none}.select{padding:12px 18px}.select b{display:block;font-size:14px}.select small{color:var(--muted);font-size:10px}.dims{display:flex;gap:28px;padding:0 24px;border-left:1px solid var(--line);border-right:1px solid var(--line)}.dims div{font-size:10px;color:var(--muted)}.dims strong{display:block;color:white;font-size:14px}.coords{padding:10px 18px;font-size:10px;color:var(--muted)}.systems-active .viewport{box-shadow:inset 0 0 0 4px #12b8d0}.mobile-toggle{display:none}.night canvas{filter:brightness(.72) saturate(1.2)}
@media(max-width:920px){body{overflow:auto;padding-bottom:50px}body.inspector-open{padding-bottom:92px}.app{height:auto;min-height:100vh;grid-template:58px 58vh auto auto/1fr}.top{position:sticky;top:0;z-index:10;padding:0 10px}.status .pill:nth-child(2){display:none}.left{grid-row:3;border:0;padding:12px}.right{grid-row:4;border:0}.viewport{grid-row:2}.inspector{position:fixed;z-index:20;left:0;right:0;bottom:0;display:grid;grid-template-columns:minmax(175px,1fr) auto;height:44px;background:#08111f;border-top:2px solid #2a405c;box-shadow:0 -5px 18px rgba(0,0,0,.24);transition:height .18s ease}.inspector.open{height:82px;border-top:3px solid #12b8d0;box-shadow:0 -10px 28px rgba(0,0,0,.38)}.inspector-toggle{display:block;position:absolute;right:8px;top:3px;min-height:36px;background:#155eef;border-color:#79a8ff;padding:6px 11px}.inspector.open .inspector-toggle{left:8px;right:auto;top:7px;min-height:30px;padding:5px 8px}.inspector:not(.open) .select,.inspector:not(.open) .dims{display:none}.inspector.open .select{padding-left:82px}.select{padding:10px 12px;min-width:0}.select b,.select small{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.dims{border:0;padding:8px 10px;gap:9px;flex-wrap:nowrap}.dims div:nth-child(4){display:none}.dims strong{font-size:11px}.coords{display:none}.views{grid-template-columns:repeat(4,1fr)}.views button{font-size:10px;padding:6px}.views .wide{grid-column:auto}.layers{grid-template-columns:1fr 1fr;margin-bottom:12px}.layer{min-height:44px}.hint{display:none}.work-label{top:8px;left:8px}.compass{top:8px;right:10px}.scale{bottom:8px;right:10px}}
@media(max-width:430px){.brand{font-size:14px}.version{display:none}.top{gap:7px}.pill{font-size:9px;padding:4px 6px}.viewport{height:52vh}.app{grid-template-rows:52px 52vh auto auto auto}.views{grid-template-columns:repeat(2,1fr)}.layer-tools{flex-wrap:wrap}.right{padding-bottom:24px}}
</style></head><body><main class="app" id="app"><header class="top"><div><div class="brand">PROJECT DOMUS</div><div class="version">GEMELO DIGITAL v3</div></div><div class="status"><span class="pill">● 100 % LOCAL</span><span class="pill">5 V DC · SIN RADIO</span><span class="pill" id="count">0 PIEZAS</span></div></header>
<aside class="left"><section class="section"><div class="eyebrow">01 / VISTAS</div><div class="views" id="views"><button data-view="presentation" aria-pressed="true">Presentación</button><button data-view="front">Frontal</button><button data-view="top">Superior</button><button data-view="inside">Interior</button><button data-view="systems" class="wide">Radiografía sistemas</button><button data-view="water">Agua / riego</button><button data-view="electric">Electricidad</button><button data-view="exploded">Explotada</button></div></section><section class="section"><div class="eyebrow">02 / CAPAS</div><div class="layer-tools"><button id="all">Mostrar todo</button><button id="isolate">Aislar</button><button id="structure">Ocultar estructura</button><button id="labels" aria-pressed="true">Etiquetas</button></div><input class="search" id="search" placeholder="Buscar pieza…" aria-label="Buscar pieza"><div class="layers" id="layers"></div></section></aside>
<section class="viewport" id="viewport"><canvas id="c" aria-label="Modelo 3D interactivo de Project Domus"></canvas><div class="work-label"><b id="modeLabel">PRESENTACIÓN / ISOMÉTRICA</b><small>Arrastra · rueda/pellizca · toca una pieza</small></div><div class="compass"><div class="north">↑</div>N / FRENTE</div><div class="scale"><i></i>0 — 100 — 200 mm</div><div class="hint">Atajos: 1 presentación · 2 superior · 3 radiografía · R restablecer</div></section>
<aside class="right"><section class="section"><div class="eyebrow">03 / LEYENDA</div><div class="legend"><span><i class="line" style="background:#ef4444"></i>Energía 5 V</span><span><i class="line" style="background:#f59e0b"></i>Señal lógica</span><span><i class="line" style="background:#1c9ee8"></i>Agua / riego</span><span><i class="line" style="background:#23a36d"></i>Sensores / cultivo</span><span><i class="line" style="background:#c58a4a"></i>Estructura</span><span><i class="line" style="background:#bfc8d2"></i>Removible</span></div></section><section class="section"><div class="eyebrow">04 / SISTEMA</div><h2>Arquitectura física local</h2><p>Agua y electrónica permanecen en extremos opuestos. El canal técnico inferior reúne alimentación y señal sin ocultar su recorrido didáctico.</p><div class="metric"><div><b>1000 × 650</b><small>BASE / MM</small></div><div><b>5 V DC</b><small>BAJA TENSIÓN</small></div><div><b>120 s</b><small>MÁX. BOMBA</small></div><div><b>30 → 45 %</b><small>RIEGO</small></div></div><button id="theme">Contraste día / noche</button><button id="reset">Restablecer</button></section></aside>
<footer class="inspector" id="inspector"><button class="inspector-toggle" id="inspectorToggle" aria-expanded="false" aria-controls="inspector">Ficha técnica ▲</button><div class="select"><b id="partName">Ninguna pieza seleccionada</b><small id="partNote">Toca el modelo o busca una pieza para inspeccionarla.</small></div><div class="dims"><div>ANCHO<strong id="dw">—</strong></div><div>FONDO<strong id="dd">—</strong></div><div>ALTO<strong id="dh">—</strong></div><div>CAPA<strong id="dl">—</strong></div></div><div class="coords" id="coords">X — · Y — · Z —</div></footer></main>
<script>const parts=__PARTS__,colors=__COLORS__;const labels={base:'Base',systems:'Canal',house:'Casa',roof:'Techo',furniture:'Mobiliario',bath:'Baño',solar:'Solar',porch:'Porche',landscape:'Jardín',sensors:'Sensores',water:'Agua',greenhouse:'Invernadero',plants:'Cultivo',jarvis:'Jarvis',electronics:'Gabinete',boards:'Placas',lights:'Luces',power:'Energía',signal:'Señal',removable:'Removibles'};const order=['house','roof','furniture','greenhouse','plants','water','power','signal','sensors','solar','porch','jarvis','electronics','boards','lights','removable','base','systems','bath','landscape'];const visible=Object.fromEntries(order.map(x=>[x,true]));let rot=-35,elev=29,zoom=.92,explode=0,alphaStructure=1,selected=null,drag=false,moved=false,lastX=0,lastY=0,centers=[],showLabels=true;const c=document.querySelector('#c'),ctx=c.getContext('2d'),layers=document.querySelector('#layers');
const layerColor={house:'#c58a4a',roof:'#6f7e90',furniture:'#d6a15c',greenhouse:'#23a36d',plants:'#23a36d',water:'#1c9ee8',power:'#ef4444',signal:'#f59e0b',sensors:'#f1c40f',solar:'#155eef',porch:'#a8753d',jarvis:'#155eef',electronics:'#718197',boards:'#23a36d',lights:'#12b8d0',removable:'#c5ced7',base:'#303d50',systems:'#155eef',bath:'#12b8d0',landscape:'#23a36d'};
function makeLayers(){layers.innerHTML='';order.filter(l=>parts.some(p=>p.layer===l)).forEach(layer=>{const label=document.createElement('label');label.className='layer';label.innerHTML=`<input type="checkbox" data-layer="${layer}" ${visible[layer]?'checked':''}><i class="swatch" style="background:${layerColor[layer]||'#fff'}"></i>${labels[layer]||layer}`;label.querySelector('input').onchange=e=>{visible[layer]=e.target.checked;if(selected&&!visible[selected.layer])selectPart(null);draw()};layers.append(label)})}makeLayers();
function setInspectorOpen(open){const panel=document.querySelector('#inspector'),button=document.querySelector('#inspectorToggle');panel.classList.toggle('open',open);document.body.classList.toggle('inspector-open',open);button.setAttribute('aria-expanded',open);button.textContent=open?'Cerrar ×':'Ficha técnica ▲'}document.querySelector('#inspectorToggle').onclick=()=>setInspectorOpen(!document.querySelector('#inspector').classList.contains('open'));
function sync(){layers.querySelectorAll('input').forEach(i=>i.checked=visible[i.dataset.layer]);document.querySelector('#count').textContent=parts.filter(p=>visible[p.layer]).length+' PIEZAS'}function size(){const d=devicePixelRatio||1,r=c.getBoundingClientRect();c.width=Math.max(1,r.width*d);c.height=Math.max(1,r.height*d);ctx.setTransform(d,0,0,d,0,0);draw()}
function offset(p){let x=p.x,y=p.y,z=p.z;if(explode){if(p.layer==='roof')z+=100*explode;if(p.layer==='solar')z+=155*explode;if(['electronics','boards','removable'].includes(p.layer))x+=58*explode;if(['greenhouse','plants'].includes(p.layer))x-=35*explode}return{x,y,z}}
function vertices(p){const o=offset(p),x=o.x,y=o.y,z=o.z,w=p.w,d=p.d,h=p.h,cx=x+w/2,cy=y+d/2,cz=z+h/2;let vs=[[x,y,z],[x+w,y,z],[x+w,y+d,z],[x,y+d,z],[x,y,z+h],[x+w,y,z+h],[x+w,y+d,z+h],[x,y+d,z+h]],rx=(p.rx||0)*Math.PI/180,ry=(p.ry||0)*Math.PI/180,rz=(p.rz||0)*Math.PI/180;return vs.map(v=>{let X=v[0]-cx,Y=v[1]-cy,Z=v[2]-cz,q=Y*Math.cos(rx)-Z*Math.sin(rx);Z=Y*Math.sin(rx)+Z*Math.cos(rx);Y=q;q=X*Math.cos(ry)+Z*Math.sin(ry);Z=-X*Math.sin(ry)+Z*Math.cos(ry);X=q;q=X*Math.cos(rz)-Y*Math.sin(rz);Y=X*Math.sin(rz)+Y*Math.cos(rz);X=q;return[X+cx,Y+cy,Z+cz]})}
function project(v){const a=rot*Math.PI/180,e=elev*Math.PI/180,x=v[0]-500,y=v[1]-325,z=v[2]-130,xr=x*Math.cos(a)-y*Math.sin(a),yr=x*Math.sin(a)+y*Math.cos(a),yy=yr*Math.sin(e)-z*Math.cos(e),depth=yr*Math.cos(e)+z*Math.sin(e),s=Math.min(c.clientWidth/1050,c.clientHeight/650)*zoom;return[c.clientWidth/2+xr*s,c.clientHeight/2+yy*s,depth]}
const faces=[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[4,0,3,7]];function grid(){ctx.save();ctx.strokeStyle='rgba(70,99,126,.16)';ctx.lineWidth=1;for(let x=0;x<c.clientWidth;x+=28){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,c.clientHeight);ctx.stroke()}for(let y=0;y<c.clientHeight;y+=28){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(c.clientWidth,y);ctx.stroke()}ctx.restore()}
function draw(){ctx.clearRect(0,0,c.clientWidth,c.clientHeight);ctx.fillStyle='#eef3f7';ctx.fillRect(0,0,c.clientWidth,c.clientHeight);grid();let polys=[];centers=[];parts.filter(p=>visible[p.layer]).forEach(p=>{let vv=vertices(p).map(project);faces.forEach((f,fi)=>{let pts=f.map(i=>vv[i]);polys.push({pts,depth:pts.reduce((s,q)=>s+q[2],0)/4,p,fi})});let o=offset(p),cc=project([o.x+p.w/2,o.y+p.d/2,o.z+p.h/2]);centers.push({x:cc[0],y:cc[1],p})});polys.sort((a,b)=>a.depth-b.depth);polys.forEach(o=>{let rgb=colors[o.p.material]||[.5,.5,.5],shade=.7+o.fi*.035,struct=['house','roof','furniture','base','porch','greenhouse'].includes(o.p.layer),alpha=o.p.material==='glass'||o.p.material==='acrylic'?.22:(struct?alphaStructure:.97);ctx.beginPath();o.pts.forEach((q,i)=>i?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]));ctx.closePath();ctx.fillStyle=`rgba(${rgb.map(v=>Math.round(v*255*shade)).join(',')},${alpha})`;ctx.fill();ctx.strokeStyle=selected===o.p?'#12b8d0':'rgba(8,17,31,.42)';ctx.lineWidth=selected===o.p?2:.55;ctx.stroke()});if(showLabels&&['systems','water','electric'].includes(currentView))drawLabels();sync()}
function drawLabels(){let wanted=currentView==='water'?['water','sensors']:currentView==='electric'?['power','signal','boards','electronics','sensors']:['water','power','signal','sensors'],mobile=c.clientWidth<600,limit=mobile?6:12,placed=[];const short={'Sensor nivel depósito':'Nivel depósito','Manguera depósito-bomba':'Depósito → bomba','Manguera principal riego':'Riego principal','Sensor humedad suelo':'Humedad suelo','Bus 5V canal técnico':'Bus 5 V','Bus GND canal técnico':'Bus GND','Línea de riego izquierda':'Riego izq.','Línea de riego derecha':'Riego der.'};ctx.save();ctx.font=`700 ${mobile?9:10}px Bahnschrift,Segoe UI`;let candidates=centers.filter(o=>wanted.includes(o.p.layer)&&(/Sensor|Bus|Bomba|ESP32|relé|Manguera|Línea/.test(o.p.name))).sort((a,b)=>(/Sensor|Bus|Bomba/.test(b.p.name)?1:0)-(/Sensor|Bus|Bomba/.test(a.p.name)?1:0)).slice(0,limit);candidates.forEach((o,i)=>{let text=mobile?(short[o.p.name]||o.p.name.replace('Sensor ','').slice(0,20)):o.p.name,tw=Math.min(c.clientWidth-20,ctx.measureText(text).width+10),tx=o.x+(i%2?24:-tw-24),ty=o.y-18-(i%3)*7;tx=Math.max(8,Math.min(c.clientWidth-tw-8,tx));ty=Math.max(22,Math.min(c.clientHeight-10,ty));for(let tries=0;tries<7&&placed.some(r=>Math.abs(r.x-tx)<Math.max(r.w,tw)&&Math.abs(r.y-ty)<19);tries++){ty+=20;if(ty>c.clientHeight-10)ty=22+tries*18}placed.push({x:tx,y:ty,w:tw});ctx.strokeStyle=layerColor[o.p.layer]||'#155eef';ctx.beginPath();ctx.moveTo(Math.max(4,Math.min(c.clientWidth-4,o.x)),Math.max(4,Math.min(c.clientHeight-4,o.y)));ctx.lineTo(tx,ty-5);ctx.stroke();ctx.fillStyle='#08111f';ctx.fillRect(tx,ty-14,tw,17);ctx.fillStyle='#fff';ctx.fillText(text,tx+5,ty-2)});ctx.restore()}
function selectPart(p){selected=p;document.querySelector('#partName').textContent=p?p.name:'Ninguna pieza seleccionada';document.querySelector('#partNote').textContent=p?(p.note||'Pieza documentada en el inventario geométrico.'):'Toca el modelo o busca una pieza para inspeccionarla.';document.querySelector('#dw').textContent=p?p.w+' mm':'—';document.querySelector('#dd').textContent=p?p.d+' mm':'—';document.querySelector('#dh').textContent=p?p.h+' mm':'—';document.querySelector('#dl').textContent=p?(labels[p.layer]||p.layer):'—';document.querySelector('#coords').textContent=p?`X ${p.x} · Y ${p.y} · Z ${p.z}`:'X — · Y — · Z —';if(innerWidth<=920)setInspectorOpen(Boolean(p));draw()}
let currentView='presentation';const presets={presentation:[-35,29,.92,0,1],front:[0,16,1.02,0,1],top:[0,78,.86,0,1],inside:[-20,33,1.02,0,1],systems:[-35,30,.98,0,.18],water:[-48,31,1.02,0,.14],electric:[-18,26,1.14,0,.12],exploded:[-35,28,.78,1,1]},modeNames={presentation:'PRESENTACIÓN / ISOMÉTRICA',front:'FRONTAL',top:'SUPERIOR',inside:'INTERIOR SIN TECHO',systems:'RADIOGRAFÍA / AGUA · ENERGÍA · SEÑAL',water:'AGUA / RIEGO',electric:'ELECTRICIDAD / GABINETE',exploded:'VISTA EXPLOTADA'};function setView(name){currentView=name;let v=presets[name];[rot,elev,zoom,explode,alphaStructure]=v;Object.keys(visible).forEach(x=>visible[x]=true);if(name==='inside'){visible.roof=false;visible.solar=false}if(name==='water')Object.keys(visible).forEach(x=>visible[x]=['base','water','sensors','greenhouse','plants'].includes(x));if(name==='electric')Object.keys(visible).forEach(x=>visible[x]=['base','electronics','boards','power','signal','sensors','lights','jarvis'].includes(x));if(selected&&!visible[selected.layer])selectPart(null);document.body.classList.toggle('systems-active',name==='systems');document.querySelector('#modeLabel').textContent=modeNames[name];document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.view===name));sync();draw()}
document.querySelector('#views').onclick=e=>{let b=e.target.closest('[data-view]');if(b)setView(b.dataset.view)};document.querySelector('#all').onclick=()=>{Object.keys(visible).forEach(x=>visible[x]=true);sync();draw()};document.querySelector('#structure').onclick=()=>{['house','roof','furniture','porch','base'].forEach(x=>visible[x]=false);if(selected&&!visible[selected.layer])selectPart(null);sync();draw()};document.querySelector('#isolate').onclick=()=>{if(!selected)return;Object.keys(visible).forEach(x=>visible[x]=x===selected.layer);sync();draw()};document.querySelector('#labels').onclick=e=>{showLabels=!showLabels;e.currentTarget.setAttribute('aria-pressed',showLabels);draw()};document.querySelector('#reset').onclick=()=>setView('presentation');document.querySelector('#theme').onclick=()=>document.body.classList.toggle('night');document.querySelector('#search').oninput=e=>{let q=e.target.value.toLowerCase().trim();if(q){let p=parts.find(x=>x.name.toLowerCase().includes(q));if(p){visible[p.layer]=true;selectPart(p);sync()}}};
c.onpointerdown=e=>{drag=true;moved=false;lastX=e.clientX;lastY=e.clientY;c.setPointerCapture(e.pointerId)};c.onpointermove=e=>{if(!drag)return;let dx=e.clientX-lastX,dy=e.clientY-lastY;if(Math.abs(dx)+Math.abs(dy)>2)moved=true;rot+=dx*.35;elev=Math.max(8,Math.min(80,elev-dy*.25));lastX=e.clientX;lastY=e.clientY;draw()};c.onpointerup=e=>{drag=false;if(moved)return;let r=c.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top,best=null,d=34;centers.forEach(o=>{let nd=Math.hypot(o.x-x,o.y-y);if(nd<d){best=o.p;d=nd}});if(best)selectPart(best)};c.onwheel=e=>{e.preventDefault();zoom=Math.max(.42,Math.min(1.65,zoom-e.deltaY*.0008));draw()};addEventListener('keydown',e=>{if(e.key==='1')setView('presentation');if(e.key==='2')setView('top');if(e.key==='3')setView('systems');if(e.key.toLowerCase()==='r')setView('presentation')});addEventListener('resize',size);size();</script></body></html>'''
    (ROOT/'modelo_3d_interactivo.html').write_text(tpl.replace('__PARTS__',data).replace('__COLORS__',colors),encoding='utf-8')


def main() -> None:
    parts = enhance_parts(build_parts())
    write_obj(parts)
    write_svg_v3()
    write_parts_csv(parts)
    render_png(parts)
    Image.open(ROOT / 'project_domus_render.png').save(ROOT / 'plano_tecnico_domus_preview.png')
    write_viewer_v3(parts)
    pdf_path = write_pdf_v3()
    print(f"Generados {len(parts)} elementos del modelo en {ROOT}")
    print(f"PDF técnico: {pdf_path}")


if __name__ == "__main__":
    main()
