# ============================================================
# USS SPIDERBOT — Bucle Principal y Estabilización Activa (Asíncrono)
# Solemne 3 — Taller de Programación I
# Microcontrolador: ESP32
# Lenguaje: MicroPython
# ============================================================

from machine import I2C, Pin, PWM
import time
import uasyncio as asyncio
import sys
import select
import state
from mpu6050 import MPU6050
from sonar_sensor import SonarSensor
from buzzer_alert import BuzzerAlert

class ESP32ServoDirect:
    """
    Controlador fallback de servos conectado directamente a pines GPIO de la ESP32.
    Se utiliza en el simulador Wokwi para emular el comportamiento del chip PCA9685.
    """
    def __init__(self, channels_pins):
        self.pwms = {}
        for ch, pin_num in channels_pins.items():
            try:
                # Frecuencia de 50Hz para servomotores analógicos estándar
                pwm = PWM(Pin(pin_num), freq=50)
                self.pwms[ch] = pwm
            except Exception as e:
                print(f"[WARNING] No se pudo iniciar PWM en GPIO {pin_num}:", e)

    def set_servo_angle(self, channel, angle):
        if channel in self.pwms:
            # 50Hz -> Período = 20ms.
            # Ciclo de trabajo típico para servos SG90 (0.5ms a 2.5ms de ancho de pulso):
            # 0.5ms / 20ms = 2.5% -> 0.025 * 65535 = 1638 ticks
            # 2.5ms / 20ms = 12.5% -> 0.125 * 65535 = 8192 ticks
            min_duty = 1638
            max_duty = 8192
            
            # Clampear ángulo entre 0 y 180
            angle = max(0, min(180, angle))
            
            duty = int(min_duty + (angle / 180.0) * (max_duty - min_duty))
            self.pwms[channel].duty_u16(duty)

# ── 1. Inicialización de Interfaces ──────────────────────────────
print("Iniciando bus I2C (SDA=21, SCL=22) para IMU...")
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)

dispositivos = i2c.scan()
print("Dispositivos I2C detectados: ", [hex(d) for d in dispositivos])

# ── 2. Inicialización de Drivers ────────────────────────────────
# Mapeo de canales a pines GPIO físicos en la ESP32 (Control Directo)
channels_pins = {
    0: 13, 1: 12, # Pata 0 (FR)
    2: 15, 3: 2,  # Pata 1 (FL)
    4: 4,  5: 5,  # Pata 2 (RL)
    6: 23, 7: 25  # Pata 3 (RR)
}

print("Inicializando controlador de servos directo por GPIO...")
servos = ESP32ServoDirect(channels_pins)

# Auto-detectar si estamos corriendo en el simulador Wokwi buscando la red virtual
modo_simulacion = False
try:
    import network
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    print("Escaneando redes Wi-Fi para auto-detectar simulador...")
    redes = sta.scan()
    ssids = [r[0].decode('utf-8') for r in redes]
    if "Wokwi-GUEST" in ssids:
        print("[INFO] Red 'Wokwi-GUEST' detectada. Entorno: SIMULADOR WOKWI.")
        modo_simulacion = True
    else:
        print("[INFO] Red 'Wokwi-GUEST' no detectada. Entorno: HARDWARE REAL.")
except Exception as e:
    print("[WARNING] Falló escaneo de red para auto-detección:", e)

try:
    imu = MPU6050(i2c, address=0x68)
    print("[OK] Acelerómetro (MPU6050) configurado.")
    # Intentar cargar los offsets de calibración guardados
    try:
        with open("mpu_offsets.txt", "r") as f:
            linea = f.read().strip()
            ox, oy, oz = [int(v) for v in linea.split(",")]
            imu.set_offsets(ox, oy, oz)
            print(f"[OK] Offsets de IMU cargados: X={ox}, Y={oy}, Z={oz}")
    except OSError:
        print("[WARNING] No se encontró mpu_offsets.txt. Usando offsets por defecto (0,0,0).")
except Exception as e:
    print("[ERROR] No se pudo iniciar el MPU6050: ", e)
    imu = None

sonar = SonarSensor(trigger_pin=18, echo_pin=19)
alarma = BuzzerAlert(pin_number=14)

alarma.play_startup() # Melodía rítmica de inicio para buzzer activo

# ── 3. Definición de Canales de Servos y Poses ─────────────────────
COXA_CHANNELS = [0, 2, 4, 6]
FEMUR_CHANNELS = [1, 3, 5, 7]

