# ============================================================
# USS SPIDERBOT — Prueba de 4 Servomotores Individuales (ESP32)
# Diseñado para probar servos en los pines GPIO directos de la ESP32 (4-DoF):
# FR_C (23), FL_C (17), RL_C (15), RR_C (13)
# Ejecutar en Thonny e ingresar los comandos en la consola.
# ============================================================

from machine import Pin, PWM
import time
import sys

# Mapeo de pines físicos de la ESP32 (4-DoF)
PINES_ACTIVOS = {
    "FR_C": 23,  # FR Coxa/Cadera
    "FL_C": 17,  # FL Coxa/Cadera
    "RL_C": 15,  # RL Coxa/Cadera
    "RR_C": 13   # RR Coxa/Cadera
}

servos = {}

print("Inicializando canales PWM a 50Hz para ESP32 (Resolución de 16-bit)...")
for nombre, pin_num in PINES_ACTIVOS.items():
    try:
        servos[nombre] = PWM(Pin(pin_num), freq=50)
        print(f"  [OK] Servo {nombre} configurado en GPIO {pin_num}")
    except Exception as e:
        print(f"  [ERROR] No se pudo inicializar {nombre} (GPIO {pin_num}): {e}")

def mover_servo(nombre, angulo):
    """Establece el ángulo (0-180) para un servo específico"""
    if nombre not in servos:
        print(f"[ERROR] El servo {nombre} no está inicializado.")
        return
        
    # Limitar el rango por seguridad
    angulo = max(0, min(180, angulo))
    
    # Rango calibrado de Duty (16-bit en ESP32: 0-65535)
    # min_duty = 1638 (~0.5ms para 0 grados)
    # max_duty = 8192 (~2.5ms para 180 grados)
    min_duty = 1638
    max_duty = 8192
    
    duty = int(min_duty + (angulo / 180.0) * (max_duty - min_duty))
    servos[nombre].duty_u16(duty)
    print(f"[MOVER] {nombre} (GPIO {PINES_ACTIVOS[nombre]}) -> Ángulo: {angulo}° | Duty: {duty}")

def mover_todos(angulo):
    """Mueve todos los servos configurados al mismo ángulo"""
    print(f"\nMoviendo todos los servos a {angulo}°...")
    for nombre in PINES_ACTIVOS.keys():
        mover_servo(nombre, angulo)

def test_barrido():
    """Realiza un barrido secuencial en todos los servos para prueba rápida"""
    print("\n--- Iniciando barrido automático secuencial ---")
    for nombre in PINES_ACTIVOS.keys():
        print(f"\nProbando canal: {nombre}")
        for ang in [90, 45, 90, 135, 90]:
            mover_servo(nombre, ang)
            time.sleep_ms(400)
    print("\n--- Barrido automático finalizado ---")

def main():
    if not servos:
        print("[ERROR] No hay ningún servo inicializado correctamente.")
        return
        
    print("\n=======================================================")
    print("  Prueba Controladora de 4 Servos Individual - ESP32   ")
    print("=======================================================")
    print("Opciones de comando:")
    print("  1. Escribe un ángulo (0-180) para mover TODOS los servos (ej: 90).")
    print("  2. Escribe '<PATA_SERVO> <ANGULO>' para mover uno solo.")
    print("     Opciones de PATA_SERVO:")
    print(f"       {list(PINES_ACTIVOS.keys())}")
    print("     Ejemplos: FR_C 45, RR_C 120")
    print("  3. Escribe 'b' para iniciar un barrido secuencial de prueba.")
    print("  4. Escribe 'salir' para terminar.")
    
    # Centrar todos al iniciar
    mover_todos(90)
    
    while True:
        try:
            entrada = input("\nIngrese comando: ").strip().upper()
            
            if entrada == 'SALIR':
                print("Finalizando prueba de servos.")
                break
            elif entrada == 'B':
                test_barrido()
            elif entrada == '':
                continue
            
            # Intentar procesar comandos del tipo "FR_C 45"
            elif " " in entrada:
                partes = entrada.split()
                if len(partes) == 2:
                    pin = partes[0]
                    if pin in PINES_ACTIVOS:
                        try:
                            angulo = int(partes[1])
                            if 0 <= angulo <= 180:
                                mover_servo(pin, angulo)
                            else:
                                print("[ALERTA] Ángulo fuera de rango (0-180).")
                        except ValueError:
                            print("[ERROR] El ángulo debe ser un número entero.")
                    else:
                        print(f"[ERROR] Servo no válido. Opciones: {list(PINES_ACTIVOS.keys())}")
                else:
                    print("[ERROR] Formato incorrecto. Use '<PATA_SERVO> <ANGULO>' (ej: FR_C 90).")
                    
            # Intentar procesar un ángulo global (ej: 90)
            else:
                try:
                    angulo = int(entrada)
                    if 0 <= angulo <= 180:
                        mover_todos(angulo)
                    else:
                        print("[ALERTA] Ángulo fuera de rango (0-180).")
                except ValueError:
                    print("[ERROR] Comando no reconocido. Escriba un número, '<PATA_SERVO> <ANGULO>', 'b' o 'salir'.")
                    
        except ValueError:
            print("[ERROR] Entrada no válida.")
        except KeyboardInterrupt:
            print("\nPrueba interrumpida por teclado.")
            break

if __name__ == "__main__":
    main()
