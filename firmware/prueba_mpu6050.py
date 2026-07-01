# ============================================================
# USS SPIDERBOT — Script de Diagnóstico del Sensor GY-521 (MPU6050)
# Microcontrolador: ESP32 | Lenguaje: MicroPython
# ============================================================
# Este script es 100% autoportante (no requiere otras librerías).
# Escanea el bus I2C para verificar la conexión física del chip,
# despierta la IMU y grafica continuamente en consola:
# Aceleraciones (g), Inclinación (Pitch/Roll), Velocidad Angular (°/s)
# y la temperatura interna del silicio (°C).
# ============================================================

from machine import I2C, Pin
import time
import math

# Inicializar bus I2C por hardware en pines oficiales (GPIO 21 y 22)
SDA_PIN = 21
SCL_PIN = 22
print("=== Buscando Sensor GY-521 (MPU6050) ===")
print(f"Inicializando I2C en GPIO {SDA_PIN} (SDA) y GPIO {SCL_PIN} (SCL)...")

i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=400000)

# Escaneo del bus I2C
dispositivos = i2c.scan()
MPU_ADDR = 0x68

if MPU_ADDR not in dispositivos:
    print("\n[ERROR] ¡No se detectó el sensor MPU6050 (Dirección 0x68)!")
    print("Dispositivos encontrados en el bus:", [hex(d) for d in dispositivos])
    print("\nGuía de Diagnóstico Físico:")
    print("  1. Verifique que VCC de la IMU esté conectada a 3.3V de la ESP32.")
    print("  2. Verifique que GND de la IMU esté conectada a GND de la ESP32.")
    print("  3. Verifique que SDA esté en GPIO 21 y SCL en GPIO 22.")
    print("  4. Compruebe que no estén los pines SDA y SCL intercambiados.")
    print("  5. Asegúrese de que las soldaduras de los pines del módulo estén firmes.")
else:
    print(f"\n[OK] ¡Sensor MPU6050 detectado con éxito en la dirección {hex(MPU_ADDR)}!")
    
    # Despertar el sensor (sacarlo de modo Sleep escribiendo 0x00 en Power Management 0x6B)
    i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')
    time.sleep_ms(100)
    
    # Función auxiliar para convertir 2 bytes en entero de 16 bits con signo (short)
    def to_short(bytes_data):
        val = (bytes_data[0] << 8) | bytes_data[1]
        if val > 32767:
            val -= 65536
        return val

    print("\nIniciando lectura continua. Mueva el sensor para ver la telemetría...")
    print("Presione Ctrl+C en Thonny para detener la prueba.\n")
    print("-" * 75)
    print(" Pitch (°) | Roll (°)  | Accel (G) | Temp (°C) | Giroscopio X/Y/Z (°/s)")
    print("-" * 75)

    while True:
        try:
            # Leer 14 bytes consecutivos desde el registro de aceleración X (0x3B)
            # Esto obtiene de una vez: Accel X/Y/Z, Temp, y Gyro X/Y/Z
            data = i2c.readfrom_mem(MPU_ADDR, 0x3B, 14)
            
            # Decodificar lecturas brutas
            ax = to_short(data[0:2])
            ay = to_short(data[2:4])
            az = to_short(data[4:6])
            raw_temp = to_short(data[6:8])
            gx = to_short(data[8:10])
            gy = to_short(data[10:12])
            gz = to_short(data[12:14])
            
            # Escalar valores brutas a unidades físicas
            # Acelerómetro escala: +/-2g = 16384 LSB/g
            acc_x = ax / 16384.0
            acc_y = ay / 16384.0
            acc_z = az / 16384.0
            
            # Giroscopio escala: +/-250 deg/s = 131 LSB/(deg/s)
            gyro_x = gx / 131.0
            gyro_y = gy / 131.0
            gyro_z = gz / 131.0
            
            # Temperatura escala
            temp_c = (raw_temp / 340.0) + 36.53
            
            # Calcular Pitch y Roll a partir de la gravedad
            # Pitch (inclinación frontal)
            pitch = math.atan2(acc_y, math.sqrt(acc_x**2 + acc_z**2)) * (180.0 / math.pi)
            # Roll (inclinación lateral)
            roll = math.atan2(-acc_x, math.sqrt(acc_y**2 + acc_z**2)) * (180.0 / math.pi)
            
            # Magnitud del vector de gravedad (estática debe ser cercano a 1.0 G)
            gravedad = math.sqrt(acc_x**2 + acc_y**2 + acc_z**2)
            
            # Imprimir telemetría formateada en una sola línea interactiva
            print("  {:6.1f}   |  {:6.1f}   |   {:4.2f} G  |  {:5.1f}ºC   |  ({:5.1f}, {:5.1f}, {:5.1f})".format(
                pitch, roll, gravedad, temp_c, gyro_x, gyro_y, gyro_z
            ))
            
            # Tasa de muestreo de 10Hz (100ms)
            time.sleep_ms(100)
            
        except Exception as e:
            print(f"\n[ERROR] Fallo en la comunicación I2C: {e}")
            print("Verifique las conexiones y soldaduras.")
            time.sleep_ms(1000)
