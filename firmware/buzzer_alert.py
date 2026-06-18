from machine import Pin, PWM
import time

class BuzzerAlert:
    """
    Clase para control de sonidos y alertas del Buzzer.
    Soporta buzzer activo (salida digital directa) y pasivo (PWM).
    """
    
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
            self.pin.value(1) # Encendido continuo (genera oscilación interna)
            time.sleep_ms(duracion_ms)
            self.pin.value(0)
            
    def beep(self, duration_ms=100):
        self.emitir_sonido(frecuencia=1000, duracion_ms=duration_ms)
        
    def alarma_rapida(self, repeticiones=3):
        for _ in range(repeticiones):
            self.beep(80)
            time.sleep_ms(80)
            
    def alerta_postura(self):
        # Alerta intermitente de frecuencia más alta y audible (2000Hz)
        self.emitir_sonido(frecuencia=2000, duracion_ms=250)
        time.sleep_ms(100)
        
    def apagar(self):
        if self.es_pasivo:
            self.pwm.duty(0)
        else:
            self.pin.value(0)
