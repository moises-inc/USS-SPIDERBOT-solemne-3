# ============================================================
# USS SPIDERBOT — Prueba Autoportante de Sonar y Buzzer (ESP32)
# Diseñado para verificar el sensor ultrasónico HC-SR04
# (Trigger: Pin 18, Echo: Pin 19) y el Buzzer (Pin 14).
# SCRIPT AUTOPORTANTE: No requiere subir dependencias a la ESP32.
# ============================================================

from machine import Pin, PWM
import time

# ── 1. CLASE AUTOCONTENIDA DEL SENSOR ULTRASÓNICO ────────────────
class SonarSensor:
    """Clase para medir distancia usando sensor de ultrasonido HC-SR04."""
    
    def __init__(self, trigger_pin=18, echo_pin=19):
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trigger.value(0)
        time.sleep_ms(20) # Estabilizar
        
    def medir_distancia(self) -> float:
        """Envía pulso y retorna la distancia medida en cm. Retorna -1.0 en caso de error."""
        self.trigger.value(0)
        time.sleep_us(2)
        
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        
        timeout_start = time.ticks_us()
        while self.echo.value() == 0:
            if time.ticks_diff(time.ticks_us(), timeout_start) > 30000: # 30ms timeout
                return -1.0
                
        t_start = time.ticks_us()
        
        timeout_end = time.ticks_us()
        while self.echo.value() == 1:
            if time.ticks_diff(time.ticks_us(), timeout_end) > 30000: # 30ms timeout
                return -1.0
                
        t_end = time.ticks_us()
        
        duracion = time.ticks_diff(t_end, t_start)
        distancia = (duracion * 0.0343) / 2
        
        if 2.0 <= distancia <= 400.0:
            return round(distancia, 1)
        else:
            return -1.0

# ── 2. CLASE AUTOCONTENIDA DEL BUZZER ───────────────────────────
class BuzzerAlert:
    """Clase para control de sonidos y alertas del Buzzer."""
    
    def __init__(self, pin_number=14, es_pasivo=False):
        self.pin_num = pin_number
        self.es_pasivo = es_pasivo
        
        if self.es_pasivo:
            self.pwm = PWM(Pin(self.pin_num))
            self.pwm.duty(0) # Apagado inicialmente
        else:
            self.pin = Pin(self.pin_num, Pin.OUT)
            self.pin.value(0)
            
    def emitir_sonido(self, frecuencia=1000, duracion_ms=100):
        if self.es_pasivo:
            self.pwm.freq(frecuencia)
            self.pwm.duty(512) # 50% ciclo de trabajo para volumen máximo
            time.sleep_ms(duracion_ms)
            self.pwm.duty(0)
        else:
            self.pin.value(1) # Encendido continuo
            time.sleep_ms(duracion_ms)
            self.pin.value(0)
            
    def beep(self, duration_ms=100):
        self.emitir_sonido(frecuencia=1000, duracion_ms=duration_ms)
        
    def alarma_rapida(self, repeticiones=3):
        for _ in range(repeticiones):
            self.beep(80)
            time.sleep_ms(80)
            
    def apagar(self):
        if self.es_pasivo:
            self.pwm.duty(0)
        else:
            self.pin.value(0)

# ── 3. CONFIGURACIÓN DE PINES ────────────────────────────────────
PIN_TRIGGER = 18
PIN_ECHO = 19
PIN_BUZZER = 14
BUZZER_PASIVO = False # Cambia a True si tu buzzer requiere modulación PWM

# ── 4. BUCLE DE PRUEBA PRINCIPAL ─────────────────────────────────
def main():
    print("=======================================================")
    print("  USS SpiderBot - Prueba Sonar y Buzzer Autoportante")
    print("=======================================================")
    
    print("Inicializando componentes...")
    sonar = SonarSensor(trigger_pin=PIN_TRIGGER, echo_pin=PIN_ECHO)
    buzzer = BuzzerAlert(pin_number=PIN_BUZZER, es_pasivo=BUZZER_PASIVO)
    print("  [OK] Inicializados con éxito.")
    
    # Beep de confirmación al arrancar
    print("\nEmitiendo beep de prueba...")
    buzzer.beep(150)
    time.sleep_ms(300)
    
    print("\nIniciando bucle de medición continua (5 lecturas/seg)...")
    print("El buzzer emitirá una alarma rápida si detecta un objeto a menos de 15 cm.")
    print("Presiona Ctrl+C en Thonny para detener la prueba.\n")
    print(f"{'Tiempo (s)':<12}{'Distancia (cm)':<18}{'Estado':<15}")
    print("-" * 45)
    
    t_inicio = time.time()
    
    while True:
        try:
            # Medir distancia
            distancia = sonar.medir_distancia()
            tiempo_transcurrido = time.time() - t_inicio
            
            estado = "SEGURO"
            
            if distancia == -1.0:
                dist_str = "Error de lectura"
                estado = "FALLA"
            else:
                dist_str = f"{distancia:.1f} cm"
                
                # Proximidad crítica (< 15cm)
                if 0.0 < distancia < 15.0:
                    estado = "CRÍTICO (ALERTA)"
                    buzzer.alarma_rapida(repeticiones=2)
                # Advertencia (< 30cm)
                elif 15.0 <= distancia < 30.0:
                    estado = "ADVERTENCIA"
                    buzzer.beep(40) # Pitido corto
            
            # Mostrar telemetría
            print(f"{tiempo_transcurrido:<12.1f}{dist_str:<18}{estado:<15}")
            
            time.sleep_ms(200)
            
        except KeyboardInterrupt:
            print("\nPrueba finalizada.")
            buzzer.apagar()
            break
        except Exception as e:
            print(f"\n[ERROR] Excepción: {e}")
            time.sleep_ms(1000)

if __name__ == "__main__":
    main()
