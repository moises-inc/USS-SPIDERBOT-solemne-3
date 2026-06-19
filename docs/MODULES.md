# Diccionario de Componentes y Módulos — USS SpiderBot

Esta sección detalla cada archivo del repositorio, describiendo su propósito, estructura de código (clases/funciones) y dependencias de importación internas.

---

## 📂 Directorio `firmware/` (Código MicroPython y Web)

Módulos encargados de la ejecución en la placa ESP32:

### 1. [main.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/main.py)
*   **Propósito:** Orquestador principal del robot. Levanta los drivers físicos, gestiona las tareas asíncronas de lectura inercial, locomoción y evasión reactiva, y maneja el inicio del Wi-Fi en modo AP (físico) o STA (simulador).
*   **Clases Auxiliares:**
    *   `ESP32ServoDirect`: Emulador de la API del PCA9685. Si la ESP32 no encuentra el PCA9685 en I2C, se instancia esta clase y se configuran 8 señales PWM directas hacia los GPIOs del simulador:
        *   Canal 0 (FR Coxa) $\rightarrow$ GPIO 13
        *   Canal 1 (FR Fémur) $\rightarrow$ GPIO 12
        *   Canal 2 (FL Coxa) $\rightarrow$ GPIO 15
        *   Canal 3 (FL Fémur) $\rightarrow$ GPIO 2
        *   Canal 4 (RL Coxa) $\rightarrow$ GPIO 4
        *   Canal 5 (RL Fémur) $\rightarrow$ GPIO 5
        *   Canal 6 (RR Coxa) $\rightarrow$ GPIO 23
        *   Canal 7 (RR Fémur) $\rightarrow$ GPIO 25
*   **Funciones Principales:**
    *   `pos_reposo()`: Posiciona todos los canales de servos a sus ángulos base estándar.
    *   `establecer_angulo_pata(indice, coxa, femur)`: Calcula y aplica la compensación inercial proporcional sobre los fémures en apoyo.
    *   `mover_suave_ciclo(coxa_targets, femur_targets)`: Interpola de forma asíncrona no bloqueante los ángulos de reposo a los objetivos usando `await asyncio.sleep_ms(delay_ms)`.
    *   `caminar_adelante()` / `caminar_atras()` / `girar_izquierda()` / `girar_derecha()`: Ejecutan ciclos completos de la marcha de gateo (Crawl Gait).
    *   `sensor_updater()`: Corrutina que lee a 20Hz el sonar y la IMU y actualiza el estado.
    *   `locomotion_loop()`: Corrutina de toma de decisiones de movimiento y freno de emergencia.
    *   `main_async()`: Punto de entrada asíncrono. Gestiona la conexión Wi-Fi adaptativa: modo AP (`USS_SpiderBot_AP`) en físico, y modo Estación conectado a `Wokwi-GUEST` en simulación.
*   **Dependencias Internas:** Importa [state.py](../firmware/state.py), [pca9685.py](../firmware/pca9685.py), [mpu6050.py](../firmware/mpu6050.py), [sonar_sensor.py](../firmware/sonar_sensor.py), [buzzer_alert.py](../firmware/buzzer_alert.py), [web_server.py](../firmware/web_server.py).

### 2. [web_server.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/web_server.py)
*   **Propósito:** Inicializa las funciones Wi-Fi y levanta un servidor HTTP no bloqueante en socket TCP (puerto 80).
*   **Funciones Principales:**
    *   `iniciar_wifi(ssid, password, modo_ap)`: Configura el modo Access Point (AP) o modo Estación (STA) para conectarse a un router, devolviendo la IP asignada.
    *   `handle_client(reader, writer)`: Handler asíncrono que parsea las peticiones HTTP y maneja la API de endpoints:
        *   `/` / `/index.html`: Transmite en bloques de 512 bytes el dashboard.
        *   `/telemetry`: Entrega datos en formato JSON de Pitch, Roll, comando actual y distancia.
        *   `/api/control`: Controla la dirección (`cmd=...`) y la estabilización (`stabilize=...`).
    *   `start_server_task(ip)`: Inicia el socket HTTP no bloqueante.
*   **Dependencias Internas:** Importa [state.py](../firmware/state.py).

### 3. [state.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/state.py)
*   **Propósito:** Módulo de almacenamiento global (Singleton). Centraliza el estado físico medido y las órdenes de control del robot.
*   **Variables Globales:** `comando_actual`, `estabilizacion_activa`, `pitch_actual`, `roll_actual`, `distancia_actual`.
*   **Dependencias Internas:** Ninguna.

### 4. [index.html](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/index.html)
*   **Propósito:** Código frontend de la interfaz web del operador. Diseñado para operar 100% offline, con diseño responsive Glassmorphism y visualizaciones SVG en tiempo real para inclinación y sensores.
*   **Dependencias Internas:** Se comunica mediante Fetch asíncrono con los endpoints expuestos en [web_server.py](../firmware/web_server.py).

### 5. [pca9685.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/pca9685.py)
*   **Propósito:** Driver de bajo nivel para el expansor PWM PCA9685 mediante I2C.
*   **Métodos Principales:**
    *   `set_pwm_freq(freq)`: Ajusta la frecuencia PWM (50Hz para servos SG90).
    *   `set_servo_angle(channel, angle)`: Convierte ángulos de 0° a 180° a ciclos de trabajo PWM de 12 bits.
*   **Dependencias Internas:** Ninguna.

### 6. [mpu6050.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/mpu6050.py)
*   **Propósito:** Driver para el acelerómetro MPU6050 por I2C.
*   **Métodos Principales:**
    *   `set_offsets(ox, oy, oz)`: Establece los offsets de calibración a sustraer.
    *   `obtener_inclinacion()`: Retorna Pitch y Roll redondeados a un decimal usando funciones trigonométricas.
*   **Dependencias Internas:** Ninguna.

### 7. [sonar_sensor.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/sonar_sensor.py)
*   **Propósito:** Gestor del sensor de distancia ultrasónico HC-SR04.
*   **Métodos Principales:**
    *   `medir_distancia()`: Emite el pulso y cronometra la respuesta en microsegundos, calculando la distancia lineal.
*   **Dependencias Internas:** Ninguna.

### 8. [buzzer_alert.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/buzzer_alert.py)
*   **Propósito:** Controla el buzzer del robot para generar avisos acústicos.
*   **Métodos Principales:**
    *   `beep()`, `alarma_rapida()`, `alerta_postura()`.
*   **Dependencias Internas:** Ninguna.

### 9. [calibrate_mpu.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/calibrate_mpu.py)
*   **Propósito:** Utilidad de calibración de offsets para la IMU. Genera `mpu_offsets.txt`.
*   **Dependencias Internas:** Importa [mpu6050.py](mpu6050.py).

### 10. [validate_files.py](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/validate_files.py)
*   **Propósito:** Validador estático que verifica que todos los archivos Python del directorio compilen correctamente en Python local mediante el análisis AST.

### 11. [diagram.json](file:///mnt/9b846436-0407-4e80-b8af-5417ffbdee8e/Github/USS%20SPIDERBOT%20(solemne%203)/firmware/diagram.json)
*   **Propósito:** Configuración del cableado virtual para simulaciones en Wokwi. Incluye la conexión de los 8 servomotores virtuales.

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
