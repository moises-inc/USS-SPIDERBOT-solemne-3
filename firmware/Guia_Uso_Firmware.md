# Guía de Uso del Firmware — USS SpiderBot

Esta guía detalla la arquitectura de software, la asignación física de pines en la **ESP32** y el flujo de uso de los códigos y scripts de prueba desarrollados para el robot cuadrúpedo **USS SpiderBot**.

---

## 🔌 Asignación Física de Pines (ESP32 DevKit V1)

Al haber migrado a **control directo por GPIO** (sin usar el driver PCA9685) y alimentación mediante un **pack de baterías Li-ion 2S en serie (7.4V)** regulado por un **UBEC de 5V/3A**, las conexiones físicas se realizan directamente de la siguiente manera:

### 1. Servomotores (8 Canales Directos a GPIO)
Los cables de señal de los 8 servomotores SG90 se conectan a los siguientes pines de la ESP32 (los terminales de alimentación **VCC y GND deben ir al riel de salida del UBEC**, compartiendo la tierra común GND con la ESP32):

| Canal | Componente | Pin GPIO | Descripción |
|:---:|:---|:---:|:---|
| **0** | Pata FR - Coxa (Cadera) | **GPIO 13** | Rotación horizontal delantera derecha |
| **1** | Pata FR - Fémur (Rodilla) | **GPIO 12** | Rotación vertical delantera derecha |
| **2** | Pata FL - Coxa (Cadera) | **GPIO 15** | Rotación horizontal delantera izquierda |
| **3** | Pata FL - Fémur (Rodilla) | **GPIO 2** | Rotación vertical delantera izquierda |
| **4** | Pata RL - Coxa (Cadera) | **GPIO 4** | Rotación horizontal trasera izquierda |
| **5** | Pata RL - Fémur (Rodilla) | **GPIO 5** | Rotación vertical trasera izquierda |
| **6** | Pata RR - Coxa (Cadera) | **GPIO 23** | Rotación horizontal trasera derecha |
| **7** | Pata RR - Fémur (Rodilla) | **GPIO 25** | Rotación vertical trasera derecha |

### 2. Sensores e Interfaces de Alerta
| Dispositivo | Señal / Pin | Pin GPIO | Notas |
|:---|:---:|:---:|:---|
| **Sensor Ultrasónico HC-SR04** | Trigger | **GPIO 18** | Envío del pulso de disparo ultrasónico |
| **Sensor Ultrasónico HC-SR04** | Echo | **GPIO 19** | Retorno del pulso (lectura de duración) |
| **IMU MPU6050 (Acelerómetro/Giro)** | SDA | **GPIO 21** | Bus I2C de hardware de la ESP32 |
| **IMU MPU6050 (Acelerómetro/Giro)** | SCL | **GPIO 22** | Bus I2C de hardware de la ESP32 |
| **Buzzer Activo/Pasivo** | Positivo | **GPIO 14** | Señal de alertas y pitidos de proximidad |

---

## 📂 Descripción del Directorio de Firmware

El directorio de firmware consta de los siguientes archivos:

1. **`main.py`**: Código de control principal y asíncrono. Inicia el servidor web, el bucle de sensores (IMU, Sonar), el control inercial y los algoritmos de marcha (*Crawl Gait*).
2. **`prueba_servos.py`**: Script interactivo para testear y barrer los 8 servos secuencialmente. Incluye la opción para posicionar todos los servos a **90 grados** (crucial para el armado y calibración mecánica de las patas).
3. **`prueba_servo_individual.py`**: Consola interactiva para mover servomotores uno a uno ingresando comandos directos como `FR_C 45` o `RR_F 120`.
4. **`prueba_sonar_buzzer.py`**: Script autoportante (no requiere subir otras librerías) para probar la telemetría del sonar y las alertas de sonido del buzzer.
5. **`calibrate_mpu.py`**: Script para calibrar y grabar los offsets del sensor MPU6050 colocándolo en una superficie completamente nivelada.
6. **`web_server.py`**: Servidor Web asíncrono HTTP/WebSockets que sirve el panel de control.
7. **`index.html`**: Panel web de control interactivo con joysticks y visualización de telemetría en tiempo real.
8. **`state.py`**: Estructura de datos global para compartir el estado de variables entre las diferentes tareas asíncronas de MicroPython.
9. **`sonar_sensor.py`**: Librería/Driver del sensor ultrasónico HC-SR04.
10. **`mpu6050.py`**: Librería/Driver del giroscopio/acelerómetro MPU6050.
11. **`buzzer_alert.py`**: Librería/Driver de control del buzzer.
12. **`validate_files.py`**: Utilidad que valida que no existan errores de sintaxis en los scripts Python.