# Ángulos base para posición de reposo (Standing Pose)
ANGULO_COXA_BASE = 90  # Todos centrados

# Los servos de la izquierda están invertidos mecánicamente respecto a la derecha
ANGULO_FEMUR_DER_BASE = 60   # Patas 0 y 3 (Canales 1 y 7)
ANGULO_FEMUR_IZQ_BASE = 120  # Patas 1 y 2 (Canales 3 y 5)

# Registro del estado actual de los ángulos de los servos para interpolaciones
estado_coxas = [90, 90, 90, 90]
estado_femures = [60, 120, 120, 60]

def pos_reposo():
    """Lleva a todos los servos del cuadrúpedo a su pose de reposo estático aplicando estabilización activa."""
    global estado_coxas, estado_femures
    if not servos: return
    
    estado_coxas = [90, 90, 90, 90]
    estado_femures = [60, 120, 120, 60]
    
    # Mover patas aplicando la función de estabilización inercial activa
    establecer_angulo_pata(0, 90, 60)
    establecer_angulo_pata(1, 90, 120)
    establecer_angulo_pata(2, 90, 120)
    establecer_angulo_pata(3, 90, 60)

# Establecer pose inicial al arrancar
pos_reposo()

# ── 4. Compensación e Inferencia de Postura (IA Reactiva) ──────────
PITCH_TOLERANCIA = 3.0      # Tolerancia de grados antes de actuar
ROLL_TOLERANCIA = 3.0
FACTOR_COMPENSACION = 1.2   # Escala de respuesta correctora por grado de inclinación

def establecer_angulo_pata(indice, coxa_ang, femur_ang):
    """Establece los ángulos de una pata aplicando compensación inercial si está en apoyo."""
    if not servos: return
    
    # Si el fémur está en posición de apoyo (no levantado en swing), se aplica la compensación
    es_apoyo = abs(femur_ang - 90) > 10
    
    if state.estabilizacion_activa and es_apoyo and (abs(state.pitch_actual) > PITCH_TOLERANCIA or abs(state.roll_actual) > ROLL_TOLERANCIA):
        correc_pitch = state.pitch_actual * FACTOR_COMPENSACION
        correc_roll = state.roll_actual * FACTOR_COMPENSACION
        
        # Aplicar correcciones según la posición física de la pata
        if indice == 0:    # Delantera Derecha (FR)
            femur_ang = femur_ang - correc_pitch - correc_roll
        elif indice == 1:  # Delantera Izquierda (FL)
            femur_ang = femur_ang + correc_pitch - correc_roll
        elif indice == 2:  # Trasera Izquierda (RL)
            femur_ang = femur_ang - correc_pitch + correc_roll
        elif indice == 3:  # Trasera Derecha (RR)
            femur_ang = femur_ang + correc_pitch + correc_roll
            
    # Límites físicos de seguridad para los servos SG90 (15° a 165°)
    femur_ang = max(15, min(165, int(femur_ang)))
    coxa_ang = max(15, min(165, int(coxa_ang)))
    
    servos.set_servo_angle(COXA_CHANNELS[indice], coxa_ang)
    servos.set_servo_angle(FEMUR_CHANNELS[indice], femur_ang)

async def mover_suave_ciclo(coxa_targets, femur_targets, pasos=4, delay_ms=25):
    """Interpola los ángulos suavemente mientras monitorea obstáculos de forma asíncrona."""
    global estado_coxas, estado_femures
    for paso in range(1, pasos + 1):
        # Monitorear sensor ultrasónico por seguridad
        if 0.0 < state.distancia_actual < 15.0:
            return False  # Abortar movimiento inmediatamente por obstáculo
            
        t = paso / pasos
        for i in range(4):
            c_ang = estado_coxas[i] + (coxa_targets[i] - estado_coxas[i]) * t
            f_ang = estado_femures[i] + (femur_targets[i] - estado_femures[i]) * t
            establecer_angulo_pata(i, c_ang, f_ang)
        await asyncio.sleep_ms(delay_ms)
        
    estado_coxas = list(coxa_targets)
    estado_femures = list(femur_targets)
    return True

# ── 5. Definición de Marchas de Locomoción Asíncronas ──────────────

