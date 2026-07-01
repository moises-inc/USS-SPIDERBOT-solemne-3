# ============================================================
# USS SPIDERBOT — Script de Calibración Inercial (MPU6050)
# Solemne 3 — Taller de Programación I
# Microcontrolador: ESP32
# Lenguaje: MicroPython
# ============================================================
# Toma 100 muestras de aceleración bruta con el robot inmóvil
# y plano, calcula los offsets promedio y los guarda en un
# archivo de texto para que main.py pueda leerlos al arrancar.
# ============================================================

from machine import I2C, Pin
from mpu6050 import MPU6050
import time
import sys

NUM_MUESTRAS = 100
OFFSETS_FILE = "mpu_offsets.txt"

print("Iniciando bus I2C (SDA=Pin 21, SCL=Pin 22, Freq=100kHz)...")
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)

dispositivos = i2c.scan()
print("Dispositivos I2C encontrados:", [hex(d) for d in dispositivos])

if not dispositivos:
    print("\n[ERROR] No se detectó ningún dispositivo I2C en el bus.")
    print("Revisa:")
    print("  1. Que el MPU6050 (GY-521) esté energizado (VCC a 3.3V/5V y GND a GND).")
    print("  2. Que los pines SDA y SCL estén conectados a GPIO 21 y GPIO 22 respectivamente.")
    print("  3. Que las soldaduras en los pines del MPU6050 hagan buen contacto.")
    sys.exit(1)

address = dispositivos[0]
print(f"Usando dispositivo inercial en dirección: {hex(address)}")
imu = MPU6050(i2c, address=address)

print("\nAsegúrate de que el robot esté inmóvil y sobre una superficie plana.")
print(f"Tomando {NUM_MUESTRAS} muestras...\n")
time.sleep_ms(1000)

sum_x = 0
sum_y = 0
sum_z = 0

for i in range(NUM_MUESTRAS):
    x, y, z = imu.read_accel_raw()
    sum_x += x
    sum_y += y
    sum_z += z
    if (i + 1) % 25 == 0:
        print(f"  Progreso: {i + 1}/{NUM_MUESTRAS} muestras")
    time.sleep_ms(10)

offset_x = sum_x // NUM_MUESTRAS
offset_y = sum_y // NUM_MUESTRAS
offset_z = sum_z // NUM_MUESTRAS

print(f"\nOffsets calculados (valores brutos):")
print(f"  X = {offset_x}")
print(f"  Y = {offset_y}")
print(f"  Z = {offset_z}")

with open(OFFSETS_FILE, "w") as f:
    f.write(f"{offset_x},{offset_y},{offset_z}\n")

print(f"\n[OK] Offsets guardados en {OFFSETS_FILE}")
print("Calibración completada.")
