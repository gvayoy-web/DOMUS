#pragma once
#include <stdint.h>

struct TrabajoSD {
  bool prueba;
  uint32_t momento;
  char linea[192];
};

// Los tipos usados por firmas de funciones viven en un encabezado para que el
// generador automático de prototipos de Arduino los conozca antes de declarar
// construirRespuestaJarvis() y ejecutarOrdenActuador().
enum OrigenOrden {
  ORIGEN_SISTEMA,
  ORIGEN_MANUAL,
  ORIGEN_AUTOMATICO,
  ORIGEN_IR,
  ORIGEN_WIFI
};

struct OrdenActuador {
  int indiceRele;
  bool encender;
  OrigenOrden origen;
  float confianza;
  const char* nombre;
};

struct ResultadoOrden {
  bool exito;
  bool cambioReal;
  const char* motivo;
};
