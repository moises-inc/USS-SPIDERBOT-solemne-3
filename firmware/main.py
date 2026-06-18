# ============================================================
# USS SPIDERBOT — Bucle Principal y Estabilización Activa (Asíncrono)
# Solemne 3 — Taller de Programación I
# Microcontrolador: ESP32
# Lenguaje: MicroPython
# ============================================================

from machine import I2C, Pin
import time
import uasyncio as asyncio
import state
from pca9685 import PCA9685
from mpu6050 import MPU6050
from sonar_sensor import SonarSensor
from buzzer_alert import BuzzerAlert

# ── 1. Inicialización de Interfaces ──────────────────────────────
print("Iniciando bus I2C (SDA=21, SCL=22)...")
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)

dispositivos = i2c.scan()
print("Dispositivos I2C detectados: ", [hex(d) for d in dispositivos])

# ── 2. Inicialización de Drivers ────────────────────────────────
try:
    servos = PCA9685(i2c, address=0x40)
    print("[OK] Servomotores (PCA9685) configurados.")
except Exception as e:
    print("[ERROR] No se pudo iniciar el PCA9685: ", e)
    servos = None

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

alarma.beep(300) # Beep de encendido exitoso

# ── 3. Definición de Canales de Servos y Poses ─────────────────────
# Patas: 0 (Delantera Derecha), 1 (Delantera Izquierda), 2 (Trasera Izquierda), 3 (Trasera Derecha)
# Canales PCA9685:
# Pata 0 -> Coxa: Ch 0, Femur: Ch 1
# Pata 1 -> Coxa: Ch 2, Femur: Ch 3
# Pata 2 -> Coxa: Ch 4, Femur: Ch 5
# Pata 3 -> Coxa: Ch 6, Femur: Ch 7

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
    """Lleva a todos los servos del cuadrúpedo a su pose de reposo estático."""
    global estado_coxas, estado_femures
    if not servos: return
    
    estado_coxas = [90, 90, 90, 90]
    estado_femures = [60, 120, 120, 60]
    
    # Mover caderas a 90 grados
    for ch in COXA_CHANNELS:
        servos.set_servo_angle(ch, ANGULO_COXA_BASE)
        
    # Mover muslos a sus ángulos base
    servos.set_servo_angle(1, ANGULO_FEMUR_DER_BASE)
    servos.set_servo_angle(7, ANGULO_FEMUR_DER_BASE)
    servos.set_servo_angle(3, ANGULO_FEMUR_IZQ_BASE)
    servos.set_servo_angle(5, ANGULO_FEMUR_IZQ_BASE)

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
    # 1. Fase de empuje del cuerpo (Stance Shift): todos los Coxas van hacia atrás
    if not await mover_suave_ciclo([70, 110, 110, 70], [60, 120, 120, 60], pasos=5):
        return False
        
    # 2. Paso Pata 0 (FR): Levantar, avanzar Coxa, apoyar
    if not await mover_suave_ciclo([70, 110, 110, 70], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 110, 70], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 110, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    # 3. Paso Pata 3 (RR): Levantar, avanzar Coxa, apoyar
    if not await mover_suave_ciclo([110, 110, 110, 70], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 110, 110], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 110, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    # 4. Paso Pata 1 (FL): Levantar, avanzar Coxa, apoyar
    if not await mover_suave_ciclo([110, 110, 110, 110], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 110, 110], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 110, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    # 5. Paso Pata 2 (RL): Levantar, avanzar Coxa, apoyar
    if not await mover_suave_ciclo([110, 70, 110, 110], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 70, 110], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 70, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    return True

async def caminar_atras():
    """Ejecuta un ciclo completo de marcha de gateo (Crawl Gait) hacia atrás."""
    # 1. Stance Shift: cuerpo se desplaza hacia atrás (caderas se mueven adelante)
    if not await mover_suave_ciclo([110, 70, 70, 110], [60, 120, 120, 60], pasos=5):
        return False
        
    # 2. Paso Pata 0 (FR): Levantar, retroceder Coxa, apoyar
    if not await mover_suave_ciclo([110, 70, 70, 110], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 70, 110], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 70, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    # 3. Paso Pata 3 (RR): Levantar, retroceder Coxa, apoyar
    if not await mover_suave_ciclo([70, 70, 70, 110], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 70, 70], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 70, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    # 4. Paso Pata 1 (FL): Levantar, retroceder Coxa, apoyar
    if not await mover_suave_ciclo([70, 70, 70, 70], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 70, 70], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 70, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    # 5. Paso Pata 2 (RL): Levantar, retroceder Coxa, apoyar
    if not await mover_suave_ciclo([70, 110, 70, 70], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 110, 70], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 110, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    return True

