/*
 * PROJECT DOMUS — esqueleto del banco actual.
 * Compila literalmente el firmware de producto con el hardware disponible:
 * sensores, LCD, botones, LED, IR y una bomba mediante S8050.
 */
#define DOMUS_PERFIL_CASA 3
#define DOMUS_SALIDAS_ECONOMICAS 0
#define MICROSD_HABILITADA false

// Arduino solo genera prototipos para el .ino principal, no para un .ino
// incluido. Estas son las tres funciones que la pantalla usa antes de su
// definicion dentro del firmware de producto.
bool leerHumedad(int &crudoSalida, int &pctSalida);
bool leerLuz(int &crudoSalida, int &pctSalida);
bool leerAmbiente(float &tempCSalida, float &humAireSalida);

#include "../casa_inteligente_v4/casa_inteligente_v4.ino"
