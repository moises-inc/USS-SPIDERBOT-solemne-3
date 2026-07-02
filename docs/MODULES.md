# Diccionario de Componentes y Módulos — USS SpiderBot

Esta sección detalla cada archivo del repositorio, describiendo su propósito, estructura de código (clases/funciones) y dependencias de importación internas.

---

## 📂 Directorio `firmware/` (Código MicroPython y Web)

Módulos encargados de la ejecución en la placa ESP32:

### 1. [main.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/main.py)
*   **Propósito:** Orquestador principal del robot en arquitectura 4-DoF. Levanta los drivers físicos, gestiona las tareas asíncronas de lectura inercial, clasificación IA, locomoción de 4 caderas y evasión reactiva. Maneja el inicio del Wi-Fi en modo AP (físico) o STA (simulador).
*   **Clases Auxiliares:**
    *   `ESP32ServoDirect`: Controlador único de servomotores conectado directamente a pines GPIO de la ESP32 (solo 4 canales de cadera). Sin multiplexor PCA9685. Genera modulación PWM de 16 bits nativa a 50Hz.
        *   Canal 0 (FR Coxa) $\rightarrow$ GPIO 23
        *   Canal 1 (FL Coxa) $\rightarrow$ GPIO 17
        *   Canal 2 (RL Coxa) $\rightarrow$ GPIO 15
        *   Canal 3 (RR Coxa) $\rightarrow$ GPIO 13
*   **Funciones Principales:**
    *   `pos_reposo(secuencial=False)`: Posiciona los 4 servos de cadera a 90°. Soporta encendido secuencial (250ms de separación) para mitigar brownouts por pico de corriente al arranque.
    *   `establecer_angulo_pata(indice, coxa_ang, femur_ang=90)`: Establece el ángulo de una cadera (el fémur se omite por ser fijo a 90°).
    *   `mover_suave_ciclo(coxa_targets, femur_targets=None, pasos=4, delay_ms=12)`: Interpola de forma asíncrona no bloqueante las 4 caderas. Monitorea `state.distancia_actual` en cada paso y aborta si hay obstáculo < 15cm. El parámetro `delay_ms` parametriza la velocidad de oscilación de la marcha.
    *   `caminar_adelante()` / `caminar_atras()` / `girar_izquierda()` / `girar_derecha()`: Ejecutan ciclos completos de la marcha de gateo (Crawl Gait) interpolando solo las 4 caderas con 5 fases (para avance/retroceso) o 2 fases (para giros).
    *   `sensor_updater()`: Corrutina que lee a 20Hz el sonar (con timeout de 5ms y backoff adaptativo a 0.5Hz tras 5 fallos consecutivos) y la IMU. Clasifica el estado inercial mediante `classifier_ia.py` y actualiza `state.pitch_actual`, `state.roll_actual`, `state.distancia_actual` y `state.estado_ia`.
    *   `locomotion_loop()`: Corrutina de decisión de movimiento con 4 prioridades: (1) detección de caída por IA (`FALLEN`), (2) freno de emergencia por obstáculo, (3) selección de marcha según comando, (4) pose de reposo en `stop`. Emite alertas acústicas diferenciadas (`play_critical_alert`, `play_warning_alert`).
    *   `serial_listener()`: Corrutina que escucha comandos por consola serie (Thonny/Wokwi) de forma no bloqueante mediante `select.poll()`. Acepta: `forward`, `backward`, `left`, `right`, `stop`, `reposo`, `stabilize`.
    *   `main_async()`: Punto de entrada asíncrono. Crea las tareas concurrentes `sensor_updater`, `locomotion_loop`, `start_server_task` y `serial_listener` mediante `asyncio.gather()`.
*   **Dependencias Internas:** Importa [state.py](../firmware/state.py), [mpu6050.py](../firmware/mpu6050.py), [sonar_sensor.py](../firmware/sonar_sensor.py), [buzzer_alert.py](../firmware/buzzer_alert.py), [classifier_ia.py](../firmware/classifier_ia.py), [web_server.py](../firmware/web_server.py).

