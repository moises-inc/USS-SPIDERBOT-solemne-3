import time

class PCA9685:
    """Driver simple para el controlador de servos I2C PCA9685 en MicroPython."""
    
    def __init__(self, i2c, address=0x40):
        self.i2c = i2c
        self.address = address
        self.reset()
        self.set_pwm_freq(50) # 50Hz para servos analógicos estándar
        
    def reset(self):
        self.write_reg(0x00, 0x00) # MODE1 normal
        
    def write_reg(self, reg, val):
        self.i2c.writeto_mem(self.address, reg, bytes([val]))
        
    def read_reg(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]
        
    def set_pwm_freq(self, freq):
        """Ajusta la frecuencia del PWM en Hz."""
        prescaleval = 25000000.0 # 25MHz reloj interno
        prescaleval /= 4096.0    # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = int(prescaleval + 0.5)
        
        oldmode = self.read_reg(0x00)
        newmode = (oldmode & 0x7F) | 0x10 # Sleep mode para configurar prescale
        self.write_reg(0x00, newmode)
        self.write_reg(0xFE, prescale) # Escribir prescale
        self.write_reg(0x00, oldmode)
        time.sleep_us(500)
        self.write_reg(0x00, oldmode | 0xa1) # Reiniciar modo1 con auto-incremento
        
    def set_pwm(self, channel, on, off):
        """Ajusta los tiempos ON y OFF de PWM (0-4095) para un canal específico."""
        self.write_reg(0x06 + 4 * channel, on & 0xFF)
        self.write_reg(0x07 + 4 * channel, (on >> 8) & 0xFF)
        self.write_reg(0x08 + 4 * channel, off & 0xFF)
        self.write_reg(0x09 + 4 * channel, (off >> 8) & 0xFF)
        
    def set_servo_angle(self, channel, angle):
        """
        Ajusta el ángulo del servo (0 a 180 grados).
        Mapea el ángulo al ciclo de trabajo de pulso del servo (típicamente 0.5ms a 2.5ms).
        """
        # Pulso en ticks (de 0 a 4095): 50Hz -> Periodo = 20ms. 
        # 1ms = 204 ticks, 2ms = 409 ticks.
        # Rango típico de servos SG90: ~130 a ~530 ticks (aproximadamente 0.6ms a 2.6ms)
        min_pulse = 130
        max_pulse = 530
        
        # Clampear ángulo
        if angle < 0: angle = 0
        if angle > 180: angle = 180
            
        off_tick = int(min_pulse + (angle / 180.0) * (max_pulse - min_pulse))
        self.set_pwm(channel, 0, off_tick)
