from machine import Pin
import time

class SonarSensor:
    """Clase para medir distancia usando sensor de ultrasonido HC-SR04."""
    
    def __init__(self, trigger_pin=18, echo_pin=19):
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trigger.value(0)
        time.sleep_ms(20) # Estabilizar
        
    def medir_distancia(self) -> float:
        """Envía pulso y retorna la distancia medida en cm. Retorna -1.0 en caso de error."""
        # 1. Asegurar trigger en bajo
        self.trigger.value(0)
        time.sleep_us(2)
        
        # 2. Pulso de 10us
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        
        # 3. Esperar inicio de pulso (ECHO = 1)
        timeout_start = time.ticks_us()
        while self.echo.value() == 0:
            if time.ticks_diff(time.ticks_us(), timeout_start) > 30000: # 30ms timeout
                return -1.0
                
        t_start = time.ticks_us()
        
        # 4. Esperar fin de pulso (ECHO = 0)
        timeout_end = time.ticks_us()
        while self.echo.value() == 1:
            if time.ticks_diff(time.ticks_us(), timeout_end) > 30000: # 30ms timeout
                return -1.0
                
        t_end = time.ticks_us()
        
        # 5. Calcular distancia
        duracion = time.ticks_diff(t_end, t_start)
        distancia = (duracion * 0.0343) / 2
        
        if 2.0 <= distancia <= 400.0:
            return round(distancia, 1)
        else:
            return -1.0
