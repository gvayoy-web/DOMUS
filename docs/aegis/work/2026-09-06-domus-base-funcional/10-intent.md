# Intencion

Resultado solicitado: convertir `firmware/domus_esqueleto` en una base funcional
para probar el hardware confirmado, consolidar la ruta recomendada y cubrirla
con pruebas y CI.

Alcance: ESP32-S3, LCD, DHT, ADC, PIR, botones, bomba, LED y ventilador.
No objetivos: activar voz, SD, red, bateria o solar; retirar el firmware principal;
declarar validacion fisica sin banco.

Referencias: inventario Obsidian 01, manual 18, metas 32, firmware principal y
README previo del esqueleto. La decision mantiene compatibilidad por comandos y
preserva el firmware principal como referencia hasta alcanzar paridad fisica.
