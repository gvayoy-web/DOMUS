"""Genera el paquete imprimible para la ronda B01-B05 de PROJECT DOMUS."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "DOMUS_Ronda_B01-B05_sin_compras.pdf"

NAVY = colors.HexColor("#12355B")
BLUE = colors.HexColor("#247BA0")
PALE = colors.HexColor("#EAF4F8")
GREEN = colors.HexColor("#DDF2E3")
AMBER = colors.HexColor("#FFF1C7")
RED = colors.HexColor("#B3261E")
INK = colors.HexColor("#1C2630")
GRAY = colors.HexColor("#5B6873")


def p(text, style):
    return Paragraph(text, style)


def table(data, widths, header=True, font=8.2):
    normal_cell = ParagraphStyle(
        "Cell",
        fontName="Helvetica",
        fontSize=font,
        leading=font + 2,
        textColor=INK,
    )
    header_cell = ParagraphStyle(
        "HeaderCell",
        parent=normal_cell,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )
    wrapped = []
    for row_index, row in enumerate(data):
        style = header_cell if header and row_index == 0 else normal_cell
        wrapped.append([
            value if isinstance(value, Paragraph) else Paragraph(escape(str(value)), style)
            for value in row
        ])
    t = Table(wrapped, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    rules = [
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#93A8B7")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font),
        ("LEADING", (0, 0), (-1, -1), font + 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        rules += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    for row in range(1 if header else 0, len(data)):
        if row % 2 == 0:
            rules.append(("BACKGROUND", (0, row), (-1, row), colors.HexColor("#F5F8FA")))
    t.setStyle(TableStyle(rules))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#C8D3DA"))
    canvas.line(18 * mm, 13 * mm, 198 * mm, 13 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(18 * mm, 8 * mm, "PROJECT DOMUS - Ronda B01-B05 - ESP32-S3 N16R8")
    canvas.drawRightString(198 * mm, 8 * mm, f"Pagina {doc.page}")
    canvas.restoreState()


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleDOMUS", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=25, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8)
    subtitle = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=11, leading=14, textColor=GRAY, alignment=TA_CENTER, spaceAfter=13)
    h1 = ParagraphStyle("H1DOMUS", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=NAVY, spaceBefore=5, spaceAfter=7)
    h2 = ParagraphStyle("H2DOMUS", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, leading=14, textColor=BLUE, spaceBefore=7, spaceAfter=5)
    body = ParagraphStyle("BodyDOMUS", parent=styles["BodyText"], fontSize=9.2, leading=12, textColor=INK, spaceAfter=5)
    small = ParagraphStyle("SmallDOMUS", parent=body, fontSize=8, leading=10)
    warning = ParagraphStyle("WarningDOMUS", parent=body, fontName="Helvetica-Bold", textColor=RED, backColor=colors.HexColor("#FDE9E7"), borderColor=RED, borderWidth=0.8, borderPadding=7, spaceAfter=9)
    okbox = ParagraphStyle("OKDOMUS", parent=body, fontName="Helvetica-Bold", textColor=NAVY, backColor=GREEN, borderColor=BLUE, borderWidth=0.8, borderPadding=7, spaceAfter=9)
    mono = ParagraphStyle("MonoDOMUS", parent=body, fontName="Courier", fontSize=7.8, leading=10, backColor=colors.HexColor("#EEF2F5"), borderPadding=6)

    story = [
        Spacer(1, 8 * mm),
        p("PROJECT DOMUS", title),
        p("Paquete de pruebas B01-B05 sin compras", title),
        p("ESP32-S3 N16R8 - Firmware domus_esqueleto - 7 septiembre 2026", subtitle),
        p("OBJETIVO: comprobar la placa y los sensores que ya tienen. No hacen falta el modulo de cuatro reles, la fuente final, audio ni microSD.", okbox),
        p("SEGURIDAD: alimentar la placa solo por USB. GPIO4-GPIO8 quedan sin conectar. No conectar bomba, motor, bateria, panel solar ni señales de 5 V. Desconectar USB antes de cambiar cables.", warning),
        p("Configuracion del Arduino IDE", h1),
        table([
            ["Opcion", "Valor"],
            ["Board", "ESP32S3 Dev Module"],
            ["Flash Size", "16MB"],
            ["PSRAM", "OPI PSRAM"],
            ["Partition Scheme", "3M APP / 9M FATFS"],
            ["CPU Frequency", "240 MHz"],
            ["Serial Monitor", "115200 baud, Newline o Both NL & CR"],
            ["Proteccion", "HABILITAR_RELE_BOMBA=false; GPIO5-GPIO8 siempre bloqueados"],
        ], [48 * mm, 122 * mm]),
        Spacer(1, 5 * mm),
        p("Secuencia permitida", h1),
        table([
            ["1", "PC + Arduino IDE", "USB", "ESP32-S3 N16R8"],
            ["2", "ESP32", "5 arranques", "Guardar salida Serial"],
            ["3", "Placa apagada", "Agregar una pieza", "Revisar cableado"],
            ["4", "Placa encendida", "Estimular sensor", "Anotar min/max y validez"],
            ["5", "Lectura segura", "Continuar", "Siguiente pieza"],
            ["STOP", "Calor / olor / resets / >3.3 V", "Desconectar USB", "Fotografiar y revisar"],
        ], [15 * mm, 50 * mm, 45 * mm, 60 * mm]),
        PageBreak(),
        p("Mapa completo del ESP32-S3 N16R8", h1),
        p("Usar los nombres impresos junto a los headers de la placa. No contar posiciones desde una esquina: distintas placas N16R8 pueden ordenar los headers de otra manera.", warning),
        table([
            ["Pin ESP32", "Conexion exacta", "Estado en la ronda"],
            ["USB", "PC por cable USB de datos", "Alimenta y programa la placa"],
            ["3V3 + GND", "DHT, suelo, nivel y divisor LDR", "Solo sensores de 3.3 V"],
            ["GPIO1", "AO del sensor de suelo", "Entrada ADC"],
            ["GPIO2", "AO del sensor de nivel", "Entrada ADC"],
            ["GPIO3", "Punto medio LDR - 10 kOhm", "Entrada ADC"],
            ["GPIO4", "1 kOhm hacia base B del S8050", "Relé de bomba; bloqueado hasta B06"],
            ["GPIO5, 6, 7, 8", "SIN CABLE", "Sin etapa; bloqueados siempre"],
            ["GPIO9", "OUT del PIR, medido <= 3.3 V", "Entrada digital"],
            ["GPIO10", "Pulsador PARO hacia GND", "INPUT_PULLUP"],
            ["GPIO11", "Switch MIC OFF hacia GND", "INPUT_PULLUP"],
            ["GPIO12", "Pulsador DEMO hacia GND", "INPUT_PULLUP"],
            ["GPIO13", "SCL del LCD, por nivel seguro", "I2C"],
            ["GPIO14", "DATA del DHT", "Entrada digital"],
            ["GPIO21", "SDA del LCD, por nivel seguro", "I2C"],
        ], [30 * mm, 91 * mm, 49 * mm], font=7.5),
        p("Nunca conectar 5 V a un GPIO. El pin 5V/VIN solo se usa con una fuente regulada y una arquitectura de alimentación ya verificada; durante B01-B05 se alimenta únicamente por USB.", body),
        PageBreak(),
        p("Único relé desnudo: diagrama completo", h1),
        p("El relé azul fotografiado no es un módulo: no tiene pines IN/VCC/GND. El GPIO jamás alimenta su bobina directamente.", okbox),
        table([
            ["Ruta de control de la bobina", "Conexion"],
            ["ESP32 GPIO4", "resistencia 1 kOhm -> base B del S8050"],
            ["S8050 emisor E", "GND común"],
            ["S8050 colector C", "COIL B del relé"],
            ["COIL A del relé", "+5 V regulados"],
            ["1N4007 sobre la bobina", "cátodo/raya a COIL A (+5 V); ánodo sin raya a COIL B/colector"],
        ], [62 * mm, 108 * mm]),
        Spacer(1, 4 * mm),
        table([
            ["Ruta de potencia de la bomba", "Conexion"],
            ["+5 V con fusible", "COM del relé"],
            ["NO del relé", "positivo + de la minibomba"],
            ["negativo - de la minibomba", "GND de la fuente"],
            ["NC del relé", "AISLADO; no conectar"],
            ["Segundo 1N4007 sobre bomba", "raya al + de bomba; ánodo al - de bomba"],
        ], [62 * mm, 108 * mm]),
        p("Esquema lógico: GPIO4 -> 1 kOhm -> B(S8050); E -> GND; C -> COIL B; COIL A -> +5 V. En paralelo con la bobina: raya del 1N4007 a +5 V. Contactos: +5 V con fusible -> COM -> NO -> bomba +; bomba - -> GND.", mono),
        p("No existe una regla universal de 'pata del medio'. Con todo desconectado, localizar primero la pareja de bobina por resistencia finita. De las tres restantes, COM-NC tiene continuidad sin energía y COM-NO está abierto; al energizar correctamente la bobina cambian. Confirmar E/B/C del S8050 por su fabricante o con probador: tampoco es universal.", warning),
        p("Solo si la inscripción superior coincide exactamente con Songle SRD-05VDC-SL-C, su hoja técnica muestra una bobina de 5 V y variantes de 55 o 70 ohm. Si no coincide, ese dato no identifica el componente. Fuente: datasheet Songle SRD.", small),
        PageBreak(),
        p("Línea exacta que desbloquea únicamente la bomba", h1),
        p("Archivo: firmware/domus_esqueleto/domus_config.h", body),
        p("constexpr bool HABILITAR_RELE_BOMBA = false;", mono),
        p("Para B01-B05 se deja en false. Después de identificar patas, montar el S8050, colocar ambos diodos, medir 5 V y superar B06 sin bomba, cambiar solamente false por true:", body),
        p("constexpr bool HABILITAR_RELE_BOMBA = true;", mono),
        p("Ese cambio habilita físicamente solo GPIO4. El arreglo SALIDA_FISICA_HABILITADA conserva GPIO5, GPIO6, GPIO7 y GPIO8 en false. El diagnóstico debe mostrar FIS=10000. Si muestra otra combinación, no conectar cargas.", warning),
        table([
            ["Antes de cambiar a true", "Criterio"],
            ["Bobina, COM, NO y NC identificados", "Multímetro; no por posición visual"],
            ["E/B/C del S8050 identificados", "Hoja técnica del componente exacto o probador"],
            ["Diodo de bobina y diodo de bomba", "Polaridad verificada"],
            ["Fuente de 5 V y GND común", "Tensión estable, sin usar 3V3 para la bobina"],
            ["B06 sin bomba", "Sin reset, olor, calor ni pulso al arrancar"],
            ["Calibración de nivel", "CAL=1 antes de autorizar riego"],
        ], [80 * mm, 90 * mm]),
        p("Volver a false inmediatamente si el relé vibra, el ESP32 se reinicia, aparece olor/calor o GPIO4 se activa al arranque. La prueba de software no reemplaza medir corriente y temperatura.", okbox),
        PageBreak(),
        p("Diagrama de conexiones - solo sensores", h1),
        p("Conectar una sola rama por vez. Todas las señales al ESP32 deben permanecer entre 0 y 3.3 V.", body),
        table([
            ["ESP32-S3 N16R8", "Conexion", "Modulo", "Limite"],
            ["3V3 / GND / GPIO14", "VCC / GND / DATA", "DHT11 o DHT22", "Confirmar modelo"],
            ["3V3 / GND / GPIO1", "VCC / GND / AO", "Suelo", "No usar DO"],
            ["3V3 / GND / GPIO2", "VCC / GND / AO", "Nivel", "Mojar solo sensor"],
            ["3V3 / GND / GPIO3", "Divisor con 10 kOhm", "LDR", "Punto medio al ADC"],
            ["VCC segun modulo / GND / GPIO9", "VCC / GND / OUT", "PIR", "Medir OUT <= 3.3 V"],
            ["GPIO10 / GND", "Pulsador N.O.", "PARO", "INPUT_PULLUP"],
            ["GPIO12 / GND", "Pulsador N.O.", "Demo", "INPUT_PULLUP"],
            ["GPIO4-GPIO8", "SIN CABLE", "Reles/cargas", "No probar en B01-B05"],
        ], [42 * mm, 49 * mm, 42 * mm, 37 * mm]),
        Spacer(1, 6 * mm),
        p("LCD I2C: decision antes de conectar", h1),
        table([
            ["Pregunta", "Si", "No / no se sabe"],
            ["Hay adaptador bidireccional I2C?", "LV=3V3, HV=5V; SDA=21, SCL=13", "Pasar a la siguiente pregunta"],
            ["Backpack confirmado funcionando a 3.3 V?", "Alimentar a 3V3; SDA=21, SCL=13", "No conectar LCD; marcar NO PROBADO"],
        ], [55 * mm, 62 * mm, 53 * mm]),
        p("No alimentar el backpack a 5 V cuando sus pull-ups puedan elevar SDA/SCL a 5 V. Omitir el LCD no invalida las pruebas de los otros sensores.", warning),
        p("GPIO2, GPIO9 y GPIO13 deben estar visibles en la placa concreta. Si un pin no aparece, no improvisar otro: fotografiar ambas caras y actualizar firmware + mapa antes de continuar.", body),
        PageBreak(),
        p("LCD1602 con backpack I2C - diagrama explicado", h1),
        p("El adaptador I2C ya instalado detras del LCD reduce la conexion de 16 pines paralelos a cuatro terminales: GND, VCC, SDA y SCL. El integrado suele ser PCF8574 y la direccion habitual es 0x27 o 0x3F.", body),
        table([
            ["ESP32-S3 N16R8", "Ruta", "Backpack I2C", "Que hace"],
            ["GND", "---------------->", "GND", "Referencia comun"],
            ["3V3 o lado LV", "---------------->", "VCC o adaptador", "Alimentacion logica segura"],
            ["GPIO21", "<--------------->", "SDA", "Datos I2C"],
            ["GPIO13", "<--------------->", "SCL", "Reloj I2C"],
        ], [42 * mm, 37 * mm, 42 * mm, 49 * mm]),
        Spacer(1, 5 * mm),
        p("Ruta A - backpack verificado a 3.3 V", h2),
        table([
            ["ESP32 3V3", "Backpack VCC"],
            ["ESP32 GND", "Backpack GND"],
            ["GPIO21", "SDA"],
            ["GPIO13", "SCL"],
        ], [60 * mm, 110 * mm]),
        p("Es la primera ruta que se puede intentar si el backpack funciona correctamente a 3.3 V. Puede ocurrir que la retroiluminacion o el contraste sean debiles; eso no autoriza subir VCC a 5 V sin revisar niveles.", body),
        p("Ruta B - backpack alimentado a 5 V", h2),
        table([
            ["ESP32", "Adaptador bidireccional", "Backpack"],
            ["3V3", "LV", "-"],
            ["5V", "HV", "VCC"],
            ["GND", "GND comun", "GND"],
            ["GPIO21", "LV1 <-> HV1", "SDA"],
            ["GPIO13", "LV2 <-> HV2", "SCL"],
        ], [48 * mm, 64 * mm, 58 * mm]),
        p("Muchos backpacks tienen resistencias pull-up conectadas a VCC. Si VCC es 5 V, SDA y SCL tambien pueden quedar a 5 V. El ESP32-S3 no tolera 5 V en GPIO: usar adaptador bidireccional o medir primero.", warning),
        p("Que debe verse al probarlo", h2),
        table([
            ["Resultado", "Interpretacion"],
            ["PROJECT DOMUS / Base modular", "LCD detectado e inicializado"],
            ["EVENTO;LCD_NO_DETECTADO", "No hubo respuesta en 0x27 ni 0x3F; revisar direccion, SDA/SCL y alimentacion"],
            ["Pantalla iluminada sin letras", "Revisar potenciometro de contraste del backpack"],
            ["Caracteres extraños", "Revisar GND, ruido, direccion y libreria; no asumir daño"],
        ], [57 * mm, 113 * mm]),
        p("Para la prueba actual de placa sola, el LCD permanece desconectado. Esta pagina se usa en B03b, no durante B01-B02.", okbox),
        PageBreak(),
        p("Procedimiento y criterios de aceptacion", h1),
        table([
            ["ID", "Accion", "PASS", "Si falla"],
            ["B01", "Foto de ambas caras; ubicar 3V3, GND, 1,2,3,9,10,12,13,14,21", "N16R8 y pines identificados", "Parar; no adivinar pin"],
            ["B02", "Cargar firmware y reiniciar 5 veces", "5 banners; sin bucle de reset", "Guardar log y probar cable/puerto"],
            ["B03a", "DHT: registrar 20 ciclos", "VA=1 estable", "Revisar DHT_TIPO y DATA"],
            ["B03b", "LCD solo si niveles son seguros", "0x27/0x3F y texto legible", "NO PROBADO si falta adaptacion"],
            ["B04a", "Suelo al aire y en muestra humeda", "VS=1; rango visible", "Revisar AO/VCC/GND"],
            ["B04b", "Nivel seco y mojado", "VN=1; rango visible", "Revisar AO/VCC/GND"],
            ["B04c", "LDR tapado y con luz", "VL=1; rango visible", "Revisar divisor 10 kOhm"],
            ["B04d", "PIR: reposo y movimiento", "PIR cambia y retiene", "Esperar estabilizacion/revisar OUT"],
            ["B05", "Guardar CAL y reiniciar", "CAL=1 despues del reinicio", "No repetir valores inventados"],
        ], [14 * mm, 66 * mm, 51 * mm, 39 * mm], font=7.6),
        Spacer(1, 6 * mm),
        p("Salida esperada", h2),
        p("DOMUS_LISTO;PLACA=ESP32-S3-N16R8;PERFIL=BANCO_SIN_ACTUADORES;RELE_BOMBA=0;GPIO5_8=OFF<br/>DIAG;...;FIS=00000;...;CAL=0", mono),
        p("VS/VN/VL/VA=1 significa que el filtro basico acepto la lectura; no certifica calibracion. CAL=0 es normal antes de B05.", body),
        PageBreak(),
        p("Hoja de registro B01-B05", h1),
        p("Nombre: ______________________________   Fecha: ______________   Puerto COM: __________", body),
        table([
            ["ID", "Componente / estado", "Min", "Max", "Validez", "PASS / FAIL / NP", "Observacion o foto"],
            ["B01", "Placa N16R8 / pines", "", "", "", "", ""],
            ["B02", "Arranque 1", "", "", "", "", ""],
            ["B02", "Arranque 2", "", "", "", "", ""],
            ["B02", "Arranque 3", "", "", "", "", ""],
            ["B02", "Arranque 4", "", "", "", "", ""],
            ["B02", "Arranque 5", "", "", "", "", ""],
            ["B03a", "DHT - 20 ciclos", "", "", "VA=", "", ""],
            ["B03b", "LCD / direccion", "", "", "addr=", "", ""],
            ["B04a", "Suelo seco / humedo", "", "", "VS=", "", ""],
            ["B04b", "Nivel seco / mojado", "", "", "VN=", "", ""],
            ["B04c", "LDR oscuro / claro", "", "", "VL=", "", ""],
            ["B04d", "PIR reposo / movimiento", "", "", "", "", ""],
            ["B05", "Calibracion tras reinicio", "", "", "CAL=", "", ""],
        ], [13 * mm, 47 * mm, 14 * mm, 14 * mm, 18 * mm, 28 * mm, 36 * mm], font=7.2),
        Spacer(1, 5 * mm),
        p("Resultado global:  [  ] PASS B01-B05   [  ] PARCIAL   [  ] DETENIDO", h2),
        p("Incidencia principal: ____________________________________________________________________________________<br/><br/>Cambio que se propone: __________________________________________________________________________________", body),
        PageBreak(),
        p("Tarjeta de calibracion y cierre", h1),
        p("Primero observar los rangos. Con las salidas desconectadas, enviar PARO y sustituir los puntos por valores medidos.", body),
        p("CAL SECO=...<br/>CAL HUMEDO=...<br/>CAL OSCURO=...<br/>CAL CLARO=...<br/>CAL NIVEL=...<br/>CAL VER<br/>CAL GUARDAR<br/>REARMAR", mono),
        Spacer(1, 5 * mm),
        table([
            ["Valor", "Medicion", "Condicion"],
            ["SECO", "________", "Sensor de suelo realmente seco"],
            ["HUMEDO", "________", "Muestra humeda, sin sumergir electronica"],
            ["OSCURO", "________", "LDR cubierto"],
            ["CLARO", "________", "LDR con iluminacion de la demostracion"],
            ["NIVEL", "________", "Minimo de agua que aun se considera seguro"],
        ], [38 * mm, 35 * mm, 97 * mm]),
        p("Separacion minima: SECO vs HUMEDO >= 100 cuentas; OSCURO vs CLARO >= 100 cuentas. Confirmar si la lectura de nivel sube o baja al mojar; no asumir direccion.", warning),
        p("Cierre de la ronda", h1),
        table([
            ["[  ]", "Se guardo el log completo del monitor serie"],
            ["[  ]", "Se guardaron fotos de la placa y de cada conexion"],
            ["[  ]", "B01-B05 fueron actualizados en la nota 33"],
            ["[  ]", "HABILITAR_RELE_BOMBA sigue en false durante B01-B05"],
            ["[  ]", "GPIO4-GPIO8 siguen sin cargas"],
            ["[  ]", "B06-B10 quedaron como DIFERIDAS, no como fallidas"],
        ], [15 * mm, 155 * mm], header=False),
        Spacer(1, 6 * mm),
        p("No continuar a B06 hasta identificar y montar el driver del único relé. B06 se hace primero sin bomba; solo después se cambia una línea y se verifica FIS=10000.", okbox),
    ]

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="PROJECT DOMUS - Ronda B01-B05 sin compras",
        author="PROJECT DOMUS",
        subject="Guia de banco ESP32-S3 N16R8",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
