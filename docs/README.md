# USS SpiderBot — Wiki Técnica de Código

Bienvenido a la wiki técnica del **USS SpiderBot**, un robot caminador cuadrúpedo de **8 grados de libertad (8-DoF)** desarrollado para la asignatura de **Taller de Programación I (Universidad San Sebastián)**. 

Este robot ha sido diseñado con estabilidad inercial activa para desplazarse de forma segura sobre terrenos rugosos o inclinados, prevención reactiva de colisiones frontales y un panel de control remoto web asíncrono y offline accesible desde cualquier navegador.

---

## 🚀 Stack Tecnológico

El proyecto integra tecnologías de hardware embebido, desarrollo web nativo y modelado tridimensional paramétrico:

*   **Microcontrolador principal:** ESP32 DevKit V1 (38 pines) ejecutando **MicroPython v1.20+**.
*   **Locomoción y multitarea:** Concurrencia cooperativa no bloqueante mediante la librería estándar **`uasyncio` (asyncio)** de MicroPython.
*   **Actuadores:** 8x Servomotores analógicos SG90 controlados mediante el chip de expansión PWM de 12 bits **PCA9685** sobre bus físico I2C.
*   **Sensores:**
    *   Unidad de Medida Inercial (IMU) **MPU6050** de 6 ejes para el cálculo dinámico de inclinación (Pitch y Roll).
    *   Sensor ultrasónico de distancia **HC-SR04** para evasión de obstáculos.
*   **Interfaz de Control Remoto:** Servidor HTTP embebido asíncrono en socket TCP (puerto 80) que sirve un Dashboard web en HTML5, CSS3 Glassmorphism y Vanilla JavaScript (sin CDNs, 100% offline).
*   **Modelado 3D Estructural:** Piezas paramétricas imprimibles en FDM modeladas íntegramente en **OpenSCAD**.

---

## 📚 Tabla de Contenidos de la Wiki

Navega a través de las secciones de documentación técnica de este repositorio:

1.  **[Arquitectura General e Inferencia de Postura](ARCHITECTURE.md):** Conoce el flujo de ejecución asíncrono, la teoría de la marcha de gateo (Crawl Gait) y la lógica matemática de la estabilización inercial activa.
2.  **[Diccionario de Componentes y Módulos](MODULES.md):** Detalle de cada archivo de código fuente, sus responsabilidades, funciones principales, variables físicas y dependencias internas de importación.

---

*Desarrollado en la Universidad San Sebastián. Año 2026.*
