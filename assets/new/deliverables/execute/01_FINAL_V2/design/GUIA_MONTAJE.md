# Guía de la maqueta PROJECT DOMUS v2

## Qué representa

La maqueta es una casa inteligente de **una sola planta** presentada en corte frontal. No es una vivienda de dos niveles. La fachada queda abierta para que durante la exposición se vean la cocina, la sala, el dormitorio, el baño, las luces y los sensores. El techo se apoya de forma removible y contiene dos paneles solares didácticos.

La distribución reproduce la composición de la referencia:

1. Extremo izquierdo: depósito, bomba e invernadero transparente.
2. Centro posterior: vivienda abierta con cocina/sala, dormitorio y baño.
3. Centro frontal: jardín, pasarela y porche cubierto.
4. Derecha: torre Jarvis con aro de luz, micrófono, altavoz, pantalla y MIC OFF.
5. Extremo derecho: gabinete transparente con ESP32-S3, relés, fusible y distribución de 5 V.

## Recorrido de cada sistema

### Riego

El sensor de humedad se coloca entre los dos bancales. El depósito y la bomba quedan en la esquina izquierda. La manguera pasa por la zona de agua, nunca por el gabinete electrónico. Si el nivel es bajo, el ESP32 mantiene la bomba apagada. También existe un límite de 120 segundos por ciclo.

### Clima

El DHT11 se instala en el muro posterior, ventilado y lejos de las luces. Cuando la temperatura supera el umbral, el ESP32 acciona el ventilador. La histéresis evita que se encienda y apague repetidamente cerca del límite.

### Iluminación y presencia

La LDR queda bajo el alero para medir luz ambiental sin recibir directamente la luz interior. El PIR mira hacia la entrada. Las luces de sala, dormitorio e invernadero se controlan localmente mediante reglas automáticas o pulsadores físicos.

### Jarvis local

El INMP441, el aro WS2812, la pantalla, el amplificador y el altavoz se concentran en la torre azul. El reconocimiento y las respuestas se ejecutan en el ESP32-S3. MIC OFF debe cortar físicamente la señal o alimentación del micrófono; no es solamente un estado de software.

### Electrónica

El gabinete derecho es transparente y removible para enseñar el circuito. De arriba hacia abajo: interruptor general, ESP32-S3, relés, fusible, barra de 5 V/GND y terminales. El gabinete permanece separado del depósito y elevado respecto de posibles fugas.

## Orden de construcción

1. Cortar la base y marcar sobre ella las posiciones del plano, sin pegar módulos.
2. Montar en seco la vivienda de una planta y comprobar que el techo entra y sale.
3. Construir el porche y verificar que no tape por completo la vista del interior.
4. Montar el esqueleto del invernadero; cortar los paneles transparentes después de verificar los ángulos.
5. Fabricar la torre Jarvis y el gabinete según las medidas reales de pantalla, aro y placas.
6. Instalar canaletas y pasar primero alimentación, después señales y por último mangueras.
7. Probar el sistema con la fuente de 5 V y cargas desconectadas.
8. Conectar una carga a la vez y medir corriente, temperatura y caída de tensión.
9. Instalar depósito y bomba al final, usando bandeja de contención.

## Archivos que debes abrir

- `plano_tecnico_domus.pdf`: medidas y vistas de fabricación.
- `modelo_3d_interactivo.html`: visor local; permite girar, ocultar capas y seleccionar piezas.
- `project_domus.obj` + `project_domus.mtl`: edición en Blender, FreeCAD o software compatible.
- `lista_corte.csv`: piezas estructurales principales.
- `piezas_modelo.csv`: las 99 piezas geométricas del modelo digital.
- `bom_componentes.csv`: electrónica y materiales.

## Decisiones todavía pendientes

Las cotas son una propuesta coherente, no deben enviarse directamente a corte láser hasta medir la pantalla, el aro LED, el módulo de relés, la placa ESP32 y el espesor real de madera/acrílico. Esas medidas pueden obligar a ajustar la torre y el gabinete unos milímetros.

El diseño no incluye Wi-Fi, Bluetooth/BLE, teléfono, Kotlin, MQTT, servidor ni nube. Todo el control es físico y local.
