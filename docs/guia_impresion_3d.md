# Guía de Impresión 3D y Configuración de Creality Print: USS SpiderBot

Esta guía detalla la configuración y laminación (slicing) de las piezas definitivas del **USS SpiderBot** utilizando el software **Creality Print**. El objetivo es optimizar los tiempos de impresión, garantizar la máxima resistencia estructural (especialmente en los soportes de servos y orificios roscados) y asegurar que todas las piezas quepan perfectamente en el volumen de impresión estándar de $220 \times 220 \times 250\text{ mm}$ (Ender-3 series, K1, Ender-3 V3).

---

## 1. Distribución de Platos de Impresión (Build Plate Layout)

Debido al diámetro del chasis central ($130\text{ mm}$ de placa más los soportes perimetrales de cadera), no es posible imprimir la placa inferior y superior juntas en una cama de $220 \times 220\text{ mm}$. Para optimizar el espacio y la calidad, el proyecto se divide en **3 Platos de Impresión (Build Plates)** secuenciales:

### 📥 Plato 1: Estructura Base (Placa Inferior)
* **Piezas:** `placa_base_inferior.stl` (1 unidad).
* **Orientación en Cama:** Cara plana inferior (Z-) asentada directamente sobre la cama de impresión. Los soportes de servo de cadera crecerán hacia arriba en el eje Z.
* **Soportes:** **Desactivados (No requiere)**. Los brackets están apoyados en el chasis o crecen sobre la placa en ángulos rectos y planos, eliminando la necesidad de material de soporte.
* **Tiempo Estimado:** ~2.5 a 3.5 horas (según velocidad).

### 📥 Plato 2: Tapa Protectora (Placa Superior)
* **Piezas:** `placa_base_superior.stl` (1 unidad).
* **Orientación en Cama:** Cara plana inferior (Z-) asentada directamente sobre la cama. Las cunas de protoboard, regulador XL6009E1 y el soporte vertical del sonar crecerán hacia arriba.
* **Soportes:** **Desactivados (No requiere)**. Las cunas tienen paredes verticales autoportantes. Los dos orificios horizontales de $16.5\text{ mm}$ del sensor ultrasónico HC-SR04 se imprimen mediante puenteo (bridging) nativo sin colapsar.
* **Tiempo Estimado:** ~2 a 3 horas.

### 📥 Plato 3: Mecanismo de Patas (Eslabones)
* **Piezas:**
  * `eslabon_femur.stl` (4 unidades).
  * `tibia_inferior.stl` (4 unidades).
* **Orientación en Cama:**
  * **Fémures:** Colocados con la cara plana inferior (Z-) sobre la cama. El bolsillo del servo de rodilla queda mirando hacia arriba (Z+). La cavidad del acople de cadera (Z-) queda contra la cama y se puentea limpiamente por la impresora (ancho de $5.2\text{ mm}$, autoportante).
  * **Tibias:** Colocadas planas sobre su cara Z-. El extremo del pie de bola sobresaldrá levemente en el laminador. Deja que el slicer realice un corte plano en la base de la bola contra la cama (aproximadamente $1\text{ mm}$ de altura). Esto mejora la adherencia a la cama y proporciona un punto de apoyo plano y estable en el suelo.
* **Disposición (Layout):** Distribuye los 8 eslabones en cuadrícula de $2 \times 4$ espaciados $15\text{ mm}$ entre sí en el centro de la cama.
* **Soportes:** **Desactivados (No requiere)**.
* **Tiempo Estimado:** ~4 a 5 horas.

---

## 2. Parámetros de Laminación (Slicing Settings)

Para asegurar la rigidez necesaria del cuadrúpedo y evitar el desgranado de capas o el barrido de roscas por los tornillos de los servos, aplica los siguientes parámetros en el perfil de **Creality Print**:

### A. Estructura y Paredes (Shells)
* **Altura de Capa (Layer Height):** `0.20 mm` (Resolución estándar, óptima velocidad/resistencia).
* **Ancho de Línea (Line Width):** `0.40 mm` (o `0.42 mm` para mejorar adhesión).
* **Recuento de Paredes (Wall Line Count):** `4 paredes` (Mínimo recomendado: 3). Esto garantiza que los agujeros M2 y M3 se rosquen en plástico sólido y no en relleno hueco.
* **Capas Superiores/Inferiores (Top/Bottom Layers):** `4 capas` (Espesor mínimo: $0.8\text{ mm}$).

### B. Relleno (Infill)
* **Densidad de Relleno (Infill Density):** `25%` a `30%` (Crítico para fémur y placa inferior).
* **Patrón de Relleno (Infill Pattern):** `Giroide (Gyroid)` o `Cúbico (Cubic)`. El relleno giroide distribuye las fuerzas de torsión de forma isotrópica, ideal para patas de robots móviles.

### C. Material y Temperaturas (PLA / PETG)
* **Material Sugerido:** **PLA** (Mayor rigidez y menor contracción térmica, perfecto para cunas electrónicas y tolerancias de servos de $0.3\text{ mm}$) o **PETG** (Mayor tenacidad frente a impactos).
* **Temperaturas de Trabajo:**
  * **PLA:** Boquilla: `210 °C` | Cama: `60 °C` | Ventilador de Capa: `100%`.
  * **PETG:** Boquilla: `240 °C` | Cama: `80 °C` | Ventilador de Capa: `30% - 50%`.

### D. Velocidad y Adherencia
* **Velocidad de Pared Externa:** `60 mm/s` (para asegurar la precisión de los pockets de los servos).
* **Tipo de Adherencia a Cama (Build Plate Adhesion):** `Falda (Skirt)` o `Borde (Brim)` de $5\text{ mm}$ (solo si la cama tiene mala adherencia o se usa PETG).

---

## 3. Preservación del Proyecto en Creality Print (`.cxprj`)

Para dejar el proyecto listo para abrir e imprimir en el futuro:

1. **Importar y Distribuir:** Abre Creality Print e importa los archivos STL en el plato correspondiente según la distribución de platos.
2. **Aplicar Perfil:** Selecciona el perfil de material (PLA/PETG) y ajusta los parámetros de relleno ($30\%$, Giroide) y paredes (4) indicados en la sección 2.
3. **Guardar el Proyecto:**
   * Ve al menú superior **Archivo (File) > Guardar Proyecto (Save Project)** o presiona `Ctrl + S`.
   * Guarda el archivo con la extensión **`.cxprj`** (Creality Print Project) bajo el nombre:
     `uss_spiderbot_print_project.cxprj`
   * Este archivo empaquetará los STL colocados en la cama, la escala de las piezas, las orientaciones y todos los parámetros de laminación para que solo tengas que hacer clic en "Laminar" (Slice) al día siguiente.
