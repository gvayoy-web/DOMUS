"""Genera el manual visual final de montaje y pruebas de PROJECT DOMUS."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
    Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "DOMUS_Manual_Test_Diagrama_Final.pdf"

NAVY = colors.HexColor("#11324D")
BLUE = colors.HexColor("#236B8E")
CYAN = colors.HexColor("#DFF4F7")
GREEN = colors.HexColor("#DDF2E3")
AMBER = colors.HexColor("#FFF0C2")
RED = colors.HexColor("#B3261E")
INK = colors.HexColor("#18242D")
GRAY = colors.HexColor("#53636D")
WIRE = {
    "power": colors.HexColor("#D64545"),
    "ground": colors.HexColor("#252B31"),
    "signal": colors.HexColor("#247BA0"),
    "i2c": colors.HexColor("#8E5CB7"),
    "motor": colors.HexColor("#E08B2D"),
}


def para(text, style):
    return Paragraph(text, style)


def make_table(data, widths, font=7.6, header=True):
    cell = ParagraphStyle("cell", fontName="Helvetica", fontSize=font,
                          leading=font + 2, textColor=INK)
    head = ParagraphStyle("head", parent=cell, fontName="Helvetica-Bold",
                          textColor=colors.white)
    rows = []
    for ri, row in enumerate(data):
        st = head if header and ri == 0 else cell
        rows.append([v if isinstance(v, Flowable) else Paragraph(escape(str(v)), st)
                     for v in row])
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#B7C3CA")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), NAVY),
                     ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
    for ri in range(1 if header else 0, len(rows)):
        if ri % 2 == 0:
            commands.append(("BACKGROUND", (0, ri), (-1, ri), colors.HexColor("#F2F6F7")))
    t.setStyle(TableStyle(commands))
    return t


class WiringMap(Flowable):
    """Diagrama vectorial de rutas, legible al imprimir."""
    def __init__(self, title, left, right, links, width=240*mm, height=118*mm):
        super().__init__()
        self.title, self.left, self.right, self.links = title, left, right, links
        self.width, self.height = width, height

    def draw(self):
        c = self.canv
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(NAVY)
        c.drawString(0, self.height - 10, self.title)
        top = self.height - 28
        box_w = 65*mm
        right_x = self.width - box_w
        row_h = min(13*mm, (self.height-35) / max(len(self.left), len(self.right), 1))

        def node(x, y, label, fill):
            c.setFillColor(fill)
            c.setStrokeColor(colors.HexColor("#8296A3"))
            c.roundRect(x, y-row_h+2, box_w, row_h-4, 3*mm, fill=1, stroke=1)
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 7.5)
            c.drawCentredString(x+box_w/2, y-row_h/2, label[:38])

        lp, rp = {}, {}
        for i, name in enumerate(self.left):
            y = top-i*row_h
            node(0, y, name, CYAN)
            lp[name] = (box_w, y-row_h/2)
        for i, name in enumerate(self.right):
            y = top-i*row_h
            node(right_x, y, name, colors.HexColor("#F4EAD7"))
            rp[name] = (right_x, y-row_h/2)
        for i, (a, b, kind, label) in enumerate(self.links):
            if a not in lp or b not in rp:
                continue
            x1, y1 = lp[a]; x2, y2 = rp[b]
            offset = ((i % 5)-2)*1.2*mm
            c.setStrokeColor(WIRE.get(kind, WIRE["signal"]))
            c.setLineWidth(1.6)
            c.line(x1, y1+offset, x2, y2+offset)
            c.setFillColor(WIRE.get(kind, WIRE["signal"]))
            c.circle(x2, y2+offset, 1.2*mm, fill=1, stroke=0)
            if label:
                c.setFont("Helvetica", 6.2)
                c.setFillColor(GRAY)
                c.drawCentredString((x1+x2)/2, (y1+y2)/2+offset+1.8*mm, label[:44])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#CBD5DA"))
    canvas.line(15*mm, 11*mm, 264*mm, 11*mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GRAY)
    canvas.drawString(15*mm, 6.5*mm, "PROJECT DOMUS - Montaje final de baja tension - ESP32-S3 N16R8")
    canvas.drawRightString(264*mm, 6.5*mm, f"Pagina {doc.page}")
    canvas.restoreState()


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], fontName="Helvetica-Bold",
                           fontSize=23, leading=26, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=10.5, leading=14,
                         textColor=GRAY, alignment=TA_CENTER, spaceAfter=12)
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontName="Helvetica-Bold",
                        fontSize=15, leading=18, textColor=NAVY, spaceBefore=4, spaceAfter=7)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName="Helvetica-Bold",
                        fontSize=11, leading=14, textColor=BLUE, spaceBefore=6, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=8.8,
                          leading=11.5, textColor=INK, spaceAfter=5)
    small = ParagraphStyle("small", parent=body, fontSize=7.4, leading=9.4)
    warn = ParagraphStyle("warn", parent=body, fontName="Helvetica-Bold", textColor=RED,
                          backColor=colors.HexColor("#FCE8E6"), borderColor=RED,
                          borderWidth=.7, borderPadding=6, spaceAfter=7)
    ok = ParagraphStyle("ok", parent=body, fontName="Helvetica-Bold", textColor=NAVY,
                        backColor=GREEN, borderColor=BLUE, borderWidth=.7,
                        borderPadding=6, spaceAfter=7)
    mono = ParagraphStyle("mono", parent=body, fontName="Courier", fontSize=7.1,
                          leading=9.2, backColor=colors.HexColor("#EEF3F5"), borderPadding=5)

    story = [
        Spacer(1, 10*mm), para("PROJECT DOMUS", title),
        para("Manual visual de montaje final y pruebas", title),
        para("ESP32-S3 N16R8 - fuente 5 V/5 A - DRV8833 - control infrarrojo Jarvis", sub),
        para("DECISION VIGENTE: no se compran reles ni luz UV. El DRV8833 controla bomba y ventilador. Dos LED azules y uno rojo representan iluminacion suplementaria. El control CAR MP3 y el receptor HX1838 accionan Jarvis; las respuestas salen en espanol por MAX98357A.", ok),
        para("NO ENERGIZAR EL MONTAJE COMPLETO DE UNA VEZ. Cada pagina indica una rama. Probar fuente, sensores, motores, luces, control IR y audio por separado antes de unirlos.", warn),
        para("Contenido", h1),
        make_table([
            ["Pagina", "Sistema", "Objetivo"],
            ["2", "Energia", "Fuente, fusible, switch, buses y condensadores"],
            ["3", "Sensores", "DHT11, suelo, nivel, LDR y PIR"],
            ["4", "Actuadores", "DRV8833, bomba, ventilador y LED de cultivo"],
            ["5", "Jarvis y controles", "HX1838, control CAR MP3, botones y buzzers"],
            ["6", "Audio", "INMP441 opcional, MAX98357A y parlante"],
            ["7", "GPIO", "Asignacion final y diferencias con firmware de banco"],
            ["8-9", "Pruebas", "Secuencia, fallas y criterios de aprobacion"],
        ], [25*mm, 65*mm, 150*mm]),
        PageBreak(),
        para("1. Diagrama de energia", h1),
        WiringMap("Una fuente, dos buses, retorno en estrella",
                  ["Fuente cerrada 5 V/5 A", "ESP32 salida 3V3"],
                  ["Fusible 4 A -> switch -> BUS +5 V", "BUS GND", "BUS 3V3"],
                  [("Fuente cerrada 5 V/5 A", "Fusible 4 A -> switch -> BUS +5 V", "power", "+5 V protegido"),
                   ("Fuente cerrada 5 V/5 A", "BUS GND", "ground", "GND"),
                   ("ESP32 salida 3V3", "BUS 3V3", "power", "3.3 V")], height=98*mm),
        make_table([
            ["Desde", "Hacia", "Regla"],
            ["Fuente +5 V", "fusible 4 A -> switch -> BUS +5 V", "Centro del jack positivo; medir antes"],
            ["Fuente GND", "BUS GND", "Todos los modulos comparten esta referencia"],
            ["BUS +5 V", "ESP32 VIN/5V, DRV8833 VM, MAX98357A VIN, LED", "No entra a GPIO"],
            ["ESP32 3V3", "LCD, DHT11, suelo, nivel, LDR, HX1838, INMP441", "Solo cargas logicas pequenas"],
            ["1000 uF", "DRV8833 VM-GND y MAX98357A VIN-GND", "Franja del capacitor a GND"],
            ["100 nF", "cerca de receptores/sensores", "Sin polaridad"],
        ], [45*mm, 95*mm, 100*mm]),
        para("No conectar simultaneamente el +5 V del USB del PC y el +5 V de la fuente externa. Para programar con la casa alimentada, aislar una ruta positiva o desconectar la fuente; GND comun si se requiere comunicacion.", warn),
        PageBreak(),
        para("2. Diagrama de sensores", h1),
        WiringMap("Mapa de senales de sensores hacia el ESP32",
                  ["GPIO1", "GPIO2", "GPIO3", "GPIO9", "GPIO14"],
                  ["Suelo VCC/GND/AO", "Nivel VCC/GND/S", "LDR + 10 kOhm", "PIR VCC/GND/OUT", "DHT11"],
                  [("GPIO1", "Suelo VCC/GND/AO", "signal", "AO"),
                   ("GPIO2", "Nivel VCC/GND/S", "signal", "S/OUT"),
                   ("GPIO3", "LDR + 10 kOhm", "signal", "punto medio"),
                   ("GPIO9", "PIR VCC/GND/OUT", "signal", "OUT <=3.3 V"),
                   ("GPIO14", "DHT11", "signal", "DATA + pull-up 10k")], height=100*mm),
        make_table([
            ["Sensor", "Conexion exacta", "Prueba"],
            ["Suelo", "VCC=3V3, GND, AO=GPIO1; DO libre", "Registrar seco y humedo"],
            ["Nivel", "VCC=3V3, GND, S=GPIO2", "Registrar vacio, minimo y lleno"],
            ["LDR", "3V3-LDR-nodo-GPIO3-10k-GND", "Tapar/iluminar; confirmar sentido"],
            ["PIR", "VCC segun HX/HC real, GND, OUT=GPIO9", "OUT debe ser <=3.3 V"],
            ["DHT11", "VCC=3V3, DATA=GPIO14, NC libre, GND; 10k DATA-3V3", "Lectura cada >2 s"],
        ], [38*mm, 125*mm, 77*mm]),
        para("Mojar solo la zona sensible. Mantener conectores, baquelita, fuente y ESP32 elevados y separados del deposito.", warn),
        PageBreak(),
        para("3. Diagrama de actuadores", h1),
        WiringMap("Motores por DRV8833 y cultivo por S8050",
                  ["BUS +5 V", "BUS GND", "3V3", "GPIO4", "GPIO7", "GPIO8"],
                  ["DRV: AIN1 -> bomba AOUT1/AOUT2", "DRV: BIN1 -> ventilador BOUT1/BOUT2", "S8050 B/E/C", "2 azul + 1 rojo"],
                  [("BUS +5 V", "DRV: AIN1 -> bomba AOUT1/AOUT2", "power", "VM; GND comun"),
                   ("3V3", "DRV: BIN1 -> ventilador BOUT1/BOUT2", "power", "SLEEP HIGH"),
                   ("GPIO4", "DRV: AIN1 -> bomba AOUT1/AOUT2", "motor", "AIN2=GND"),
                   ("GPIO7", "DRV: BIN1 -> ventilador BOUT1/BOUT2", "motor", "BIN2=GND"),
                   ("GPIO8", "S8050 B/E/C", "signal", "1k a base"),
                   ("S8050 B/E/C", "2 azul + 1 rojo", "signal", "colector a catodos")], height=96*mm),
        make_table([
            ["Elemento", "Cableado", "Proteccion"],
            ["DRV8833", "VM=5V, GND comun, SLEEP=3V3", "1000 uF entre VM/GND"],
            ["Bomba", "entre AOUT1 y AOUT2; GPIO4->AIN1; AIN2->GND", "Nivel y timeout; nunca en seco"],
            ["Ventilador", "entre BOUT1 y BOUT2; GPIO7->BIN1; BIN2->GND", "Medir arranque y temperatura"],
            ["Cultivo", "+5V->330 ohm->anodo de cada LED; catodos->colector", "Una resistencia por LED"],
            ["S8050 Q1", "GPIO8->1k->B; B->10k->GND; E->GND; C->LED", "Confirmar E/B/C del lote"],
            ["1N4007", "No se coloca sobre AOUT/BOUT del DRV8833", "El puente H ya controla la inductancia"],
            ["Rele suelto", "Fuera del montaje final", "Si se demuestra aparte: 1N4007 sobre bobina"],
        ], [38*mm, 133*mm, 69*mm]),
        para("Sin TA6586: el DRV8833 sigue siendo compra necesaria. Probar la corriente de bomba y ventilador antes de aprobar la placa concreta.", ok),
        PageBreak(),
        para("4. Jarvis por control infrarrojo, botones y buzzers", h1),
        WiringMap("Entradas deterministas y avisos sonoros",
                  ["ESP32 3V3", "ESP32 GND", "GPIO10", "GPIO11", "GPIO12", "GPIO38", "GPIO39", "GPIO40", "GPIO41", "GPIO42"],
                  ["HX1838 +/ - /S", "STOP", "Silencio", "Boton sala", "Boton riego", "Boton ventilador", "S8050 Q2 + buzzer activo", "Buzzer pasivo"],
                  [("GPIO12", "HX1838 +/ - /S", "signal", "S/OUT 38 kHz"),
                   ("GPIO10", "STOP", "ground", "pulsado a GND"),
                   ("GPIO11", "Silencio", "ground", "pulsado a GND"),
                   ("GPIO38", "Boton sala", "ground", "INPUT_PULLUP"),
                   ("GPIO39", "Boton riego", "ground", "INPUT_PULLUP"),
                   ("GPIO40", "Boton ventilador", "ground", "INPUT_PULLUP"),
                   ("GPIO41", "S8050 Q2 + buzzer activo", "signal", "1k a base"),
                   ("GPIO42", "Buzzer pasivo", "signal", "100 ohm; solo si medido")], height=92*mm),
        make_table([
            ["Control", "Funcion"],
            ["IR 1/2/3", "sala / dormitorio / cultivo"],
            ["IR 4/5", "ventilador / solicitud de riego"],
            ["IR 6/7/8/9", "temperatura / humedad / suelo-nivel / estado"],
            ["IR 0", "apagar cargas"],
            ["IR CH-/CH+", "manual / automatico"],
            ["IR VOL-/VOL+", "volumen de Jarvis"],
            ["IR 100+/200+", "silencio / rearme"],
        ], [55*mm, 185*mm]),
        make_table([
            ["Elemento", "Conexion", "Precaucion"],
            ["HX1838", "3V3 / GND / OUT->GPIO12", "100 nF; aprender codigos reales"],
            ["Buzzer activo", "+5V->+; -->colector Q2", "Q2 E->GND; GPIO41-1k-B; 10k B-GND"],
            ["Buzzer pasivo", "GPIO42 por 100 ohm", "solo si corriente medida es segura"],
        ], [40*mm, 82*mm, 118*mm], font=7.2),
        PageBreak(),
        para("5. Audio hablado de Jarvis", h1),
        WiringMap("Respuesta en espanol; microfono opcional",
                  ["BUS +5 V", "ESP32 3V3", "GND", "GPIO15", "GPIO16", "GPIO17", "GPIO18"],
                  ["INMP441", "MAX98357A", "Parlante 4 ohm/3 W"],
                  [("GPIO15", "INMP441", "signal", ""),
                   ("GPIO16", "INMP441", "signal", ""),
                   ("GPIO17", "INMP441", "signal", ""),
                   ("GPIO16", "MAX98357A", "signal", ""),
                   ("GPIO17", "MAX98357A", "signal", ""),
                   ("GPIO18", "MAX98357A", "signal", ""),
                   ("BUS +5 V", "MAX98357A", "power", ""),
                   ("ESP32 3V3", "INMP441", "power", ""),
                   ("MAX98357A", "Parlante 4 ohm/3 W", "signal", "SPK+ / SPK-")], height=88*mm),
        para("Para la feria, Jarvis recibe ordenes por IR y reproduce frases espanolas guardadas en flash. El INMP441 deja de ser requisito inmediato: puede cotizarse o instalarse como ampliacion futura. El parlante va entre SPK+ y SPK-, nunca entre una salida y GND.", ok),
        make_table([
            ["Evento", "Respuesta recomendada"],
            ["Sala ON", "He encendido la luz de la sala"],
            ["Cultivo ON", "Iluminacion suplementaria activada"],
            ["Riego aceptado", "El suelo esta seco. Iniciando riego"],
            ["Riego rechazado", "No puedo regar porque falta agua"],
            ["STOP", "Paro de seguridad activado"],
        ], [70*mm, 170*mm], font=7.2),
        para("Un codigo desconocido se ignora: ninguna carga cambia y Jarvis puede decir 'Orden no reconocida'.", ok),
        PageBreak(),
        para("6. Mapa final de GPIO", h1),
        make_table([
            ["GPIO", "Funcion", "Conexion", "Estado al arrancar"],
            ["1", "suelo", "AO", "entrada ADC"], ["2", "nivel", "S/OUT", "entrada ADC"],
            ["3", "luz", "divisor LDR/10k", "entrada ADC"],
            ["4", "bomba", "DRV8833 AIN1", "LOW"], ["5", "sala", "LED + 330 ohm", "LOW"],
            ["6", "dormitorio", "LED + 330 ohm", "LOW"], ["7", "ventilador", "DRV8833 BIN1", "LOW"],
            ["8", "cultivo", "1k -> S8050 Q1", "LOW"], ["9", "PIR", "OUT <=3.3V", "entrada"],
            ["10", "STOP", "boton a GND", "INPUT_PULLUP"], ["11", "silencio", "boton a GND", "INPUT_PULLUP"],
            ["12", "IR", "HX1838 S/OUT", "entrada"], ["13", "LCD SCL", "I2C 3.3V", "bus"],
            ["14", "DHT11", "DATA + 10k", "entrada"], ["15", "microfono", "INMP441 SD", "opcional"],
            ["16", "I2S BCLK", "microfono/amplificador", "bus"], ["17", "I2S WS", "microfono/amplificador", "bus"],
            ["18", "audio OUT", "MAX98357A DIN", "salida"], ["21", "LCD SDA", "I2C 3.3V", "bus"],
            ["38", "boton sala", "a GND", "INPUT_PULLUP"], ["39", "boton riego", "a GND", "INPUT_PULLUP"],
            ["40", "boton ventilador", "a GND", "INPUT_PULLUP"], ["41", "buzzer activo", "1k -> S8050 Q2", "LOW"],
            ["42", "buzzer pasivo", "100 ohm si aprobado", "LOW/opcional"],
        ], [18*mm, 48*mm, 112*mm, 62*mm], font=7.1),
        para("GPIO38-42 deben confirmarse visibles en la serigrafia de la placa antes de montar. Si alguno no esta expuesto, reasignar en firmware y documento antes de cablear.", warn),
        para("Firmware actual: BANCO_SIN_ACTUADORES. Firmware final pendiente: DRV8833, IR, buzzers, audio y salidas finales. No habilitar todo cambiando un solo booleano.", ok),
        PageBreak(),
        para("7. Secuencia de integracion", h1),
        make_table([
            ["Paso", "Montaje", "Aprobacion"],
            ["1", "Fuente sola; medir jack y salida", "4.8-5.2 V, centro positivo"],
            ["2", "Fusible + switch + buses", "sin corto; polaridad correcta"],
            ["3", "ESP32 con firmware de banco", "5 arranques sin salida espuria"],
            ["4", "LCD I2C a 3.3 V", "0x27/0x3F y texto estable"],
            ["5", "DHT, suelo, nivel, LDR, PIR uno a uno", "lecturas plausibles y calibradas"],
            ["6", "HX1838", "los 21 botones entregan codigos unicos"],
            ["7", "LED sala/dormitorio/cultivo", "polaridad y resistencias correctas"],
            ["8", "DRV8833 sin motores", "sin calor ni corto"],
            ["9", "Bomba dentro de agua", "pulso corto, corte por nivel/timeout"],
            ["10", "Ventilador", "giro correcto y tension estable"],
            ["11", "Buzzer activo y luego pasivo", "sin exceder GPIO ni ruido en ADC"],
            ["12", "MAX98357A + parlante", "audio claro; sin reinicios"],
            ["13", "Todo simultaneo", "1 hora vigilada, sin calor/reset"],
        ], [18*mm, 112*mm, 110*mm]),
        para("STOP obligatorio: olor, humo, cable caliente, caida sostenida de 5 V, agua fuera de bandeja, ESP32 reiniciandose o cualquier GPIO por encima de 3.3 V.", warn),
        PageBreak(),
        para("8. Fallas probables y criterio final", h1),
        make_table([
            ["Sintoma", "Primera comprobacion", "Accion"],
            ["IR no responde", "pila, orientacion HX1838, OUT GPIO12", "leer Serial y probar cada tecla"],
            ["IR repite acciones", "trama NEC repeat", "ignorar repeticion salvo volumen"],
            ["LCD sin texto", "3.3 V, contraste, SDA21/SCL13", "escanear 0x27/0x3F"],
            ["Bomba no gira", "VM, SLEEP, AIN1, AOUT1/AOUT2", "probar dentro de agua y medir"],
            ["ESP32 se reinicia", "caida del bus y retorno de motor", "estrella, cables y capacitor"],
            ["LED no enciende", "anodo/catodo, 330 ohm, E/B/C", "probar cada LED por separado"],
            ["Buzzer mudo", "activo/pasivo, polaridad y transistor", "probar tono/pulso corto"],
            ["Audio distorsiona", "SPK+/SPK-, ganancia y 5 V", "bajar volumen; revisar capacitor"],
            ["Riego rechazado", "CAL, nivel, STOP, bloqueo", "diagnostico y rearme"],
            ["Sensor fijo 0/4095", "VCC, GND, AO y humedad", "desenergizar y revisar"],
        ], [43*mm, 95*mm, 102*mm], font=7.2),
        para("Checklist de salida", h2),
        make_table([
            ["[ ]", "Todas las cargas apagadas al encender"],
            ["[ ]", "STOP fisico apaga bomba, ventilador y luces"],
            ["[ ]", "Nivel bajo impide riego incluso por control IR"],
            ["[ ]", "Codigo IR desconocido no cambia ninguna salida"],
            ["[ ]", "Tres LED de cultivo: 2 azules + 1 rojo, 330 ohm individual"],
            ["[ ]", "Jarvis responde en espanol y puede silenciarse"],
            ["[ ]", "Una hora completa sin reinicios, olor ni calentamiento anormal"],
        ], [18*mm, 222*mm]),
    ]

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=landscape(letter),
                            rightMargin=15*mm, leftMargin=15*mm,
                            topMargin=14*mm, bottomMargin=16*mm,
                            title="PROJECT DOMUS Manual visual final",
                            author="PROJECT DOMUS")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
