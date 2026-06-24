from machine import Pin, PWM
import time

class BuzzerAlert:
    """
    Clase para control de sonidos y alertas del Buzzer.
    Optimizado para buzzer activo (generación de melodías rítmicas digitales)
    y compatible con buzzer pasivo (frecuencias PWM).
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
            self.pin.value(1) # Encendido continuo (el buzzer activo oscila internamente)
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

    # ── MELODÍAS RÍTMICAS PARA BUZZER ACTIVO ──
    
    def play_startup(self):
        """Melodía de encendido: tres beeps rápidos ascendentes en ritmo (Trino)"""
        self.beep(40)
        time.sleep_ms(40)
        self.beep(40)
        time.sleep_ms(40)
        self.beep(120)
        print("[BUZZER] Melodía de inicio reproducida.")

    def play_critical_alert(self):
        """Alerta de proximidad crítica (obstáculo < 15cm): beeps muy rápidos continuos"""
        for _ in range(2):
            self.beep(50)
            time.sleep_ms(30)

    def play_warning_alert(self):
        """Alerta de advertencia (obstáculo < 30cm): un beep corto espaciado"""
        self.beep(30)

    def play_shutdown(self):
        """Melodía de apagado: un beep largo y luego dos cortos descendentes"""
        self.beep(180)
        time.sleep_ms(80)
        self.beep(60)
        time.sleep_ms(40)
        self.beep(60)
        print("[BUZZER] Melodía de apagado reproducida.")

    def play_gait_step(self):
        """Sonido de paso de caminata: un tick acústico muy corto"""
        self.beep(15)

    def apagar(self):
        if self.es_pasivo:
            self.pwm.duty(0)
        else:
            self.pin.value(0)
