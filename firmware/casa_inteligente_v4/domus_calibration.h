#pragma once
#include <stdint.h>

struct CalibracionDomus {
  uint16_t version;
  uint16_t sueloSeco;
  uint16_t sueloHumedo;
  uint16_t luzOscura;
  uint16_t luzClara;
  uint16_t nivelMinimo;
  uint32_t checksum;
};

inline uint32_t checksumCalibracion(const CalibracionDomus &c) {
  const uint16_t valores[] = {c.version, c.sueloSeco, c.sueloHumedo,
                             c.luzOscura, c.luzClara, c.nivelMinimo};
  uint32_t hash = 2166136261u;
  for (uint16_t valor : valores) {
    hash = (hash ^ (valor & 255)) * 16777619u;
    hash = (hash ^ (valor >> 8)) * 16777619u;
  }
  return hash;
}

inline bool calibracionValida(const CalibracionDomus &c) {
  int suelo = int(c.sueloSeco) - int(c.sueloHumedo);
  int luz = int(c.luzOscura) - int(c.luzClara);
  return c.version == 1 && c.sueloSeco >= 50 && c.sueloSeco <= 4045 &&
    c.sueloHumedo >= 50 && c.sueloHumedo <= 4045 &&
    c.luzOscura >= 16 && c.luzOscura <= 4079 &&
    c.luzClara >= 16 && c.luzClara <= 4079 &&
    c.nivelMinimo >= 16 && c.nivelMinimo <= 4079 &&
    (suelo >= 100 || suelo <= -100) && (luz >= 100 || luz <= -100);
}
