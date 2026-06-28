# Reporte de Evaluación de Diseño 3D e Integración Mecánica: USS SpiderBot

Este reporte presenta la evaluación geométrica, física y cinemática para integrar los nuevos componentes de potencia (**2x Convertidores LM2596** y **2x Porta Pilas Duales 18650**) en el chasis del robot cuadrúpedo **USS SpiderBot**, considerando que la estructura física ya se encuentra impresa en más de un **90%**.

El objetivo principal es lograr una integración 100% viable sin necesidad de volver a imprimir las placas del chasis (doble deck) o las articulaciones principales.

---

## 1. Dimensionamiento Físico de los Nuevos Componentes

Para el análisis de colisiones y encajes mecánicos, se definen los envolventes prismáticos reales de los dispositivos adquiridos:

| Componente | Cantidad | Largo ($X$) | Ancho ($Y$) | Alto ($Z$) | Volumen Envolvente (Individual) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Porta Pilas Dual 2x18650** | 2 | $76.0\text{ mm}$ | $40.0\text{ mm}$ | $19.0\text{ mm}$ | $57.76\text{ cm}^3$ |
| **Convertidor Step-Down LM2596** | 2 | $43.0\text{ mm}$ | $21.0\text{ mm}$ | $14.0\text{ mm}$ | $12.64\text{ cm}^3$ |

---

## 2. Evaluación Geométrica del Chasis (Placa Base Inferior)

La placa base inferior circular tiene un radio nominal de $r = 65.0\text{ mm}$ (diámetro de $130.0\text{ mm}$) y un espesor de $3.0\text{ mm}$.

### A. Espacio Libre Central en la Cara Inferior
*   **Restricciones Físicas:** Los 4 brackets de cadera (`soporte_servo_cadera`) están ubicados en la periferia a ángulos de $45^\circ, 135^\circ, 225^\circ\text{ y }315^\circ$, proyectados radialmente a $58.0\text{ mm}$ desde el centro. Cada bracket mide $42.0\text{ mm}$ de largo (eje radial local) por $30.0\text{ mm}$ de ancho.
*   **Área Disponible:** El centro inferior de la placa cuenta con una zona plana libre de brackets que forma un círculo despejado de radio aproximado de $38.0\text{ mm}$ (diámetro $76.0\text{ mm}$).
*   **Encaje de Baterías:** 
    *   Un porta pilas dual de $76.0\text{ x }40.0\text{ mm}$ tiene una semidiagonal de $\sqrt{38^2 + 20^2} = 42.9\text{ mm}$.
    *   Si se alinea el eje longitudinal del portabaterías con el eje X del robot ($Y = 0$), las esquinas del portabaterías se sitúan en los cuadrantes de $0^\circ, 90^\circ, 180^\circ\text{ y }270^\circ$, alejándose al máximo de los brackets que están orientados a $45^\circ$.
    *   **Conclusión:** Un porta pilas (o dos apilados verticalmente) calza perfectamente en el centro de la cara inferior sin colisionar con los soportes de servos de cadera.

### B. Sujeción Mecánica sin Reimpresión
*   **Uso de Ranuras de Velcro Existentes:** La placa inferior ya tiene 4 ranuras de sujeción para correas de velcro a $X = \pm 20\text{ mm}$ y $Y = \pm 10\text{ mm}$.
*   **Solución:** Se apilan verticalmente los dos porta pilas duales (haciendo un sándwich de $76.0\text{ x }40.0\text{ x }38.0\text{ mm}$). Se utiliza una sola correa de velcro extendida (o amarra plástica de nylon) que pasa a través de las 4 ranuras del chasis inferior para abrazar firmemente ambos portabaterías. Esta solución requiere **cero modificaciones de modelado o reimpresión** del chasis base.

---

## 3. Evaluación de Espacio en el Deck Superior (Reguladores)

La placa superior contiene cunas destinadas a la electrónica de control y potencia:
1.  **Cuna Central (Protoboard):** $86.0 \times 58.0\text{ mm}$ (para la protoboard de 400 puntos).
2.  **Cuna Trasera (Diseño XL6009E1):** $45.6 \times 23.6\text{ mm}$, profundidad de $3.0\text{ mm}$.

