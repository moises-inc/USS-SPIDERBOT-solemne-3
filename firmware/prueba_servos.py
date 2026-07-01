# ============================================================
# USS SPIDERBOT — Script de Prueba de Servomotores (MicroPython)
# Diseñado para ejecutarse interactiva o automáticamente en Thonny IDE.
# ============================================================

from machine import I2C, Pin, PWM
import time
import sys

# Mapeo descriptivo de canales y nombres (4-DoF)
NOMBRES_SERVOS = {
    0: "Canal 0 (Pata FR - Coxa/Cadera)",
    1: "Canal 1 (Pata FL - Coxa/Cadera)",
    2: "Canal 2 (Pata RL - Coxa/Cadera)",
    3: "Canal 3 (Pata RR - Coxa/Cadera)"
}

# Mapeo de pines GPIO directos de la ESP32 (Control Directo 4-DoF)
PINE_GPIO_DIRECTOS = {
    0: 13, # Pata FR
    1: 15, # Pata FL
    2: 4,  # Pata RL
    3: 23  # Pata RR
}



# Clase mínima para GPIO Directo
class GPIOServoDriver:
    def __init__(self, pins):
        self.pwms = {}
        for ch, pin_num in pins.items():
            try:
                self.pwms[ch] = PWM(Pin(pin_num), freq=50)
            except Exception as e:
                print(f"[ERROR] No se pudo inicializar PWM en GPIO {pin_num}: {e}")
                
    def set_angle(self, channel, angle):
        if channel in self.pwms:
            angle = max(0, min(180, angle))
            min_duty = 1638  # ~0.5ms (1638/65535)
            max_duty = 8192  # ~2.5ms (8192/65535)
            duty = int(min_duty + (angle / 180.0) * (max_duty - min_duty))
            self.pwms[channel].duty_u16(duty)

def realizar_barrido(driver, canal, nombre):
    print(f"\n---> Iniciando barrido en: {nombre}")
    print("Moviendo a 90 grados (Centro)...")
    driver.set_angle(canal, 90)
    time.sleep_ms(800)
    
    print("Moviendo a 45 grados...")
    driver.set_angle(canal, 45)
    time.sleep_ms(800)
    
    print("Moviendo a 135 grados...")
    driver.set_angle(canal, 135)
    time.sleep_ms(800)
    
    print("Regresando a 90 grados...")
    driver.set_angle(canal, 90)
    time.sleep_ms(800)
    print("Barrido terminado.")

def main():
    print("=====================================================")
    print("          Prueba de Servomotores - USS SpiderBot      ")
    print("=====================================================")
    
    # Inicializar el controlador directo por GPIO para los 8 servos
    print("Inicializando driver GPIO Directo (8 canales activos)...")
    driver = GPIOServoDriver(PINE_GPIO_DIRECTOS)
        
    print("\nModos de prueba:")
    print("1. Barrido automático de todos los canales (0 al 7)")
    print("2. Barrido interactivo paso a paso (presionar ENTER para cambiar)")
    print("3. Posicionar todos los servos a 90 grados (Modo Armado/Calibración)")
    
    try:
        seleccion = input("\nSeleccione una opción (1, 2 o 3): ").strip()
    except Exception:
        seleccion = "1" # Fallback si Thonny no recibe stdin interactiva en la primera
        
    if seleccion == "3":
        print("\nColocando todos los servos (0-3) a 90 grados...")
        for ch in range(4):
            driver.set_angle(ch, 90)
            time.sleep_ms(100)
        print("[OK] Todos los servos centrados a 90°. ¡Listo para el acople mecánico!")
        
    elif seleccion == "2":
        print("\n--- PRUEBA INTERACTIVA PASO A PASO ---")
        for ch in range(4):
            nombre = NOMBRES_SERVOS.get(ch, f"Canal {ch}")
            print(f"\nSiguiente servo a probar: {nombre}")
            input("Presione ENTER para iniciar el barrido del servo...")
            realizar_barrido(driver, ch, nombre)
        print("\n[OK] Fin de la prueba interactiva.")
        
    else:
        print("\n--- PRUEBA AUTOMÁTICA DE BARRIDO ---")
        for ch in range(4):
            nombre = NOMBRES_SERVOS.get(ch, f"Canal {ch}")
            realizar_barrido(driver, ch, nombre)
            time.sleep_ms(200)
        print("\n[OK] Fin de la prueba de barrido automático.")

if __name__ == "__main__":
    main()
