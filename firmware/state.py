# ============================================================
# USS SPIDERBOT — Registro de Estado Global Compartido
# Solemne 3 — Taller de Programación I
# ============================================================
# Este archivo centraliza el estado en tiempo real del robot,
# permitiendo la comunicación bidireccional asíncrona entre
# el bucle de locomoción (main.py) y el servidor web (web_server.py)
# sin incurrir en problemas de importación circular en MicroPython.
# ============================================================

# Comando de movimiento actual ("forward", "backward", "left", "right", "stop", "reposo")
comando_actual = "stop"

# Interruptor de la compensación inercial por acelerómetro
estabilizacion_activa = True

# Variables físicas medidas por los sensores actualizadas a 20Hz
pitch_actual = 0.0
roll_actual = 0.0
distancia_actual = 100.0
