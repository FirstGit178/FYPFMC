# This controller doesn't know if the hardware is 
# real or emulated, it just runs the test sequence regardless.

import threading

class TestController:
    """
    Manages the high-voltage testing sequence, coordinating between a hardware tester,
    an ESP32 status indicator, and a UI update callback.
    """
    def __init__(self, on_update, tester, esp32):
        # Callbacks and hardware interfaces
        self.on_update = on_update  # Function to call when state changes (e.g., to refresh UI)
        self.tester = tester        # High-voltage tester hardware interface
        self.esp32 = esp32          # ESP32 controller for external status LEDs/displays

        # Threading and Synchronization
        self.stop_event = threading.Event() # Signal to abort running tests immediately
        self.lock = threading.Lock()        # Ensures thread-safe access to shared state variables
        
        # Test State Variables
        self.state = "IDLE"          # Overall status: IDLE, TESTING, PASS, FAIL, ERROR
        self.voltage = 0             # Current applied voltage
        self.leakage = 0.0           # Current leakage reading (mA)
        self.test1 = "STANDBY"       # Progress of first test phase
        self.test2 = "STANDBY"       # Progress of second test phase
        self.hvil_state = "UNKNOWN"  # High Voltage Interlock Loop state (OPEN/CLOSED)

    def snapshot(self):
        """Returns a thread-safe dictionary of the current controller state for UI rendering."""
        with self.lock:
            return {k: getattr(self, k) for k in ["state", "voltage", "leakage", "test1", "test2", "hvil_state"]}

    def _set_values(self, **values):
        """Updates multiple state variables atomically and triggers the UI update callback."""
        with self.lock:
            for key, value in values.items():
                setattr(self, key, value)
        self.on_update()

    def start(self, fault=False):
        """
        Initiates the test sequence in a separate daemon thread.
        Prevents starting if already testing, in error, or if the HVIL is open.
        """
        with self.lock:
            if self.state in ("TESTING", "ERROR") or self.hvil_state != "CLOSED":
                return
            self.stop_event.clear()
            self.state = "TESTING"
            self.voltage = 0
            self.leakage = 0.0
            self.test1 = "RUNNING"
            self.test2 = "STANDBY"
        
        self.on_update()
        # Run the sequence in the background so the UI/main thread remains responsive
        threading.Thread(target=self._run_sequence, args=(fault,), daemon=True).start()

    def _ramp(self, voltages, target_voltage, test_name, leakage_limit_ua):
        """
        Iterates through a list of voltages, checking leakage at each step.
        Returns True if the ramp completes successfully, False if a limit is exceeded or aborted.
        """
        for voltage in voltages:
            if self.stop_event.is_set():
                return False

            self.tester.set_voltage(voltage)
            leakage_ma = self.tester.read_leakage(voltage, target_voltage)
            self._set_values(voltage=voltage, leakage=leakage_ma)

            # Convert the reading from mA to µA before comparing with the limit.
            if leakage_ma * 1000 > leakage_limit_ua:
                self.tester.safe_output() # Immediate hardware shutdown
                self._set_values(
                    state="FAIL",
                    **{test_name: "FAILED"},
                    **({"test2": "BYPASSED"} if test_name == "test1" else {})
                )
                self.esp32.set_status("FAIL")
                return False

            # Wait 0.7s between steps; returns False immediately if stop_event is triggered
            if self.stop_event.wait(0.7):
                return False

        return True

    def _run_sequence(self, fault):
        """The main logic loop for the test sequence."""
        if fault:
            # Simulated fault scenario: ramps to 1100V, then forces a failure state
            if not self._ramp(range(100, 1101, 200), 1500, "test1", 500): return
            self._set_values(voltage=1150, leakage=18.95)
            if self.stop_event.wait(0.5): return
            self._set_values(state="FAIL", test1="FAILED", test2="BYPASSED")
            self.esp32.set_status("FAIL")
            return

        # --- Standard Test Path ---
        # Test 1: High Voltage Ramp (100V to 1500V, 500µA limit)
        if not self._ramp(range(100, 1501, 200), 1500, "test1", 500): return
        self._set_values(test1="PASSED")
        
        if self.stop_event.wait(1.2): return
        
        # Test 2: Lower Voltage Ramp (0V to 500V, 100µA limit)
        self._set_values(test2="RUNNING")
        if not self._ramp(range(0, 501, 100), 500, "test2", 100): return
        
        if not self.stop_event.is_set():
            self._set_values(state="PASS", test2="PASSED")
            self.esp32.set_status("PASS")

    def set_hvil_state(self, state):
        """Updates the HVIL state. Opening the HVIL triggers an immediate emergency shutdown."""
        state = state.upper()
        if state == "OPEN": 
            self.emergency_shutdown()
        elif state == "CLOSED": 
            self._set_values(hvil_state="CLOSED")

    def emergency_shutdown(self):
        """Aborts all operations, shuts down hardware output, and sets state to ERROR."""
        self.stop_event.set()
        self.tester.safe_output()
        self.esp32.set_status("ERROR")
        self._set_values(
            state="ERROR", 
            voltage=0, 
            leakage=0.0, 
            test1="ABORTED", 
            test2="ABORTED", 
            hvil_state="OPEN"
        )

    def reset(self):
        """Returns the controller to the initial IDLE state and ensures hardware is safe."""
        self.stop_event.set()
        self.tester.safe_output()
        self.esp32.set_status("IDLE")
        self._set_values(
            state="IDLE", 
            voltage=0, 
            leakage=0.0, 
            test1="STANDBY", 
            test2="STANDBY", 
            hvil_state="UNKNOWN"
        )