async def girar_izquierda():
    """Ejecuta un ciclo de rotación sobre su propio eje en sentido antihorario."""
    # 1. Stance Shift rotacional: Coxas van a 70
    if not await mover_suave_ciclo([70, 70, 70, 70], [60, 120, 120, 60], pasos=5):
        return False
        
    # 2. Paso Pata 0 (FR): Levantar, avanzar, apoyar
    if not await mover_suave_ciclo([70, 70, 70, 70], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 70, 70], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 70, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    # 3. Paso Pata 3 (RR): Levantar, avanzar, apoyar
    if not await mover_suave_ciclo([110, 70, 70, 70], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 70, 110], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 70, 70, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    # 4. Paso Pata 1 (FL): Levantar, retroceder, apoyar
    if not await mover_suave_ciclo([110, 70, 70, 110], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 70, 110], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 70, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    # 5. Paso Pata 2 (RL): Levantar, retroceder, apoyar
    if not await mover_suave_ciclo([110, 110, 70, 110], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 110, 110], [60, 120, 90, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([110, 110, 110, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    return True

async def girar_derecha():
    """Ejecuta un ciclo de rotación sobre su propio eje en sentido horario."""
    # 1. Stance Shift rotacional: Coxas van a 110
    if not await mover_suave_ciclo([110, 110, 110, 110], [60, 120, 120, 60], pasos=5):
        return False
        
    # 2. Paso Pata 0 (FR): Levantar, retroceder, apoyar
    if not await mover_suave_ciclo([110, 110, 110, 110], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 110, 110], [90, 120, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 110, 110], [60, 120, 120, 60], pasos=3):
        return False
        
    # 3. Paso Pata 3 (RR): Levantar, retroceder, apoyar
    if not await mover_suave_ciclo([70, 110, 110, 110], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 110, 70], [60, 120, 120, 90], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 110, 110, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    # 4. Paso Pata 1 (FL): Levantar, avanzar, apoyar
    if not await mover_suave_ciclo([70, 110, 110, 70], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 110, 70], [60, 90, 120, 60], pasos=3):
        return False
    if not await mover_suave_ciclo([70, 70, 110, 70], [60, 120, 120, 60], pasos=3):
        return False
        
    # 5. Paso Pata 2 (RL): Levantar, avanzar, apoyar
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
            alarma.alarma_rapida(2)
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
                alarma.beep(150)
                pos_reposo()
                state.comando_actual = "stop"
                await asyncio.sleep_ms(500)
        elif cmd == "backward":
            marchando = await caminar_atras()
            if not marchando:
                print("[ALERTA] Marcha atrás cancelada por obstáculo.")
                alarma.beep(150)
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
            # Comando "stop" o apagado
            pos_reposo()
            await asyncio.sleep_ms(100)

async def main_async():
    """Punto de entrada principal para orquestar la concurrencia."""
    from web_server import iniciar_wifi, start_server_task
    
    # Inicializar interfaz de red Wi-Fi en modo AP
    ip = iniciar_wifi(ssid="USS_SpiderBot_AP", modo_ap=True)
    
    # Crear tareas concurrentes en el event loop
    task_sensors = asyncio.create_task(sensor_updater())
    task_locomotion = asyncio.create_task(locomotion_loop())
    task_server = asyncio.create_task(start_server_task(ip))
    
    print("\n[OK] USS SpiderBot completamente operativo e interactivo por Wi-Fi.")
    
    # Unir tareas para ejecución indeterminada
    await asyncio.gather(task_sensors, task_locomotion, task_server)

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
    pos_reposo()
    alarma.apagar()