### 2. [web_server.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/web_server.py)
*   **Propósito:** Inicializa las funciones Wi-Fi y levanta un servidor HTTP no bloqueante en socket TCP (puerto 80).
*   **Funciones Principales:**
    *   `iniciar_wifi(ssid, password, modo_ap)`: Configura el modo Access Point (AP, con hasta 4 clientes) o modo Estación (STA) para conectarse a un router. En STA, espera hasta 10s por conexión y revierte automáticamente a AP si falla.
    *   `handle_client(reader, writer)`: Handler asíncrono que parsea las peticiones HTTP y maneja la API de endpoints:
        *   `/` / `/dashboard.html` / `/index.html`: Transmite en bloques de 512 bytes el dashboard.
        *   `/telemetry`: Entrega datos en formato JSON de Pitch, Roll, distancia, comando actual, estabilización y `estado_ia` (clasificación del Decision Tree).
        *   `/api/control`: Controla la dirección (`cmd=forward|backward|left|right|stop|reposo`) y la estabilización (`stabilize=0|1`).
    *   `start_server_task(ip)`: Inicia el socket HTTP no bloqueante. Mantiene la corrutina viva con `await asyncio.sleep(3600)`.
    *   *Mitigación de latencia:* Tras cada respuesta HTTP, ejecuta `gc.collect()` condicional solo si `gc.mem_free() < 15000`, desplazando la GC a segundo plano para minimizar la latencia de respuesta al cliente.
*   **Dependencias Internas:** Importa [state.py](../firmware/state.py) y el módulo estándar `gc`.

### 3. [state.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/state.py)
*   **Propósito:** Módulo de almacenamiento global (Singleton). Centraliza el estado físico medido y las órdenes de control del robot.
*   **Variables Globales:** `comando_actual`, `estabilizacion_activa`, `pitch_actual`, `roll_actual`, `distancia_actual`, `estado_ia`.
*   **Dependencias Internas:** Ninguna.

### 4. [index.html](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/index.html)
*   **Propósito:** Código frontend de la interfaz web del operador. Diseñado para operar 100% offline, con diseño responsive Glassmorphism y visualizaciones SVG en tiempo real para inclinación y sensores.
*   **Dependencias Internas:** Se comunica mediante Fetch asíncrono con los endpoints expuestos en [web_server.py](../firmware/web_server.py).

### 5. [classifier_ia.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/classifier_ia.py)
*   **Propósito:** Clasificador de estados físicos del robot mediante árbol de decisión (Decision Tree) embebido en MicroPython. Procesa las firmas inerciales de la IMU (acelerómetro y giroscopio) para clasificar el estado dinámico del cuadrúpedo en 4 categorías.
*   **Clase:** `IASensorClassifier`
*   **Métodos Principales:**
    *   `classify(ax, ay, az, gx, gy, gz, comando_actual)`: Clasifica el estado actual. Retorna uno de 4 strings:
        *   `"FALLEN"` — Caída: inclinación Pitch o Roll > $\pm45^\circ$, caída libre ($|a| < 0.2g$) o impacto ($|a| > 2g$).
        *   `"PUSHED"` — Perturbación: velocidad angular > $120^\circ$/s mientras el robot está en reposo.
        *   `"SLIPPING"` — Derrape: varianza del acelerómetro horizontal por debajo de 0.08g durante la marcha.
        *   `"NORMAL"` — Estado estable.
    *   `_accel_to_g(raw)`: Convierte lectura bruta del acelerómetro a unidades g (LSB/g = 16384).
    *   `_gyro_to_dps(raw)`: Convierte lectura bruta del giroscopio a grados/segundo (LSB/°/s = 131).
    *   `_compute_pitch_roll(ax_g, ay_g, az_g)`: Calcula Pitch y Roll a partir de aceleraciones normalizadas.
*   **Constantes de Umbral:** `PITCH_FALLEN_THRESHOLD=45.0`, `ROLL_FALLEN_THRESHOLD=45.0`, `FREE_FALL_ACCEL_THRESHOLD=0.2`, `IMPACT_THRESHOLD=2.0`, `GYRO_PUSH_THRESHOLD=120.0`, `SLIP_ACCEL_VAR_THRESHOLD=0.08`.
*   **Dependencias Internas:** Ninguna (usa solo `math` estándar de MicroPython).