async def caminar_adelante():
    """Ejecuta un ciclo completo de marcha de gateo (Crawl Gait) hacia adelante."""
    if not await mover_suave_ciclo([70, 110, 110, 70], [60, 120, 120, 60], pasos=5):
        return False
        
    if not await mover_suave_ciclo([70, 110, 110, 70], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 110, 70], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 110, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    if not await mover_suave_ciclo([110, 110, 110, 70], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 110, 110], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 110, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    if not await mover_suave_ciclo([110, 110, 110, 110], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 110, 110], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 110, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    if not await mover_suave_ciclo([110, 70, 110, 110], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 70, 110], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 70, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    return True

async def caminar_atras():
    """Ejecuta un ciclo completo de marcha de gateo (Crawl Gait) hacia atrás."""
    if not await mover_suave_ciclo([110, 70, 70, 110], [60, 120, 120, 60], pasos=5):
        return False
        
    if not await mover_suave_ciclo([110, 70, 70, 110], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 70, 110], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 70, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    if not await mover_suave_ciclo([70, 70, 70, 110], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 70, 70], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 70, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    if not await mover_suave_ciclo([70, 70, 70, 70], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 70, 70], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 70, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    if not await mover_suave_ciclo([70, 110, 70, 70], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 110, 70], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 110, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    return True

async def girar_izquierda():
    """Ejecuta un ciclo de rotación sobre su propio eje en sentido antihorario."""
    if not await mover_suave_ciclo([70, 70, 70, 70], [60, 120, 120, 60], pasos=5):
        return False
        
    if not await mover_suave_ciclo([70, 70, 70, 70], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 70, 70], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 70, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    if not await mover_suave_ciclo([110, 70, 70, 70], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 70, 110], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 70, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    if not await mover_suave_ciclo([110, 70, 70, 110], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 70, 110], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 70, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    if not await mover_suave_ciclo([110, 110, 70, 110], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 110, 110], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 110, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    return True

async def girar_derecha():
    """Ejecuta un ciclo de rotación sobre su propio eje en sentido horario."""
    if not await mover_suave_ciclo([110, 110, 110, 110], [60, 120, 120, 60], pasos=5):
        return False
        
    if not await mover_suave_ciclo([110, 110, 110, 110], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 110, 110], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 110, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    if not await mover_suave_ciclo([70, 110, 110, 110], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 110, 70], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 110, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    if not await mover_suave_ciclo([70, 110, 110, 70], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 110, 70], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 110, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    if not await mover_suave_ciclo([70, 70, 110, 70], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 70, 70], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 70, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    return True

# ── 6. Tareas Coactivas Asíncronas (Tasks) ─────────────────────────

async def sensor_updater():
    """Actualiza continuamente los valores de telemetría de sensores a 20Hz."""
    print("Iniciando tarea de monitoreo de sensores (20Hz)...")
    loop_count = 0
    while True:
        # 1. Medir distancia ultrasónica
        state.distancia_actual = sonar.medir_distancia()
        
        # 2. Medir inclinación MPU6050
        if imu:
            try:
                state.pitch_actual, state.roll_actual = imu.obtener_inclinacion()
                
                # Alerta inercial si el robot se inclina peligrosamente (>15 grados)
                if abs(state.pitch_actual) > 15.0 or abs(state.roll_actual) > 15.0:
                    alarma.alerta_postura()
            except Exception as e:
                pass # Silenciar fallas momentáneas de lectura I2C
                
        # Imprimir telemetría en consola una vez cada 2 segundos (40 ciclos)
        loop_count = (loop_count + 1) % 40
        if loop_count == 0:
            print(f"[IMU] Pitch: {state.pitch_actual:.1f}°, Roll: {state.roll_actual:.1f}° | [Sonar]: {state.distancia_actual:.1f} cm | Cmd: {state.comando_actual}")
            
        await asyncio.sleep_ms(50)

