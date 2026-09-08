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
    Image as RLImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "DOMUS_Ronda_B01-B05_sin_compras.pdf"
COMPONENT_GUIDE = ROOT / "output" / "diagramas" / "guia-identificacion-transistor-diodo-led.png"

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
            ["Proteccion", "HABILITAR_BOMBA=false; GPIO5-GPIO8 siempre bloqueados"],
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
            ["GPIO4", "1 kOhm hacia base B del S8050", "Bomba 3-6 V; bloqueada hasta B07"],
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
        p("Bomba 3-6 V con S8050: diagrama completo", h1),
        p("El relé no participa. GPIO4 solo entrega la señal de control; la fuente de 5 V entrega la corriente de la bomba.", okbox),
        table([
            ["Ruta de control", "Conexion"],
            ["ESP32 GPIO4", "resistencia 1 kOhm -> base B del S8050"],
            ["S8050 emisor E", "GND común"],
            ["S8050 colector C", "negativo de la bomba"],
            ["positivo de la bomba", "+5 V regulados del rail"],
            ["1N4007 sobre la bomba", "catodo/raya al positivo (+5 V); anodo sin raya al colector"],
        ], [62 * mm, 108 * mm]),
        Spacer(1, 4 * mm),
        table([
            ["Desacoplo y alimentacion", "Conexion"],
            ["Electrolitico 470-1000 uF", "+ al rail 5 V; -/franja a GND, cerca del motor"],
            ["Ceramico 100 nF", "en paralelo con el rail o terminales del motor; no tiene polaridad"],
            ["GND de fuente de bomba", "unir a GND del ESP32 solo al integrar el driver"],
            ["5 V de dos USB", "NO unir entre si; elegir una fuente para cada rail"],
            ["Relé azul", "reservado; no se conecta en esta version"],
        ], [62 * mm, 108 * mm]),
        p("Esquema: +5 V -> bomba +; bomba - -> C(S8050); E -> GND; GPIO4 -> 1 kOhm -> B. Diodo 1N4007 en paralelo con la bomba: RAYA al +5 V y lado SIN RAYA al colector.", mono),
        p("Confirmar E/B/C del transistor exacto: el orden fisico puede variar. La resistencia de 1 kOhm es un punto inicial y no certifica saturacion. Medir corriente, caida C-E y temperatura; si el motor no arranca o el transistor se calienta, parar.", warning),
        PageBreak(),
        p("Guia visual de transistor, diodo y LED", h1),
        RLImage(str(COMPONENT_GUIDE), width=170 * mm, height=113.3 * mm),
        Spacer(1, 5 * mm),
        p("La vista E-B-C solo aplica si la marca y la hoja tecnica del transistor exacto lo confirman. En el 1N4007, la franja fisica identifica el catodo. En un LED nuevo, la pata larga suele ser anodo y el lado plano catodo; verificar si las patas fueron cortadas.", warning),
        PageBreak(),
        p("Código: línea exacta que habilita únicamente la bomba", h1),
        p("Archivo: firmware/domus_esqueleto/domus_config.h", body),
        p("constexpr bool HABILITAR_BOMBA = false;", mono),
        p("Se deja en false hasta que el rail tenga 5 V medidos, la bomba funcione directa y el S8050 con diodo este montado. Después cambiar solamente false por true:", body),
        p("constexpr bool HABILITAR_BOMBA = true;", mono),
        p("Ese cambio habilita físicamente solo GPIO4. El arreglo SALIDA_FISICA_HABILITADA conserva GPIO5, GPIO6, GPIO7 y GPIO8 en false. El diagnóstico debe mostrar FIS=10000. Si muestra otra combinación, no conectar cargas.", warning),
        table([
            ["Antes de cambiar a true", "Criterio"],
            ["Bomba funciona directa", "3-5 V medidos; prueba breve sin ESP32"],
            ["E/B/C del S8050 identificados", "Hoja técnica del componente exacto o probador"],
            ["Diodo de bomba", "Raya a +5 V; lado sin raya al colector"],
            ["Fuente de 5 V y GND común", "Tension estable; nunca usar GPIO o 3V3 para motor"],
            ["B07 con driver", "Sin reset, olor, calor ni pulso al arrancar"],
            ["Calibración de nivel", "CAL=1 antes de autorizar riego"],
        ], [80 * mm, 90 * mm]),
        p("Volver a false inmediatamente si la bomba no arranca, el ESP32 se reinicia, aparece olor/calor o GPIO4 se activa al arranque. La prueba de software no reemplaza medir corriente y temperatura.", okbox),
        PageBreak(),
        p("Diagnostico de alimentacion y bomba", h1),
        p("La bomba no depende del codigo durante esta pagina. Primero demostrar energia y giro con ESP32 desconectado.", okbox),
        table([
            ["Paso", "Accion", "Resultado correcto", "Si no ocurre"],
            ["P1", "Switch ON; jumper del rail en 5V", "Modulo encendido", "Revisar entrada y polaridad"],
            ["P2", "Medir + y - del mismo rail", "4.8-5.2 V", "No conectar bomba; revisar jumper/rail"],
            ["P3", "Probar LED + resistencia", "LED enciende", "Rail o contacto incorrecto"],
            ["P4", "Bomba directa 1 s", "Gira/vibra", "Invertir cables una vez"],
            ["P5", "Bomba sigue inmovil", "FAIL confirmado", "Cable roto, rotor trabado o bomba dañada"],
        ], [14 * mm, 57 * mm, 47 * mm, 52 * mm], font=7.7),
        p("En muchos modulos tipo MB102, el USB-A hembra es salida y el jack circular es entrada. No asumir: leer IN/OUT y el rango impreso. No conectar un adaptador circular de voltaje o polaridad desconocidos.", warning),
        p("Prueba directa", h2),
        p("FUENTE +5V -> cable positivo de bomba<br/>FUENTE GND -> cable negativo de bomba<br/>ESP32: DESCONECTADO<br/>S8050 y diodo: todavia fuera", mono),
        p("Si el rail mide 5 V sin bomba pero cae mucho al conectarla, la fuente no entrega la corriente de arranque, el contacto es deficiente o la bomba esta en corto/trabada.", body),
        PageBreak(),
        p("Matriz de fallas probables", h1),
        table([
            ["Sintoma", "Causas probables", "Comprobacion / accion"],
            ["Modulo no enciende", "Entrada incorrecta; switch OFF; adaptador incompatible", "Desconectar y leer serigrafia/etiqueta"],
            ["LED del modulo enciende, rail 0 V", "Jumper OFF/mal puesto; rail equivocado", "Medir el mismo + y -; mover jumper sin energia"],
            ["Rail 5 V, bomba muda", "Polaridad; cable roto; rotor trabado; bomba dañada", "Prueba directa 1 s en ambas polaridades"],
            ["Rail cae al conectar bomba", "Fuente insuficiente; corto; contacto flojo", "Medir con carga; cambiar fuente/cables"],
            ["S8050 se calienta", "E/C invertidos; corriente excesiva; base insuficiente", "Apagar; verificar pinout y corriente"],
            ["ESP32 se reinicia al arrancar", "Ruido; caida de 5 V; GND deficiente; falta diodo/capacitor", "Separar fuente; revisar 1N4007 y 470-1000 uF"],
            ["Bomba siempre encendida", "C-E en corto; GPIO flotante; pinout incorrecto", "Volver false; desconectar GPIO; revisar transistor"],
            ["Bomba nunca enciende por codigo", "HABILITAR_BOMBA=false; CAL=0; nivel bajo; PARO", "DIAGNOSTICO, CAL VER, REARMAR"],
            ["Diodo se calienta", "Instalado al derecho sobre alimentacion", "Apagar: raya debe ir a +5 V"],
            ["LCD sin texto", "Direccion; contraste; SDA/SCL; nivel I2C", "Escanear 0x27/0x3F; ajustar contraste"],
            ["DHT invalido", "Tipo 11/22; DATA; intervalo; falta pull-up", "Revisar DHT_TIPO y 10 kOhm si suelto"],
            ["ADC fijo 0/4095", "AO desconectado; GND; 5 V; sensor saturado", "Desenergizar y revisar VCC/AO/GND"],
            ["PIR siempre activo", "Calentamiento; ajuste; ruido", "Esperar estabilizacion y reducir sensibilidad"],
        ], [38 * mm, 61 * mm, 71 * mm], font=6.9),
        p("DETENER: humo, olor, componente caliente al tacto, cable blando, chispas, USB que se desconecta repetidamente o mas de 3.3 V en un GPIO.", warning),
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
        p("DOMUS_LISTO;PLACA=ESP32-S3-N16R8;PERFIL=BANCO_SIN_ACTUADORES;DRIVER_BOMBA=0;GPIO5_8=OFF<br/>DIAG;...;FIS=00000;...;CAL=0", mono),
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
            ["[  ]", "HABILITAR_BOMBA sigue en false hasta probar fuente, bomba y driver"],
            ["[  ]", "GPIO4-GPIO8 siguen sin cargas"],
            ["[  ]", "B06-B10 quedaron como DIFERIDAS, no como fallidas"],
        ], [15 * mm, 155 * mm], header=False),
        Spacer(1, 6 * mm),
        p("No habilitar GPIO4 hasta que B06 confirme rail y bomba directa. B07 monta S8050 + 1N4007; solo despues se cambia una linea y se verifica FIS=10000.", okbox),
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
