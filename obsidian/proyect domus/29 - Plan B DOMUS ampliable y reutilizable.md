# Plan B: DOMUS ampliable y reutilizable

**Objetivo:** ahorrar recompras y permitir cambios de módulos sin reescribir el control.
**Arquitectura:** mismo ESP32 y cinco salidas; alimentación, sensores, potencia y
audio en ramales desmontables. **Tecnología:** Arduino y perfiles existentes 0/1.
**Base:** notas [[18 - Manual maestro de conexiones pin por pin]],
[[21 - Simplificacion y reduccion de costos]], [[27 - Comparador de planes costo y versatilidad]].
**Compatibilidad:** mismo despachador, protecciones y protocolo; no detección automática eléctrica.
**TDD:** fuera de esta entrega documental; regresión por cada cambio futuro.
**Verificación:** compilaciones separadas, inspección de mazo y protocolo de banco.
**Estado:** propuesta recomendada como estructura física de A y futura C.

## Dos opciones excluyentes de potencia

- **B económica:** etapas del plan A, perfil 1, solo cargas compatibles.
- **B relés:** relé individual existente + módulo de cuatro canales compatible,
  perfil 0, esquema de nota 18. Compra adicional si no se tiene; no es más barato
  por definición, pero evita depender del S8050 si el motor no resulta apto.

No combinar polaridades a voluntad: el perfil económico actual fija bomba LOW
y las otras cuatro HIGH. Un montaje mixto distinto requiere configuración y
pruebas nuevas antes de usarlo. Versatilidad no significa compatibilidad universal.

## Simplificaciones prioritarias

1. Una pantalla: LCD1602. Matriz, barra y displays quedan de reserva.
2. Un controlador: no añadir Pico/ESP8266 como coprocesadores sin necesidad medida.
3. Un indicador sencillo: LED del kit para estados antes de instalar WS2812.
4. Una entrada adicional como máximo: botones primero; IR si interesa mando
   remoto. Keypad de ocho señales no aporta ventaja si bastan botones.
5. Reed antes que RFID para detectar puerta; no son equivalentes para identificar
   usuarios. Ambos son ampliaciones, no capacidades implementadas por tener la pieza.
6. No añadir L293D al ventilador de un sentido por estar disponible: comprobar
   corriente, caída y arranque; la inversión de giro no es requisito doméstico.
7. No comprar lector SD para guardar pocas calibraciones: reutilizar persistencia
   existente. Registro largo en tarjeta sigue siendo una función opcional distinta.

## Pasos ejecutables

1. Elegir B económica o B relés según cargas reales; anotar elección en la nota 18.
2. Etiquetar ramales `ALIMENTACION`, `SENSORES`, `POTENCIA` y `AUDIO`; cada conector
   debe tener pinout, voltaje, corriente admisible y polaridad documentados.
   No reservar potencia por jumpers finos ni llevar red AC a la casa.
3. Registrar en nota 05 los pines ya ocupados; no asignar periféricos nuevos en
   pines reservados para micrófono/audio/SD sin revisión conjunta del firmware.
4. Compilar el perfil elegido con el comando del plan A cambiando únicamente
   `DOMUS_SALIDAS_ECONOMICAS=0` y carpeta `build/plan_b` para B relés.
5. Ejecutar `.venv-ia/Scripts/python.exe scripts/validate_project.py`.
6. Repetir las pruebas de nota 19 tras cada cambio: desconectar módulo opcional,
   comprobar funcionamiento doméstico, arranque OFF, PARO y recuperación.
7. En nota 12 registrar módulo/cableado/perfil/binario aprobado como conjunto.

## Costos y límites

Gasto = base de A + conectores/material faltante + etapa de potencia elegida.
No sumar relé cuádruple y cuatro drivers alternativos si cumplen el mismo fin.
Reutilizar conectores aptos ahorra compra; no elimina la necesidad de aislamiento.
Alimentación de pared ahora; batería/solar no forman parte de este presupuesto.
No hacer selector entre fuentes hasta diseñar protección contra retorno.

Estos pasos cambian documentación/configuración y montaje futuro, no añaden
un gestor genérico al sketch de más de 1800 líneas. Si surge un perfil mixto,
su cambio debe ser pequeño, explícito y probado en `firmware/tests`.
Retorno seguro: recuperar el mazo y binario anteriores, no solo una bandera.
