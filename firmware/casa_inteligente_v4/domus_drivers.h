#pragma once
// PROJECT DOMUS — backends de driver de motores preparados pero INACTIVOS.
//
// Estado: NINGUNO por defecto. DRV8833 y MX1508 existen solo como descriptores
// (nombre + notas de cableado futuro); no asignan GPIO ni mueven hardware.
// Puerta F1 (validacion fisica: modulo identificado por foto + chip y tabla
// medida): DRIVER_MOTORES_LISTO significa "backend seleccionado + F1 superada".
// Hoy F1 no esta superada para ningun modulo, asi que en la practica el flag
// es false porque el valor seguro predeterminado es NINGUNO. Seleccionar un
// backend por bandera (-DDOMUS_DRIVER=1/2) sin haber superado F1 esta prohibido
// por procedimiento; la bandera solo prepara la compilacion, no autoriza
// cablear ni mover motores. No se adivina cual modulo llego: default NINGUNO.
// El despachador de casa_inteligente_v4.ino no cambia: `driver_no_listo` se
// revisa antes que `salida_no_instalada`.
//
// Seleccion por bandera de compilacion:
//   -DDOMUS_DRIVER=0 -> NINGUNO (seguro, predeterminado)
//   -DDOMUS_DRIVER=1 -> DRV8833 (preparado, inactivo hasta F1)
//   -DDOMUS_DRIVER=2 -> MX1508  (preparado, inactivo hasta F1)
// Otro valor falla por static_assert.
#include <stdint.h>

#ifndef DOMUS_DRIVER
#define DOMUS_DRIVER 0
#endif

// Backend de driver separado, seleccionable por bandera. NINGUNO es el valor
// seguro predeterminado: no se adivina cual modulo llego.
enum class BackendMotor : uint8_t { NINGUNO = 0, DRV8833 = 1, MX1508 = 2 };

static_assert(DOMUS_DRIVER >= 0 && DOMUS_DRIVER <= 2,
              "DOMUS_DRIVER debe ser 0, 1 o 2");

constexpr BackendMotor BACKEND_MOTOR_SELECCIONADO =
    DOMUS_DRIVER == 1 ? BackendMotor::DRV8833 :
    DOMUS_DRIVER == 2 ? BackendMotor::MX1508 :
                        BackendMotor::NINGUNO;

constexpr const char* nombreBackendMotor(BackendMotor b) {
  return b == BackendMotor::DRV8833 ? "DRV8833" :
         b == BackendMotor::MX1508 ? "MX1508" : "NINGUNO";
}

// --- Driver de motores (puerta F1) ---
// Deriva del backend: listo solo si hay backend seleccionado. Equivale a
// (BACKEND_MOTOR_SELECCIONADO != BackendMotor::NINGUNO); la rama del valor
// seguro predeterminado se escribe como false explicito para auditoria.
#if DOMUS_DRIVER == 0
constexpr bool DRIVER_MOTORES_LISTO = false;
#else
constexpr bool DRIVER_MOTORES_LISTO = (BACKEND_MOTOR_SELECCIONADO != BackendMotor::NINGUNO);
#endif
// Orden que el driver confirmado ejecutará. Declaración del contrato;
// la definición vive en el driver de la placa identificada, no aquí.
struct OrdenMotorDriver {
  uint8_t canal;  // 0 = bomba, 1 = ventilador
  bool activar;
};
inline bool driverMotoresListo() { return DRIVER_MOTORES_LISTO; }
// Seguro por defecto: devuelve false (no mueve nada) hasta F1 superada.
// Ninguna llamada a esta funcion toca GPIO hoy.
inline bool driverMotoresAplicar(uint8_t canal, bool activar) {
  (void)canal;
  (void)activar;
  return false;
}

// --- Descriptores por backend (SIN pinouts) ---
// Solo nombre + notas de cableado futuro. Prohibido asignar GPIO aqui: el
// cableado real se define con F1, nunca antes.
struct DescriptorBackendMotor {
  const char* nombre;
  const char* notasCableadoFuturo;
};
constexpr DescriptorBackendMotor DESCRIPTOR_NINGUNO = {
  "NINGUNO",
  "Sin driver: ningun modulo adivinado; motores bloqueados hasta F1."
};
constexpr DescriptorBackendMotor DESCRIPTOR_DRV8833 = {
  "DRV8833",
  "Puente dual con entradas AIN1/AIN2/BIN1/BIN2 y pin nSLEEP; cableado futuro pendiente de F1, sin GPIO asignados."
};
constexpr DescriptorBackendMotor DESCRIPTOR_MX1508 = {
  "MX1508",
  "Puente dual con entradas IN1-IN4 y salidas OUT1-OUT4, sin pin SLEEP; cableado futuro pendiente de F1, sin GPIO asignados."
};
constexpr const DescriptorBackendMotor& descriptorBackendMotor(BackendMotor b) {
  return b == BackendMotor::DRV8833 ? DESCRIPTOR_DRV8833 :
         b == BackendMotor::MX1508 ? DESCRIPTOR_MX1508 : DESCRIPTOR_NINGUNO;
}

// --- IR CAR MP3 (puerta F4) ---
// 21 teclas del mando real. La tabla protocolo/dirección/comando se registra
// del control físico; copiar códigos de internet está prohibido (nota 46).
constexpr uint8_t IR_TOTAL_TECLAS = 21;
constexpr bool IR_CANDIDATO_HABILITADO = false;

// --- Audio Jarvis (puerta F5) ---
// Frases fijas en español vía responderJarvis() cuando exista MAX98357A en
// pines sin colisiones. MUTE nunca bloquea seguridad (nota 46).
constexpr bool AUDIO_CANDIDATO_HABILITADO = false;
