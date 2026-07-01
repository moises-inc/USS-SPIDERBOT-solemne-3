# Manual Definitivo de Armado, Electrónica, Locomoción y Firmware — USS SpiderBot (4-DoF)
**Solemne 3 — Taller de Programación I (Universidad San Sebastián, 2026)**

Este documento constituye la guía oficial y definitiva para el ensamblaje mecánico, la integración de la electrónica regulada, el conexionado físico (pinout), el centrado de servomotores y la calibración inercial del robot cuadrúpedo **USS SpiderBot** simplificado a una configuración de **4 servomotores (4-DoF)**. Además, se detalla la arquitectura de software (MicroPython) y el funcionamiento de la Inteligencia Artificial Sensorial embebida.

---

## 💻 Índice
1. [Especificaciones y Arquitectura General](#1-especificaciones-y-arquitectura-general)
2. [Lista de Materiales y Herramientas (BOM)](#2-lista-de-materiales-y-herramientas-bom)
3. [Integración Eléctrica y Regulación de Potencia](#3-integración-eléctrica-y-regulación-de-potencia)
4. [Pinout y Diagrama de Cableado Detallado](#4-pinout-y-diagrama-de-cableado-detallado)
5. [Guía de Ensamblaje Mecánico 3D Paso a Paso](#5-guía-de-ensamblaje-mecánico-3d-paso-a-paso)
6. [Estructura del Firmware y Mapa de Archivos](#6-estructura-del-firmware-y-mapa-de-archivos)
7. [Algoritmo de Locomoción y Marcha de Gateo](#7-algoritmo-de-locomoción-y-marcha-de-gateo)
8. [Inteligencia Artificial Sensorial (IA Local)](#8-inteligencia-artificial-sensorial-ia-local)
9. [Protocolo de Puesta en Marcha y Calibración](#9-protocolo-de-puesta-en-marcha-y-calibración)
10. [Guía de Diagnóstico y Resolución de Problemas (FAQ)](#10-guía-de-diagnóstico-y-resolución-de-problemas-faq)

---

## 1. Especificaciones y Arquitectura General
El **USS SpiderBot** es un robot móvil terrestre cuadrúpedo articulado con **4 grados de libertad (4-DoF)**. Su diseño físico simplificado cuenta con **un único servomotor por pata**, posicionado en la articulación de la cadera o *Coxa*. La articulación de la rodilla (*Fémur*) se mantiene en un ángulo rígido fijo de $90^\circ$ (perpendicular), lo que reduce considerablemente el peso, el consumo eléctrico y la complejidad del cableado, permitiendo una locomoción robusta basada en deslizamiento y fricción controlada.

### Características Principales:
*   **Microcontrolador Principal:** ESP32 DevKit V1 ejecutando MicroPython asíncrono.
*   **Locomoción Dinámica:** Marcha de gateo oscilante de 4 fases actuando únicamente sobre las caderas.
*   **Seguridad Reactiva:** Sensor de proximidad ultrasónico HC-SR04 y buzzer activo de alarma.
*   **IA de Borde (Edge AI):** Clasificador embebido local (MPU6050) para detectar caídas, derrapes y perturbaciones externas.
*   **Interfaz de Operación:** Servidor web asíncrono y control inalámbrico mediante dashboard Glassmorphism por Wi-Fi.

---

## 2. Lista de Materiales y Herramientas (BOM)

### A. Componentes Electrónicos
*   **1x ESP32 DevKit V1 (38 pines):** Microcontrolador principal de 3.3V.
*   **4x Servomotores SG90 (engranajes de nylon) o MG90S (engranajes metálicos):** Actuadores de cadera.
*   **1x Módulo GY-521 (IMU MPU6050):** Acelerómetro y giroscopio de 6 ejes con comunicación I2C.
*   **1x Sensor Ultrasónico HC-SR04:** Transductor de distancia de 5V.
*   **1x Buzzer Activo (5V):** Generador de alertas acústicas.
*   **2x Convertidores Step-Down LM2596:** Reguladores reductores de voltaje ajustables (LM2596 #1 para servos, LM2596 #2 para lógica).
*   **2x Porta Pilas Duales 2x18650:** Dos packs independientes de 2 celdas en serie.
*   **4x Celdas de Litio-Ion 18650:** Baterías recargables.

### B. Materiales de Chasis e Impresión 3D
*   **1x Placa Base Inferior (`cuerpo_cuadruepdo.scad`):** Soporta servos de cadera y portabaterías.
*   **1x Placa Base Superior/Tapa (`cuerpo_cuadruepdo.scad`):** Protege la electrónica y soporta la ESP32.
*   **4x Extremidades Rígidas:** Conjunto de fémur y tibia fijos mecánicamente a $90^\circ$ (o patas rígidas de una sola pieza).
*   **4x Pilares Separadores:** Pilares de 25mm M3 para distanciar el chasis.

---

## 3. Integración Eléctrica y Regulación de Potencia

Al reducir los servomotores a 4 unidades, el consumo máximo del sistema disminuye a aproximadamente **1.5A** en picos mecánicos. Esto permite simplificar la electrónica utilizando **un único convertidor step-down LM2596 regulado a 5.0V** y **un único portapilas dual 18650** para alimentar en paralelo tanto la lógica de control como los actuadores:

```text
  [Pack Batería (7.4V)] ──> [LM2596 (Regulado a 5.0V)] ──> Riel VCC (5.0V Común)
                                                          ├──> Pin Vin ESP32 y Sensores
                                                          └──> Riel VCC Servomotores (Servos 0-3)
```

### 🛠️ Protocolo Obligatorio de Regulación:
1.  **Ajuste Inicial:** Use un multímetro para ajustar la salida del **LM2596 a exactamente 5.0V** antes de conectar la ESP32 o los servos.
2.  **Masa Común (GND):** Conecte el pin GND de la ESP32, la tierra de salida del LM2596 y la tierra de los servos en el mismo riel común.
3.  **Prevención de Retorno (USB + Baterías):** **Nunca** encienda la alimentación de la batería lógica (que entrega voltaje a `Vin`) mientras la ESP32 esté conectada al puerto USB del PC. Para cargar código, apague las baterías. Para pruebas, desconecte el USB.

---

## 4. Pinout y Diagrama de Cableado Detallado

El conexionado físico de la ESP32 DevKit V1 se reduce a **4 canales PWM directos** para los servomotores:

| Pin ESP32 | Componente | Tipo de Señal | Función / Descripción |
| :---: | :--- | :---: | :--- |
| **Vin** | Salida LM2596 (5.0V) | Alimentación IN | Entrada de voltaje regulado para la lógica de la ESP32 |
| **GND** | Nodo de Tierra Común | Referencia | Tierra unificada del sistema |
| **GPIO 21** | MPU6050 (IMU) | SDA (I2C) | Bus de datos serie de la unidad inercial |
| **GPIO 22** | MPU6050 (IMU) | SCL (I2C) | Bus de reloj serie de la unidad inercial |
| **GPIO 18** | HC-SR04 (Sonar) | TRIGGER | Pulso digital de disparo del ultrasonido |
| **GPIO 19** | HC-SR04 (Sonar) | ECHO | Entrada de lectura del tiempo de eco |
| **GPIO 14** | Buzzer Activo | Salida Digital | Activación y modulación de tonos acústicos |
| **GPIO 23** | Servo FR - Coxa (Canal 0) | Salida PWM | Articulación cadera delantera derecha |
| **GPIO 17** | Servo FL - Coxa (Canal 1) | Salida PWM | Articulación cadera delantera izquierda |
| **GPIO 15** | Servo RL - Coxa (Canal 2) | Salida PWM | Articulación cadera trasera izquierda |
| **GPIO 13** | Servo RR - Coxa (Canal 3) | Salida PWM | Articulación cadera trasera derecha |

---

## 5. Guía de Ensamblaje Mecánico 3D Paso a Paso

El ensamblaje para 4-DoF simplifica el proceso al omitir la electrónica articulada en las rodillas:

1.  **Montaje de Servos en Chasis:** Inserte a presión los 4 servomotores en sus soportes perimetrales en la **Placa Base Inferior**. El eje estriado debe mirar hacia el extremo exterior. Asegúrelos con tornillos autorroscantes M2.
2.  **Calibración del Cero Eléctrico (Paso Crítico):** Conecte la ESP32 por USB y ejecute `prueba_servos.py` seleccionando la **Opción 3** para forzar a todos los servos a la posición neutra de **$90^\circ$**.
3.  **Montaje de Patas Rígidas:** Con los servos energizados y fijos en $90^\circ$, acople la estructura de pata (fémur y tibia fijos a $90^\circ$ vertical) de modo que queden alineadas a escuadra (apuntando verticalmente hacia abajo en perpendicular con el chasis). Fije los horns centrales con tornillos.
4.  **Montaje Superior:** Instale los pilares distanciadores M3 de 25mm, coloque las baterías en los portabaterías inferiores y fije la **Placa Base Superior** asegurando la protoboard, el ESP32, el HC-SR04 y la IMU en el puente superior.

---

## 6. Estructura del Firmware y Mapa de Archivos

La arquitectura en MicroPython asíncrono se optimiza para controlar los 4 actuadores:
*   `main.py`: Administra el bucle asíncrono, la lectura de sensores y el control de las 4 caderas.
*   `prueba_servos.py`: Diagnóstico de barrido rápido y modo armado para los 4 canales directos.
*   `prueba_servo_individual.py`: Terminal interactiva para depuración manual servo a servo.
*   `prueba_mpu6050.py`: Validador de bus I2C y telemetría inercial cruda del GY-521.
*   `classifier_ia.py`: Motor de clasificación inercial de Edge AI (NORMAL, FALLEN, PUSHED, SLIPPING).
*   `web_server.py`: Servidor HTTP no bloqueante que enruta las peticiones de control API y telemetría.
*   `dashboard.html`: Panel web premium auto-adaptable a la telemetría en tiempo real del robot.

---

## 7. Algoritmo de Locomoción y Marcha de Gateo

Con una configuración de 4 caderas oscilantes, la marcha se simplifica a un ciclo de gateo en **5 fases**:

```text
[Inicio: Pose Reposo 90°] ➔ [1. Adelantar FR] ➔ [2. Adelantar RR] 
                            ➔ [3. Adelantar FL] ➔ [4. Adelantar RL] ➔ [5. Empuje Cuerpo]
```

### Rangos de Oscilación por Espejo:
*   **Coxa Adelantado (Avanzar):** Derecha (FR/RR) = $110^\circ$ | Izquierda (FL/RL) = $75^\circ$.
*   **Coxa Atrasado (Empujar):** Derecha (FR/RR) = $70^\circ$ | Izquierda (FL/RL) = $105^\circ$.
*   **Empuje General (Fase 5):** Con todas las patas apoyadas, las caderas oscilan coordinadamente hacia atrás para desplazar físicamente el cuerpo del robot hacia adelante.

---

## 8. Inteligencia Artificial Sensorial (IA Local)

El clasificador local (`classifier_ia.py`) funciona independientemente del número de actuadores:
1.  **Detección de Caída (`FALLEN`):** Si la inclinación del Pitch/Roll supera los $\pm 45^\circ$, ante caída libre ($|a| < 0.2g$) o choque ($|a| > 2g$), el lazo de locomoción detiene la marcha asíncrona, lleva las 4 caderas a $90^\circ$ y activa la alarma intermitente del buzzer.
2.  **Estabilización Activa:** Dado que los servos Coxa solo actúan en el plano de avance/retroceso y no permiten modificar la altura vertical del pie, la compensación inercial activa diferencial se encuentra desactivada en software para esta variante de 4-DoF.

---

## 9. Protocolo de Puesta en Marcha y Calibración
1.  **Alineación Mecánica:** Coloque las patas de forma que en pose neutra ($90^\circ$ en `prueba_servos.py`) el robot se sostenga erguido.
2.  **Calibración Inercial:** Coloque el robot estable en superficie nivelada y ejecute `calibrate_mpu.py` en Thonny para generar el archivo `mpu_offsets.txt`.
3.  **Depuración Inalámbrica:** Desconecte el USB, encienda las baterías y controle el robot desde la red Wi-Fi `USS_SpiderBot_AP` ingresando a `http://192.168.4.1/`.

---

## 10. Guía de Diagnóstico y Resolución de Problemas (FAQ)

### P1: El robot no avanza y solo resbala en el suelo
*   **Causa:** Poca adherencia en las puntas de las patas, o el ángulo de empuje es muy amplio provocando pérdida de tracción.
*   **Solución:** Agregue gomas antideslizantes (o silicona caliente) en la base de contacto de las tibias y reduzca la velocidad de oscilación en `main.py` suavizando las transiciones.

### P2: El buzzer pita continuamente y el robot se bloquea al encender con baterías
*   **Causa:** La IMU GY-521 está mal cableada (no se detecta I2C en `0x68`) o el sensor clasifica falsos positivos de caída.
*   **Solución:** Ejecute `prueba_mpu6050.py` para validar la telemetría inercial y revise los cables de SDA (21) y SCL (22).