---

## 🚀 Guía de Puesta en Marcha en Thonny IDE

Sigue estos pasos en orden para poner a punto y calibrar el USS SpiderBot:

### Paso 1: Verificación de Conexiones
1. Conecta la ESP32 a la computadora vía USB.
2. Abre Thonny IDE y configura el intérprete en **MicroPython (ESP32)**.
3. Asegúrate de tener todos los archivos listados cargados en el sistema de archivos de la ESP32.

### Paso 2: Calibración y Armado Mecánico (Centrado de Servos)
Antes de colocar físicamente los brackets de los fémures y tibias en los engranajes metálicos de los servos, debes fijar los motores exactamente a 90 grados:
1. Abre y ejecuta `prueba_servos.py` en Thonny.
2. Selecciona la **Opción 3** (*Modo Armado/Calibración*). Esto posicionará los 8 servomotores en **90°**.
3. Ahora monta las patas (cadera y rodilla) a presión de forma que queden alineadas simétricamente en su pose neutra horizontal y aprieta los tornillos M2 de los horns.

### Paso 3: Calibración del Sensor IMU (MPU6050)
1. Coloca el robot sobre una mesa estable y completamente plana.
2. Abre y ejecuta `calibrate_mpu.py`.
3. Sigue las instrucciones en consola para guardar los valores de calibración en la memoria del sensor.

### Paso 4: Prueba de Sensores y Alertas
1. Abre y ejecuta `prueba_sonar_buzzer.py`.
2. Pasa tu mano por delante del sensor de distancia. Deberías ver la lectura variar en Thonny.
3. El buzzer pitará una vez a los **30 cm** y emitirá una alarma rápida si la distancia es menor a **15 cm**.

### Paso 5: Prueba de Servos Individuales
1. Abre y ejecuta `prueba_servo_individual.py`.
2. En la consola de Thonny ingresa comandos como:
   - `mover 90` o solo `90` (mueve todos a 90°).
   - `FR_C 45` (mueve la cadera delantera derecha a 45°).
   - `RR_F 135` (mueve la rodilla trasera derecha a 135°).
   - `b` (inicia barrido automático de canales).
   - `salir` (finaliza el programa).

### Paso 6: Ejecución del Control Principal
1. Configura el archivo `main.py`. Si deseas que se ejecute de forma autónoma al encender el robot, asegúrate de que esté grabado en la ESP32 como `main.py`.
2. Al arrancar `main.py`, la ESP32 creará un punto de acceso Wi-Fi (o se conectará a la red configurada en `main.py`).
3. Conéctate a la red inalámbrica de la ESP32 y accede en tu navegador a la dirección IP indicada en la consola de Thonny (usualmente `http://192.168.4.1`) para abrir el panel de control dinámico.

---

## 🛠️ Solución de Problemas Comunes
* **`ImportError: no module named 'sonar_sensor'`**: Asegúrate de haber subido todas las librerías auxiliares (`sonar_sensor.py`, `mpu6050.py`, `buzzer_alert.py`, `state.py`, `web_server.py`) a la ESP32 y no solo el script de prueba.
* **Los servos vibran o se reinicia la ESP32**: Los servos están demandando más corriente de la que el puerto USB o un regulador pequeño puede entregar. Conecta la alimentación externa mediante el pack de baterías 2S y el UBEC reductor, recordando unir la tierra (GND) del UBEC con la de la ESP32.
