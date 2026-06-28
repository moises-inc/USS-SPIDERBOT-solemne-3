import math

class IASensorClassifier:
    """
    Clasificador de estados físicos del robot mediante árbol de decisión.
    Evalúa aceleración y giroscopio para detectar caídas, empujes y derrapes.
    """

    # Umbrales de clasificación
    PITCH_FALLEN_THRESHOLD = 45.0
    ROLL_FALLEN_THRESHOLD = 45.0
    FREE_FALL_ACCEL_THRESHOLD = 0.2
    IMPACT_THRESHOLD = 2.0
    GYRO_PUSH_THRESHOLD = 120.0
    SLIP_ACCEL_VAR_THRESHOLD = 0.08

    # Sensibilidad MPU6050 por defecto (Acelerómetro ±2g -> 16384 LSB/g)
    ACCEL_LSB_PER_G = 16384.0
    # Sensibilidad Giroscopio ±250°/s -> 131 LSB/°/s
    GYRO_LSB_PER_DPS = 131.0

    def __init__(self):
        self.ax_hist = []
        self.hist_len = 5

    def _accel_to_g(self, raw):
        return raw / self.ACCEL_LSB_PER_G

    def _gyro_to_dps(self, raw):
        return raw / self.GYRO_LSB_PER_DPS

    def _compute_pitch_roll(self, ax_g, ay_g, az_g):
        if ax_g == 0 and ay_g == 0 and az_g == 0:
            return 0.0, 0.0
        pitch = math.atan2(ay_g, math.sqrt(ax_g * ax_g + az_g * az_g)) * (180.0 / math.pi)
        roll = math.atan2(-ax_g, math.sqrt(ay_g * ay_g + az_g * az_g)) * (180.0 / math.pi)
        return pitch, roll

    def classify(self, ax, ay, az, gx, gy, gz, comando_actual):
        """
        Clasifica el estado actual del robot.
        ax, ay, az: valores brutos del acelerómetro (int16).
        gx, gy, gz: valores brutos del giroscopio (int16).
        comando_actual: string del comando de movimiento actual.
        Retorna: "NORMAL", "FALLEN", "PUSHED", o "SLIPPING".
        """
        ax_g = self._accel_to_g(ax)
        ay_g = self._accel_to_g(ay)
        az_g = self._accel_to_g(az)

        gx_dps = self._gyro_to_dps(gx)
        gy_dps = self._gyro_to_dps(gy)
        gz_dps = self._gyro_to_dps(gz)

        # Magnitud del vector aceleración
        accel_magnitude = math.sqrt(ax_g * ax_g + ay_g * ay_g + az_g * az_g)

        # Magnitud del giroscopio
        gyro_magnitude = math.sqrt(gx_dps * gx_dps + gy_dps * gy_dps + gz_dps * gz_dps)

        pitch, roll = self._compute_pitch_roll(ax_g, ay_g, az_g)

        # FALLEN: caída libre, inclinación crítica o impacto
        if accel_magnitude < self.FREE_FALL_ACCEL_THRESHOLD:
            return "FALLEN"
        if abs(pitch) > self.PITCH_FALLEN_THRESHOLD or abs(roll) > self.ROLL_FALLEN_THRESHOLD:
            return "FALLEN"
        if accel_magnitude > self.IMPACT_THRESHOLD:
            return "FALLEN"

        # PUSHED: perturbación externa en reposo
        if comando_actual in ("stop", "reposo") and gyro_magnitude > self.GYRO_PUSH_THRESHOLD:
            return "PUSHED"

        # SLIPPING: derrape en marcha (baja varianza aceleración longitudinal)
        if comando_actual in ("forward", "backward"):
            self.ax_hist.append(ax_g)
            if len(self.ax_hist) > self.hist_len:
                self.ax_hist.pop(0)
            if len(self.ax_hist) == self.hist_len:
                mean_ax = sum(self.ax_hist) / self.hist_len
                variance = sum((v - mean_ax) ** 2 for v in self.ax_hist) / self.hist_len
                if variance < self.SLIP_ACCEL_VAR_THRESHOLD:
                    return "SLIPPING"
        else:
            self.ax_hist.clear()

        return "NORMAL"
