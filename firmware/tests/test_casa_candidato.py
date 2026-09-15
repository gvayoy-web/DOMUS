"""Pruebas específicas del candidato a producto (notas 53/54/55, jefatura).

casa_inteligente_v4 como único candidato: perfiles claros, mapa GPIO central
como fuente real, máscara física por perfil, driver/IR/audio preparados pero
deshabilitados y nombre diagnosticado sin la palabra FINAL. No toca el
esqueleto (congelado).
"""
import shutil
import tempfile
import unittest
from pathlib import Path
from test_native_firmware import function, run_host_process


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "firmware" / "casa_inteligente_v4" / "casa_inteligente_v4.ino"
DRIVERS = CANDIDATE.with_name("domus_drivers.h")
TEMPLATE = Path(__file__).with_name("native_integration.cpp")
SIGNATURES = [
    "int nivelSalida(int indice, bool encendida)",
    "bool verificarNivelLogicoSalida(int indice, bool estadoEsperado)",
    "bool solicitarSalida(int indice, bool anunciarPorVoz = true)",
    "bool desactivarSalida(int indice, bool anunciarPorVoz = true)",
    "ResultadoOrden ejecutarOrdenActuador(const OrdenActuador &orden)",
]


class CasaCandidatoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = CANDIDATE.read_text(encoding="utf-8")
        cls.drivers = DRIVERS.read_text(encoding="utf-8")

    def test_perfil_casa_es_seleccion_unica(self):
        self.assertIn("enum class PerfilCasa", self.source)
        for perfil in ("BANCO_SIN_ACTUADORES", "LED_SIN_MOTORES", "MOTOR_PENDIENTE_DRIVER",
                       "BANCO_COMPLETO_S8050_IR"):
            self.assertIn(perfil, self.source)
        self.assertIn("#ifndef DOMUS_PERFIL_CASA", self.source)
        self.assertIn("DOMUS_PERFIL_CASA debe ser 0, 1, 2 o 3", self.source)
        self.assertIn("constexpr PerfilCasa PERFIL_CASA =", self.source)

    def test_mapa_central_es_fuente_unica(self):
        # Nota 55: literales autorizados una sola vez, en el struct.
        bloque = self.source.split("constexpr MapaPinesCasa MAPA_CASA = {", 1)[1].split("};", 1)[0]
        for literal in ("15", "16", "17", "18"):
            self.assertIn(literal, bloque)
        for campo in ("suelo", "nivel", "ldr", "bomba", "sala", "cuarto",
                      "vent", "inv", "pir", "paro", "micOff", "ir", "demo",
                      "scl", "dht", "sda", "salidas"):
            self.assertIn(campo, self.source.split("struct MapaPinesCasa {", 1)[1].split("};", 1)[0])
        self.assertIn("MAPA_CASA.sda", self.source)
        self.assertIn("MAPA_CASA.salidas[indice]", self.source)

    def test_mascara_fisica_bloquea_sin_etapa_y_motores(self):
        self.assertIn("constexpr bool SALIDA_FISICA_CASA[TOTAL_SALIDAS]", self.source)
        self.assertIn('"salida_no_instalada"', self.source)
        self.assertIn('"driver_no_listo"', self.source)
        self.assertIn("pinMode(MAPA_CASA.salidas[i], SALIDA_FISICA_CASA[i] ? OUTPUT : INPUT);", self.source)

    def test_diagnostico_reporta_perfil_sin_final(self):
        self.assertIn("PERFIL_CANDIDATO=", self.source)
        for nombre in (
            '"CANDIDATO_BANCO_SIN_ACTUADORES"',
            '"CANDIDATO_LED_SIN_MOTORES"',
            '"CANDIDATO_MOTOR_PENDIENTE_DRIVER"',
            '"BANCO_COMPLETO_S8050_IR"',
        ):
            self.assertIn(nombre, self.source)
        self.assertNotIn('"FINAL"', self.source)

    def test_banco_actual_usa_producto_con_una_bomba_e_ir(self):
        self.assertIn("#define DOMUS_PERFIL_CASA 3", self.source)
        self.assertIn("constexpr bool BOMBA_DIRECTA_S8050", self.source)
        self.assertIn("constexpr bool IR_CASA_HABILITADO", self.source)
        self.assertIn("MAPA_CASA.ir == 12", self.source)
        self.assertIn("MAPA_CASA.micOff, MAPA_CASA.ir, MAPA_CASA.demo", self.source)
        self.assertIn("receptorIR.begin(MAPA_CASA.ir)", self.source)
        self.assertIn("revisarIRCasa();", self.source)
        self.assertIn('comando.startsWith("IR_GRABAR_")', self.source)
        self.assertIn("!(BOMBA_DIRECTA_S8050 && SALIDA_FISICA_CASA[3])", self.source)
        self.assertIn("AUDIO_CANDIDATO_HABILITADO = false", self.drivers)

    def test_ir_solo_acciona_teclas_aprendidas_y_rechaza_duplicados(self):
        ir = CANDIDATE.with_name("domus_ir_casa.h").read_text(encoding="utf-8")
        self.assertIn('getUInt("mask", 0)', ir)
        self.assertIn("aprendida(i) && tabla_[i] == codigo", ir)
        self.assertIn('ultimoError_ = "codigo_duplicado"', ir)
        self.assertIn("bool mapaCompleto() const", ir)
        self.assertIn("IR;APRENDIDAS=", self.source)
        self.assertIn("MAPA_SIN_APRENDER;SALIDAS_IR_BLOQUEADAS", self.source)
        self.assertIn("ORIGEN_IR", self.source)
        self.assertIn("if (orden.origen == ORIGEN_IR)", self.source)
        self.assertIn("responderJarvis(construirRespuestaJarvis", self.source)

    def test_prueba_guiada_y_arranque_seguro_de_bomba(self):
        self.assertIn("void emitirPruebaGuiada()", self.source)
        for token in ("PRUEBA;INICIO", "PRUEBA;LCD=", "PRUEBA;ACCIONES=", "PRUEBA;FIN"):
            self.assertIn(token, self.source)
        self.assertIn('comando == "PRUEBA"', self.source)
        self.assertIn("if (BOMBA_DIRECTA_S8050) propietarioSalidas[0] = PROPIETARIO_MANUAL_OFF;", self.source)
        self.assertIn("for (uint8_t dir = 0x08; dir <= 0x77; ++dir)", self.source)

    def test_driver_y_audio_separados_del_ir_activo(self):
        self.assertIn("#define DOMUS_DRIVER_VALIDADO 0", self.drivers)
        self.assertIn("BACKEND_MOTOR_SELECCIONADO != BackendMotor::NINGUNO", self.drivers)
        self.assertIn("DOMUS_DRIVER_VALIDADO == 1", self.drivers)
        self.assertIn("struct OrdenMotorDriver", self.drivers)
        self.assertNotIn("IR_CANDIDATO_HABILITADO", self.drivers)
        self.assertIn('#include "domus_ir_casa.h"', self.source)
        self.assertIn("constexpr bool AUDIO_CANDIDATO_HABILITADO = false;", self.drivers)
        self.assertIn('#include "domus_drivers.h"', self.source)
        self.assertIn("driverMotoresListo()", self.source)

    def run_dispatch(self, mask, driver):
        """Compila el despachador real con fakes dados y devuelve motivos impresos."""
        compiler = shutil.which("g++") or shutil.which("clang++")
        if not compiler:
            self.skipTest("No host C++ compiler; dispatch runs on Ubuntu CI")
        source = self.source
        template = TEMPLATE.read_text(encoding="utf-8")
        head, _ = template.split("// ACTUAL_FUNCTIONS", 1)
        head = head.replace(
            "constexpr bool SALIDA_FISICA_CASA[5]={true,true,true,true,true};",
            f"constexpr bool SALIDA_FISICA_CASA[5]={{{mask}}};")
        head = head.replace(
            "inline bool driverMotoresListo() { return true; }",
            f"inline bool driverMotoresListo() {{ return {str(driver).lower()}; }}")
        injected = "\n".join(function(source, s) for s in SIGNATURES)
        body = r'''
int main() {
  gpio[PIN_PARO_EMERGENCIA]=HIGH; gpio[PIN_MIC_OFF]=HIGH;
  agua=1000; sensorValido=true; micHabilitado=true;
  heap=100000; calibracion.nivelMinimo=600;
  ResultadoOrden bomba = ejecutarOrdenActuador({0,true,ORIGEN_MANUAL,1,"bomba"});
  ResultadoOrden sala = ejecutarOrdenActuador({1,true,ORIGEN_MANUAL,1,"sala"});
  std::puts(bomba.exito ? "BOMBA_OK" : bomba.motivo);
  std::puts(sala.exito ? "SALA_OK" : sala.motivo);
  return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix="domus-dispatch-") as directory:
            cpp = Path(directory) / "test.cpp"
            cpp.write_text(head + injected + body, encoding="utf-8")
            binary = Path(directory) / "test.exe"
            result = run_host_process([compiler, "-std=c++17", "-Wall", "-Wextra",
                                       "-I", str(CANDIDATE.parent),
                                       str(cpp), "-o", str(binary)], timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = run_host_process([str(binary)], timeout=10, allow_skip=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return result.stdout.decode().split()

    def test_despacho_distinque_driver_de_etapa(self):
        # Máscara presente + driver ausente: el motor cae por driver, la luz pasa.
        motivos = self.run_dispatch("true,true,true,true,true", False)
        self.assertEqual(motivos[0], "driver_no_listo")
        self.assertEqual(motivos[1], "SALA_OK")
        # Máscara ausente + driver listo: el motor cae por etapa del perfil.
        motivos = self.run_dispatch("false,false,false,false,false", True)
        self.assertEqual(motivos[0], "salida_no_instalada")
        self.assertEqual(motivos[1], "salida_no_instalada")


if __name__ == "__main__":
    unittest.main(verbosity=2)