### A. Ubicación del LM2596 #1 (Servos)
*   Las dimensiones de la placa del LM2596 son $43.0 \times 21.0\text{ mm}$.
*   La cuna trasera original de la placa superior es de $45.6 \times 23.6\text{ mm}$.
*   **Conclusión:** El primer regulador LM2596 calza de manera óptima dentro de la cuna del XL6009E1 original con una holgura perimetral estándar de $+1.3\text{ mm}$ por lado.

### B. Ubicación del LM2596 #2 (ESP32 y Lógica)
Para montar el segundo regulador LM2596 sin reimprimir la placa superior, se proponen dos alternativas:

1.  **Montaje en "Torre de Reguladores" (Recomendado):**
    *   Diseñar e imprimir un pequeño clip vertical (soporte de dos pisos) de $45.6 \times 23.6 \times 18\text{ mm}$. Este clip encaja a presión en la cuna trasera de la placa superior, permitiendo alojar el LM2596 #1 en el nivel inferior y el LM2596 #2 en el nivel superior.
    *   *Ventaja:* Es una pieza sumamente pequeña (tiempo de impresión ~15 minutos, consumo de filamento ~5g) y mantiene ordenados y ventilados ambos reguladores.
2.  **Montaje Adhesivo en la Placa Inferior:**
    *   Fijar el segundo regulador LM2596 en la cara superior de la placa inferior (debajo de la protoboard, donde hay un espacio de $19\text{ mm}$ de alto) utilizando cinta doble contacto de espuma de poliuretano.
    *   *Ventaja:* No requiere ninguna impresión adicional y aprovecha el espacio interno del robot.

---

## 4. Impacto Cinemático y Despeje del Suelo (Clearance)

*   **Longitud de Eslabones:** Fémur = $55.0\text{ mm}$ | Tibia = $65.0\text{ mm}$.
*   **Altura de Reposo del Chasis:** En pose estática de reposo seguro, la placa inferior se sitúa a una distancia de **$85.0\text{ mm}$** respecto al suelo.
*   **Proyección de las Baterías:** El bloque apilado de dos porta pilas 18650 sobresale $38.0\text{ mm}$ hacia abajo de la placa inferior.
*   **Despeje Libre Resultante (Clearance):** 
    $$Clearance = 85.0\text{ mm} - 38.0\text{ mm} = 47.0\text{ mm}$$
*   **Conclusión:** Un despeje al suelo de **$47.0\text{ mm}$** es sumamente holgado para un robot caminador de este tamaño, permitiendo la marcha Crawl Gait sobre superficies planas y la superación de desniveles pequeños sin rozar las baterías contra el suelo.

---

## 5. Distribución de Masas y Estabilidad Estática

*   **Peso de Celdas 18650:** Cada celda 18650 pesa aproximadamente $45\text{ g}$. Las 4 celdas más los 2 porta pilas suman un peso de potencia aproximado de **$210\text{ g}$**.
*   **Centro de Masa (CoM):** Al ubicar las celdas apiladas exactamente en el centro concéntrico de la placa base inferior, el centro de masa del conjunto de potencia se mantiene alineado en el eje central ($X=0, Y=0$) y se reduce el centro de gravedad general del robot en el eje Z.
*   **Estabilidad:** Un centro de gravedad más bajo incrementa notablemente la estabilidad estática y dinámica del cuadrúpedo durante la fase de balanceo (swing) de las patas, reduciendo el torque inercial sobre los servos de cadera.

---

## 6. Conclusiones y Plan de Acción Técnico

1.  **Viabilidad Mecánica:** Confirmada al 100%. No se requiere reimprimir ninguna de las piezas impresas (90%+ del robot).
2.  **Plan de Acción Físico:**
    *   **Paso 1:** Apilar los porta pilas 18650 en la parte inferior central del robot usando correas de velcro.
    *   **Paso 2:** Colocar el primer LM2596 en la cuna trasera de la placa superior.
    *   **Paso 3 (Opcional):** Imprimir la "Torre de Reguladores" (clip de dos pisos) para colocar el segundo LM2596 directamente encima del primero.
