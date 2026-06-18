import math

class MPU6050:
    """Driver simple para acelerómetro MPU6050 en MicroPython."""
    
    def __init__(self, i2c, address=0x68):
        self.i2c = i2c
        self.address = address
        self.offset_x = 0
        self.offset_y = 0
        self.offset_z = 0
        # Despertar MPU6050 (por defecto entra en sleep)
        self.i2c.writeto_mem(self.address, 0x6B, b'\x00')
        
    def set_offsets(self, ox, oy, oz):
        """Establece los offsets de calibración para cada eje."""
        self.offset_x = ox
        self.offset_y = oy
        self.offset_z = oz
        
    def read_accel_raw(self):
        """Lee las aceleraciones brutas en X, Y, Z."""
        data = self.i2c.readfrom_mem(self.address, 0x3B, 6)
        x = self._to_short(data[0:2])
        y = self._to_short(data[2:4])
        z = self._to_short(data[4:6])
        return x, y, z
        
    def read_accel_calibrated(self):
        """Lee las aceleraciones con offsets sustraídos (valores calibrados)."""
        x, y, z = self.read_accel_raw()
        return x - self.offset_x, y - self.offset_y, z - self.offset_z
        
    def _to_short(self, bytes_data):
        val = (bytes_data[0] << 8) | bytes_data[1]
        if val > 32767:
            val -= 65536
        return val
        
    def obtener_inclinacion(self):
        """Calcula los ángulos de inclinación (pitch y roll) en grados."""
        x, y, z = self.read_accel_calibrated()
        
        # Evitar división por cero
        if x == 0 and y == 0 and z == 0:
            return 0.0, 0.0
            
        # Calcular Pitch y Roll en radianes y convertirlos a grados
        # Pitch: Inclinación frontal
        pitch = math.atan2(y, math.sqrt(x*x + z*z)) * (180.0 / math.pi)
        # Roll: Inclinación lateral
        roll = math.atan2(-x, math.sqrt(y*y + z*z)) * (180.0 / math.pi)
        
        return round(pitch, 1), round(roll, 1)
