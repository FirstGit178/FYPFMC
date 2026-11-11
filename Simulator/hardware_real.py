# This is where I will add the code for PySerial or PyUSB.


class ActualHipotTester:
    """The real driver for the USB Hipot Tester."""
    def set_voltage(self, voltage):
        # Put actual USB write command here
        print(f"REAL HARDWARE: Setting voltage to {voltage}V")

    def read_leakage(self, voltage, target_voltage):
        # Put actual USB read command here
        return 0.0

    def safe_output(self):
    #    Place the Kill Power command here; however, the tester will have a physical E-Stop button as a backup safety option.
    #    The tester will not be able to turn on the output again until the E-Stop is released
        print("REAL HARDWARE: Emergency Safe Output Activated")

class ActualESP32:
    """Driver for the real ESP32."""

    def set_status(self, status):
        raise NotImplementedError("Serial communication is not implemented")

    def read_switches(self):
        raise NotImplementedError("Serial communication is not implemented")