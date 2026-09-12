---
proyecto: PROJECT DOMUS
tipo: ola-correccion-firmware
actualizado: 2026-09-12
estado: aplicado_ola_1
perfil: ALFA_UN_COSTADO_SIN_IR
---

# Ola 1 — buffers, Jarvis único, GPIO12 y validación por perfil

Aplica las prioridades 1-7 del dictamen conjunto (revisor + filtro Isaac).
Guía vigente: [[47 - Guia visual principiante conexiones alfa]].
Potencia vigente: [[49 - Prueba de una carga con un S8050 y TP4056]].
Autoridad: [[46 - Plan maestro de consolidacion un costado]].

## Qué estaba mal

1. `PantallaBonita::feedback()` conservaba `const char*` del llamador. Con
   `char buf[17]` local desde `ejecutarTeclaIR()` leía memoria liberada.
2. `VozJarvis::ultima_` conservaba puntero sin copiar. Frágil aunque hoy use literales.
3. `alternarIR()` emitía `voz.dice()` y el llamador repetía otra frase: doble Jarvis.
4. Las rutas sala/dormitorio/cultivo/ventilador emitían `ACK;IR;...` incluso si
   `alternarIR()` ya había emitido `NACK` → ACK/NACK contradictorios.
5. `pinesUnicos()` validaba lista manual, no funciones activas. No veía alias
   buzzer/IR en GPIO12 ni DF/BOTÓN en 18 ni DF/SDA en 17.
6. `VozJarvis::begin()` configuraba GPIO12 y `beep()` lo ponía HIGH aunque
   IR/DF estuvieran off. El SVG decía “GPIO12 libre”: discrepancia activa.
7. `splash()` bloqueaba ~640 ms con `delay(40)x16`; `beep()` bloqueaba con `delay()`.

## Cambios aplicados (código)

| Archivo | Cambio | Efecto |
|---|---|---|
| `firmware/domus_esqueleto/domus_lcd.h` | `feedbackTitulo_/Sub_[17]` buffers + `snprintf`; `splash()` sin `delay`, solo título + feedback | Fin del dangling `buf`; arranque no bloqueante |
| `firmware/domus_esqueleto/domus_voice.h` | `ultima_[160]` con copia; `BUZZER_HABILITADO` gatea `begin/beep`; `beep()` programa pulsos, `actualizar()` los ejecuta sin `delay` | GPIO12 intacto si buzzer off; loop no se congela |
| `firmware/domus_esqueleto/domus_config.h` | `BUZZER_HABILITADO=false`; PIN_IR/DF marcados FINAL-ONLY; `listaActiva()/funcionesActivasSinAlias()` + `static_assert`; `PERFIL_ALFA_BOMBA_1/VENTILADOR_1` explícitos | Compilación falla si funciones HABILITADAS comparten GPIO; un motor por compilación |
| `firmware/domus_esqueleto/domus_esqueleto.ino` | `alternarIR()` solo feedback + bool; llamadores emiten UNA frase + ACK solo si `true`; `loop()` llama `voz.actualizar()`; `DOMUS_LISTO` incluye `BUZZER=` | Una Jarvis por pulsación; sin ACK tras NACK |
| `visualizaciones/domus-alfa-guia-principiantes.svg` | “GPIO12 libre” → “GPIO12 reservado, sin conectar (buzzer deshabilitado en alfa)” | Doc = firmware |
| `visualizaciones/domus-alfa-motores-s8050.svg` | Título “HISTÓRICO — NO CABLEAR”, subtítulo a `una-carga` + nota 49 | No montar 2xS8050 |
| `obsidian/proyect domus/46 - Plan maestro…` | Cultivo G11→G8, G12 reservado, nota ola 1 | Mapa candidato = firmware |
| `obsidian/proyect domus/47 - Guia visual…` | GPIO12 reservado, procedimiento PIR 3V3→medir, ref nota 50 | Guía = firmware |

## Perfiles de motor (nota 49)

```text
normal ALFA_UN_COSTADO_SIN_IR -> GPIO4 y GPIO7 bloqueados
ALFA_BOMBA_1      -> HABILITAR_MOTOR_BOMBA=true,  VENTILADOR=false (solo GPIO4)
ALFA_VENTILADOR_1 -> HABILITAR_MOTOR_VENTILADOR=true, BOMBA=false (solo GPIO7)
```

Nunca ambos en `true` (static_assert). S8550 queda en reserva, fuera del circuito.

## PIR vigente

```text
Primera prueba: VCC a 3V3.
Si no detecta movimiento:
- identificar el módulo;
- probar alimentación a 5V;
- medir OUT antes de conectarlo al ESP32;
- OUT debe permanecer ≤3.3V.
```

## Verificación pendiente (ola 1)

- [ ] Compilación N16R8/OPI sin warnings nuevos del esqueleto
- [ ] Tests contrato (LCD copia, ACK único, GPIO activos, buzzer off = GPIO12 intacto)
- [ ] `validate_project.py` actualizado a GPIO15/16/17 + `HABILITAR_MOTOR_BOMBA` (ola 2)
- [ ] HIL solo después de lo anterior

## Relaciones

- [[46 - Plan maestro de consolidacion un costado]]
- [[47 - Guia visual principiante conexiones alfa]]
- [[48 - Guia principiante transistores bomba y ventilador]]
- [[49 - Prueba de una carga con un S8050 y TP4056]]