### 6. [mpu6050.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/mpu6050.py)
*   **Propósito:** Driver para el acelerómetro MPU6050 por I2C.
*   **Métodos Principales:**
    *   `set_offsets(ox, oy, oz)`: Establece los offsets de calibración a sustraer.
    *   `obtener_inclinacion()`: Retorna Pitch y Roll redondeados a un decimal usando funciones trigonométricas.
*   **Dependencias Internas:** Ninguna.

### 7. [sonar_sensor.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/sonar_sensor.py)
*   **Propósito:** Gestor del sensor de distancia ultrasónico HC-SR04 con timeout reducido (5ms, alcance ~85cm) y adaptación para backoff ante fallos consecutivos.
*   **Métodos Principales:**
    *   `medir_distancia()`: Emite pulso de disparo de 10µs y cronometra la respuesta con timeout de 5ms. Retorna la distancia en cm o `-1.0` en caso de timeout o fuera de rango.
*   **Dependencias Internas:** Ninguna.

### 8. [buzzer_alert.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/buzzer_alert.py)
*   **Propósito:** Controla el buzzer del robot para generar avisos acústicos. Soporta tanto buzzer activo (digital on/off) como pasivo (PWM con frecuencia variable).
*   **Métodos Principales:**
    *   `beep(duration_ms)`, `alarma_rapida(repeticiones=3)`, `alerta_postura()`.
    *   `play_startup()`: Melodía de encendido (3 beeps ascendentes).
    *   `play_critical_alert()`: Alerta de proximidad crítica (< 15cm).
    *   `play_warning_alert()`: Advertencia de obstáculo o confirmación de comando.
    *   `play_shutdown()`: Melodía de apagado (1 largo + 2 cortos).
    *   `play_gait_step()`: Tick acústico de 15ms para paso de caminata.
*   **Dependencias Internas:** Ninguna.

### 9. [calibrate_mpu.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/calibrate_mpu.py)
*   **Propósito:** Utilidad de calibración de offsets para la IMU. Genera `mpu_offsets.txt`.
*   **Dependencias Internas:** Importa [mpu6050.py](mpu6050.py).

### 10. [validate_files.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/validate_files.py)
*   **Propósito:** Validador estático que verifica que todos los archivos Python del directorio compilen correctamente en Python local mediante el análisis AST.

### 11. [diagram.json](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/diagram.json)
*   **Propósito:** Configuración del cableado virtual para simulaciones en Wokwi. Incluye la conexión de los servomotores virtuales y el cableado I2C del MPU6050.

---

## 📂 Directorio `cad/` (Diseños 3D e Impresión FDM)

Archivos OpenSCAD y STL paramétricos para fabricación digital:

### 1. [cuerpo_cuadruepdo.scad](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/cad/cuerpo_cuadruepdo.scad) / [placa_base_inferior.stl](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/cad/placa_base_inferior.stl) / [placa_base_superior.stl](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/cad/placa_base_superior.stl)
*   **Propósito:** Diseño paramétrico del chasis del robot en configuración de doble placa. La inferior incluye 4 brackets perimetrales horizontales con holguras de tolerancia de 0.3mm para servos SG90. La superior sirve de tapa de chasis y anclaje para el microcontrolador ESP32.

### 2. [eslabon_pata_cuadrupedo.scad](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/cad/eslabon_pata_cuadrupedo.scad) / [eslabon_femur.stl](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/cad/eslabon_femur.stl)
*   **Propósito:** Brazo articulado (Fémur) diseñado con un bolsillo empotrado para portar al servomotor de la rodilla de forma horizontal. El extremo proximal se conecta directamente al horn del servo de cadera.

### 3. [tibia_pata.scad](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/cad/tibia_pata.scad) / [tibia_inferior.stl](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/cad/tibia_inferior.stl)
*   **Propósito:** Eslabón final de la pata (Tibia). Curvada para favorecer la tracción, incluye un bolsillo en el extremo superior adaptado para acoplarse con tornillos al horn del servo de rodilla.

### 4. [ensamble_cuadruepodo.scad](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/cad/ensamble_cuadruepodo.scad)
*   **Propósito:** Archivo de ensamblaje general en OpenSCAD. Se utiliza exclusivamente para simular el rango de movimiento angular de las articulaciones, verificar la no-colisión de piezas y generar vistas virtuales y renders.
