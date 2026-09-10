"""Pruebas hardware-in-the-loop contra el esqueleto real (COM9, 115200).

No flashean nada: hablan con el firmware ya cargado y verifican su
comportamiento de verdad (serie, salidas LED, IR, seguridad).
Solo tocan salidas clase LED (SALA/CUARTO/INVERNADERO) y restauran todo OFF;
nunca BOMBA/VENTILADOR (pueden mover motores reales).
Sin placa conectada: SKIP explícito, no FAIL.
Puerto: env DOMUS_PORT (defecto COM9).
"""
import os
import time
import unittest

try:
    import serial
except ImportError:  # pragma: no cover
    serial = None

PORT = os.environ.get("DOMUS_PORT", "COM9")
BAUD = 115200
LED_OUTS = ("SALA", "CUARTO", "INVERNADERO")


class Board:
    def __init__(self, port):
        self.ser = serial.Serial(port, BAUD, timeout=0.2)
        time.sleep(0.5)
        self.ser.reset_input_buffer()
        time.sleep(1.5)
        while self.ser.in_waiting:
            self.ser.readline()

    def cmd(self, text, wait=2.5, keep_sensores=False):
        self.ser.write((text + "\n").encode())
        end = time.time() + wait
        got = []
        while time.time() < end:
            line = self.ser.readline().decode("utf-8", "replace").strip()
            if not line:
                continue
            if line.startswith("SENSORES;") and not keep_sensores:
                continue
            got.append(line)
        return got

    def close(self):
        self.ser.close()


def find(lines, prefix):
    return [line for line in lines if line.startswith(prefix)]


class HilEsqueletoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if serial is None:
            raise unittest.SkipTest("sin pyserial")
        try:
            cls.board = Board(PORT)
        except Exception as error:
            raise unittest.SkipTest(f"sin placa en {PORT}: {error}")
        ident = cls.board.cmd("DIAGNOSTICO")
        if not find(ident, "DIAGNOSTICO;PLACA=ESP32-S3-N16R8"):
            cls.board.close()
            raise unittest.SkipTest(f"sin firmware DOMUS en {PORT}")
        first = find(cls.board.cmd("ESTADO"), "ESTADO;")
        assert first, "sin respuesta ESTADO"
        cls.vol_inicial = first[0].split("VOL=")[1].split(";")[0]

    @classmethod
    def tearDownClass(cls):
        try:
            for out in LED_OUTS:
                cls.board.cmd(f"{out} OFF", wait=1.0)
            cls.board.cmd("MODO AUTO", wait=1.0)
            cls.board.cmd("MUTE OFF", wait=1.0)
            cls.board.cmd("PAGINA 0", wait=1.0)
            vol = cls.board.cmd("ESTADO")
            if vol:
                actual = vol[0].split("VOL=")[1].split(";")[0]
                while int(actual) < int(cls.vol_inicial):
                    cls.board.cmd("VOL+", wait=0.6)
                    actual = str(int(actual) + 2)
                while int(actual) > int(cls.vol_inicial):
                    cls.board.cmd("VOL-", wait=0.6)
                    actual = str(int(actual) - 2)
        finally:
            cls.board.close()

    def test_identidad_y_diagnostico_completo(self):
        resp = self.board.cmd("DIAGNOSTICO", wait=4.0)
        self.assertTrue(find(resp, "DIAGNOSTICO;PLACA=ESP32-S3-N16R8;PERFIL=BANCO_IR_LCD"))
        for pref in ("ESTADO;PARO=", "SALUD;HEAP=", "BANCO;PLACA="):
            self.assertTrue(find(resp, pref), pref)

    def test_estado_reporta_modo_volumen_y_salidas(self):
        resp = find(self.board.cmd("ESTADO"), "ESTADO;")
        self.assertTrue(resp)
        for campo in ("MODO=", "VOL=", "OUT=", "CAL=", "TX_OMITIDOS="):
            self.assertIn(campo, resp[0])

    def test_tabla_ir_completa_21_teclas(self):
        resp = self.board.cmd("IR LISTA", wait=6.0)
        teclas = find(resp, "IR;TECLA=")
        self.assertEqual(len(teclas), 21, [line for line in resp if line.startswith("IR;")])

    def test_comando_invalido_y_linea_larga_se_rechazan(self):
        self.assertIn("NACK;COMANDO_DESCONOCIDO", self.board.cmd("HOLA"))
        self.assertIn("NACK;LINEA_INVALIDA", self.board.cmd("X" * 60))

    def test_toggle_sala_ida_y_vuelta_con_estado(self):
        self.assertIn("ACK;SALIDA", self.board.cmd("SALA ON"))
        out = find(self.board.cmd("ESTADO"), "ESTADO;")
        self.assertIn("OUT=01000", out[0])
        self.assertIn("ACK;SALIDA", self.board.cmd("SALA OFF"))
        out = find(self.board.cmd("ESTADO"), "ESTADO;")
        self.assertIn("OUT=00000", out[0])

    def test_paro_bloquea_y_rearme_libera(self):
        estado = find(self.board.cmd("ESTADO"), "ESTADO;")[0]
        if "PARO=1" in estado:
            raise unittest.SkipTest("botón PARO físico presionado")
        self.assertIn("ACK;PARO", self.board.cmd("PARO"))
        resp = self.board.cmd("SALA ON")
        self.assertTrue(any("paro" in line for line in resp), resp)
        self.assertIn("ACK;REARMAR;SALIDAS_OFF", self.board.cmd("REARMAR"))

    def test_volumen_mute_pagina_y_modo(self):
        self.assertTrue(find(self.board.cmd("VOL+"), "ACK;VOL="))
        self.assertTrue(find(self.board.cmd("VOL-"), "ACK;VOL="))
        self.assertIn("ACK;MUTE=1", self.board.cmd("MUTE ON"))
        self.assertIn("ACK;MUTE=0", self.board.cmd("MUTE OFF"))
        self.assertTrue(find(self.board.cmd("PAGINA 2"), "ACK;PAGINA=2"))
        self.assertIn("ACK;MODO;MANUAL", self.board.cmd("MODO MANUAL"))
        estado = find(self.board.cmd("ESTADO"), "ESTADO;")[0]
        self.assertIn("MODO=MANUAL", estado)

    def test_sensores_transmiten_con_validez(self):
        resp = self.board.cmd("ESTADO", wait=3.0, keep_sensores=True)
        sens = find(resp, "SENSORES;")
        self.assertTrue(sens, "sin streaming SENSORES")
        for flag in ("VS=", "VN=", "VL=", "VA="):
            self.assertIn(flag, sens[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
