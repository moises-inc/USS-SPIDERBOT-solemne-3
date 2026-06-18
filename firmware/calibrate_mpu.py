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

NUM_MUESTRAS = 100
OFFSETS_FILE = "mpu_offsets.txt"

print("Iniciando calibración del MPU6050...")
print("Asegúrate de que el robot esté inmóvil y sobre una superficie plana.")
print(f"Tomando {NUM_MUESTRAS} muestras...\n")

i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
imu = MPU6050(i2c, address=0x68)

time.sleep_ms(500)

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
