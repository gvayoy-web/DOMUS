---
proyecto: PROJECT DOMUS
tipo: construccion
actualizado: 2026-09-01
---

# Materiales de maqueta y exposición

## Estructura

- Base de 100 × 65 cm: MDF de 12 mm según la lista de corte vigente; alternativa provisional, doble cartón corrugado con vetas cruzadas.
- Vivienda de 43 × 32.5 cm, paredes de 22.5 cm de alto y techo removible de 44.6 × 34.1 cm.
- Invernadero de 25 × 35 cm.
- Torre Jarvis de 10.5 × 29 cm y bahía electrónica contigua.
- Entrada cubierta aproximada de 25 × 19.5 cm.

## Materiales físicos todavía no confirmados

| Material | Cantidad orientativa | Uso |
|---|---:|---|
| MDF/cartón base | 1 pieza 100×65 cm | Base rígida. |
| Plywood/cartón paredes | según plano | Casa y divisiones. |
| Acrílico transparente | 1–2 láminas | Invernadero y tapa electrónica. |
| Listones/bajantes reciclados | lote | Refuerzos y techo. |
| Pintura negra, azul, blanca y tonos madera | 1 set | Identidad DOMUS. |
| Sellador/barniz al agua | 1 | Protege cartón/madera. |
| Silicón caliente | varias barras | Montaje no estructural y cables. |
| Pegamento de madera/contacto | 1 | Paredes y base. |
| Cinta doble cara/aislante | 1 de cada | Módulos y aislamiento. |
| Bridas | 20+ | Gestión de cable. |
| Separadores M3, tornillos y tuercas | lote | ESP32, relés y tapas. |
| Depósito plástico cerrado | 1 | Agua de riego. |
| Bandeja impermeable | 1 | Contención de fugas. |
| Tierra y plantas pequeñas | según invernadero | Demostración. |
| Cartulina/foamboard impreso | según banners | Etiquetas y explicación. |

## Herramientas que deben estar disponibles

- Multímetro — confirmado.
- Cautín y soporte.
- Estaño y flux.
- Pelacables/cortador.
- Pistola de silicón.
- Regla metálica, escuadra y cúter.
- Taladro manual/minitaladro si se usa plywood/acrílico.
- Destornilladores pequeños.
- Termorretráctil o cinta aislante.

## Qué mostrar al público

1. Sensores reales cambiando valores en LCD.
2. Una orden manual/USB Serial que pasa por el mismo despachador que la automatización.
3. Riego por humedad con corte seguro.
4. Funcionamiento local al desconectar Wi-Fi.
5. Jarvis solo si supera las pruebas; de lo contrario, explicar su arquitectura y usar respaldo de botón/USB Serial.
6. Ruta de energía visible y separada del agua.
7. Panel solar presentado como recarga medida, no decoración ni autosuficiencia inventada.
8. Gemelo digital v3 en la vista Radiografía para explicar agua, energía, señal, sensores y piezas removibles.
9. Juego de planos A3 v3 abierto en planta, esquema eléctrico o riego según la explicación del momento.

## Recursos visuales terminados

- Visor offline: `assets/new/deliverables/execute/01_FINAL_V2/design/modelo_3d_interactivo.html`.
- Plano A3 de seis páginas: `output/pdf/planos_tecnicos_project_domus.pdf`.
- Capturas verificadas: `visor_desktop_1440x900.png`, `visor_mobile_390x844.png` y `visor_mobile_390x844_cerrado.png`.
- Renders: general, interior sin techo y vista explotada dentro de `01_FINAL_V2/design`.
- Modelo editable: `project_domus.obj` y `project_domus.mtl`.

## Etiquetas recomendadas

- ESP32-S3 — controlador local.
- LCD1602 — estado del sistema.
- DHT — ambiente.
- PIR — presencia.
- LDR — luz ambiental.
- Humedad de suelo — decisión de riego.
- Nivel de agua — protección del depósito.
- Relés — separación entre control y cargas.
- Jarvis — voz local limitada y segura.
- Fusible / corte general — seguridad.
