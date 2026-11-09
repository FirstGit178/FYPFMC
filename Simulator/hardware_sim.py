#  This is where the simulated hardware is created.

class SimulatedTester:
    """Simulates the tester; these settings do not affect real hardware."""

    def __init__(self):
        # Simulated leakage readings, in microamps.
        self.leakage_1500v_ua = 250.0
        self.leakage_500v_ua = 50.0

    def set_voltage(self, voltage):
        pass  # No real voltage is applied in simulation.

    def read_leakage(self, voltage, target_voltage):
        # Return mA because the GUI displays leakage in mA.
        if target_voltage == 1500:
            return self.leakage_1500v_ua / 1000
        if target_voltage == 500:
            return self.leakage_500v_ua / 1000
        raise ValueError(f"Unsupported simulated target: {target_voltage} V")

    def safe_output(self):
        pass  # No real hardware is connected.

class SimulatedESP32:
    """Simulation adapter; replace with ESP32 communication code."""
    def set_status(self, status):
        pass
    
    def read_switches(self):
        return  True  # Simulate the interlock as closed