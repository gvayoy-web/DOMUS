#pragma once
// PROJECT DOMUS — interfaces futuras del candidato (nota 53, jefatura).
//
// Driver de motores, IR y audio por cola, con hardware pendiente
// DESHABILITADO. Nada de este archivo mueve GPIO hoy: documenta los contratos
// que el perfil FINAL usará cuando se superen F1 (driver), F4 (IR) y F5 (audio).
// El candidato compila y opera completo con todo en false.
#include <stdint.h>

// --- Driver de motores (puerta F1) ---
// false hasta identificar el módulo pedido (foto + chip + tabla medida).
// Cuando F1 pase, este flag y la máscara SALIDA_FISICA_CASA cambian juntos.
constexpr bool DRIVER_MOTORES_LISTO = false;
// Orden que el driver confirmado ejecutará. Declaración del contrato;
// la definición vive en el driver de la placa identificada, no aquí.
struct OrdenMotorDriver {
  uint8_t canal;  // 0 = bomba, 1 = ventilador
  bool activar;
};
inline bool driverMotoresListo() { return DRIVER_MOTORES_LISTO; }

// --- IR CAR MP3 (puerta F4) ---
// 21 teclas del mando real. La tabla protocolo/dirección/comando se registra
// del control físico; copiar códigos de internet está prohibido (nota 46).
constexpr uint8_t IR_TOTAL_TECLAS = 21;
constexpr bool IR_CANDIDATO_HABILITADO = false;

// --- Audio Jarvis (puerta F5) ---
// Frases fijas en español vía responderJarvis() cuando exista MAX98357A en
// pines sin colisiones. MUTE nunca bloquea seguridad (nota 46).
constexpr bool AUDIO_CANDIDATO_HABILITADO = false;