async def locomotion_loop():
    """Supervisa y procesa el estado actual del comando de movimiento."""
    print("Iniciando tarea de control de locomoción...")
    while True:
        # A. Prevención de colisión inmediata reactiva local
        if 0.0 < state.distancia_actual < 15.0:
            print("[ALERTA] Obstáculo crítico! Deteniendo cuadrúpedo de inmediato.")
            alarma.play_critical_alert() # Alerta crítica rítmica
            pos_reposo()
            state.comando_actual = "stop"
            await asyncio.sleep_ms(1000)
            continue
            
        # B. Selección de marcha según estado
        cmd = state.comando_actual
        if cmd == "forward":
            marchando = await caminar_adelante()
            if not marchando:
                print("[ALERTA] Marcha adelante cancelada por obstáculo.")
                alarma.play_warning_alert() # Alerta de advertencia corta
                pos_reposo()
                state.comando_actual = "stop"
                await asyncio.sleep_ms(500)
        elif cmd == "backward":
            marchando = await caminar_atras()
            if not marchando:
                print("[ALERTA] Marcha atrás cancelada por obstáculo.")
                alarma.play_warning_alert() # Alerta de advertencia corta
                pos_reposo()
                state.comando_actual = "stop"
                await asyncio.sleep_ms(500)
        elif cmd == "left":
            marchando = await girar_izquierda()
            if not marchando:
                pos_reposo()
                state.comando_actual = "stop"
                await asyncio.sleep_ms(500)
        elif cmd == "right":
            marchando = await girar_derecha()
            if not marchando:
                pos_reposo()
                state.comando_actual = "stop"
                await asyncio.sleep_ms(500)
        elif cmd == "reposo":
            pos_reposo()
            while state.comando_actual == "reposo":
                await asyncio.sleep_ms(100)
        else:
            # Comando "stop" o apagado: aplicar pose de reposo (auto-estabilizada en loop)
            pos_reposo()
            await asyncio.sleep_ms(100)

async def serial_listener():
    """Escucha comandos de consola serie (Thonny/Wokwi) de forma no bloqueante."""
    # Esperar un momento a que las otras tareas inicien e impriman sus mensajes
    await asyncio.sleep_ms(1000)
    print("\n====================================================================")
    print("[SERIAL] Consola serie activa para control directo de simulación.")
    print("         Escribe: 'forward', 'backward', 'left', 'right', 'stop'")
    print("                  'reposo' o 'stabilize' y pulsa Enter.")
    print("====================================================================\n")
    
    spoll = select.poll()
    spoll.register(sys.stdin, select.POLLIN)
    
    while True:
        if spoll.poll(0):
            line = sys.stdin.readline().strip().lower()
            if line in ["forward", "backward", "left", "right", "stop", "reposo"]:
                state.comando_actual = line
                print(f"[CONSOLA] Comando cambiado a: {line}")
                alarma.play_warning_alert() # Beep corto de confirmación
            elif line == "stabilize":
                state.estabilizacion_activa = not state.estabilizacion_activa
                print(f"[CONSOLA] Estabilización activa set a: {state.estabilizacion_activa}")
                alarma.play_warning_alert() # Beep corto de confirmación
            else:
                print(f"[CONSOLA] Comando desconocido: '{line}'")
        await asyncio.sleep_ms(100)

async def main_async():
    """Punto de entrada principal para orquestar la concurrencia."""
    from web_server import iniciar_wifi, start_server_task
    
    # Configuración de Wi-Fi adaptativa
    if modo_simulacion:
        print("[INFO] Simulación detectada. Conectando a red virtual Wokwi (SSID: Wokwi-GUEST)...")
        ip = iniciar_wifi(ssid="Wokwi-GUEST", password=None, modo_ap=False)
    else:
        ip = iniciar_wifi(ssid="USS_SpiderBot_AP", modo_ap=True)
    
    # Crear tareas concurrentes en el event loop
    task_sensors = asyncio.create_task(sensor_updater())
    task_locomotion = asyncio.create_task(locomotion_loop())
    task_server = asyncio.create_task(start_server_task(ip))
    task_serial = asyncio.create_task(serial_listener())
    
    print("\n[OK] USS SpiderBot completamente operativo e interactivo.")
    
    # Unir tareas para ejecución indeterminada
    await asyncio.gather(task_sensors, task_locomotion, task_server, task_serial)

# ── 7. Ejecución del Bucle de Eventos ──────────────────────────────
try:
    asyncio.run(main_async())
except AttributeError:
    # Compatibilidad con motores antiguos de MicroPython
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_async())
except KeyboardInterrupt:
    print("\n[INFO] Ejecución detenida por teclado por el operador.")
finally:
    print("Apagando motores y liberando puertos...")
    # Intento de llevar a reposo (puede fallar si no hay PWM ya activo)
    try:
        pos_reposo()
    except:
        pass
    try:
        alarma.play_shutdown() # Melodía rítmica de apagado para buzzer activo
    except:
        pass
    alarma.apagar()
