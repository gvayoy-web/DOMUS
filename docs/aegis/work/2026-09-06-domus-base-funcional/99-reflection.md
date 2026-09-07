# Reflexion

La logica comprobable quedo en `domus_control.h` y el sketch conserva el papel
de adaptador de hardware. El firmware principal se retiene porque aun contiene
capacidades y evidencia historica no reemplazadas fisicamente. Criterio de retiro:
B01-B10 aprobados y comparacion de paridad sin regresiones. El riesgo principal
restante es electrico, no de compilacion.
