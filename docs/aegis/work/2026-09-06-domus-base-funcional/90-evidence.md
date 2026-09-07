# Evidencia

- Arduino CLI, ESP32-S3 N16R8/OPI, warnings all: PASS; 373286 bytes de programa,
  24388 bytes globales.
- `scripts/validate_project.py`: PASS; 49 pruebas correctas y 5 C++ omitidas
  explicitamente por no existir compilador host en Windows.
- Entrenador IA, ejecutado antes del cambio: 16 pruebas PASS; no afectado.
- `git diff --check`: PASS.
- No cubierto: GPIO reales, polaridades, fuente, cargas, calibracion, 24 h/1000 ciclos.
