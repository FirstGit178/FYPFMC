# This controller doesn't know if the hardware is 
# real or emulated, it just runs the test sequence regardless.

import threading

class TestController:
    def __init__(self, on_update, tester, esp32):
        self.on_update = on_update
        self.tester = tester 
        self.esp32 = esp32

        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.state = "IDLE"
        self.voltage = 0
        self.leakage = 0.0
        self.test1 = "STANDBY"
        self.test2 = "STANDBY"
        self.hvil_state = "UNKNOWN"

    def snapshot(self):
        with self.lock:
            return {k: getattr(self, k) for k in ["state", "voltage", "leakage", "test1", "test2", "hvil_state"]}

    def _set_values(self, **values):
        with self.lock:
            for key, value in values.items():
                setattr(self, key, value)
        self.on_update()

    def start(self, fault=False):
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
        threading.Thread(target=self._run_sequence, args=(fault,), daemon=True).start()

    def _ramp(self, voltages, target_voltage, test_name, leakage_limit_ua):
        for voltage in voltages:
            if self.stop_event.is_set():
                return False

            self.tester.set_voltage(voltage)
            leakage_ma = self.tester.read_leakage(voltage, target_voltage)
            self._set_values(voltage=voltage, leakage=leakage_ma)

            # Convert the reading from mA to µA before comparing with the limit.
            if leakage_ma * 1000 > leakage_limit_ua:
                self.tester.safe_output()
                self._set_values(
                    state="FAIL",
                    **{test_name: "FAILED"},
                    **({"test2": "BYPASSED"} if test_name == "test1" else {})
                )
                self.esp32.set_status("FAIL")
                return False

            if self.stop_event.wait(0.7):
                return False

        return True

    def _run_sequence(self, fault):
        if fault:
            # Fault-demo ramp: 1500 V test, 500 µA limit.
            if not self._ramp(range(100, 1101, 200), 1500, "test1", 500): return
            self._set_values(voltage=1150, leakage=18.95)
            if self.stop_event.wait(0.5): return
            self._set_values(state="FAIL", test1="FAILED", test2="BYPASSED")
            self.esp32.set_status("FAIL")
            return
        # Standard first test: 1500 V test, 500 µA limit.
        if not self._ramp(range(100, 1501, 200), 1500, "test1", 500): return
        self._set_values(test1="PASSED")
        if self.stop_event.wait(1.2): return
        self._set_values(test2="RUNNING")
        # Standard second test: 500 V test, 100 µA limit.
        if not self._ramp(range(0, 501, 100), 500, "test2", 100): return
        if not self.stop_event.is_set():
            self._set_values(state="PASS", test2="PASSED")
            self.esp32.set_status("PASS")

    def set_hvil_state(self, state):
        state = state.upper()
        if state == "OPEN": self.emergency_shutdown()
        elif state == "CLOSED": self._set_values(hvil_state="CLOSED")

    def emergency_shutdown(self):
        self.stop_event.set()
        self.tester.safe_output()
        self.esp32.set_status("ERROR")
        self._set_values(state="ERROR", voltage=0, leakage=0.0, test1="ABORTED", test2="ABORTED", hvil_state="OPEN")

    def reset(self):
        self.stop_event.set()
        self.tester.safe_output()
        self.esp32.set_status("IDLE")
        self._set_values(state="IDLE", voltage=0, leakage=0.0, test1="STANDBY", test2="STANDBY", hvil_state="UNKNOWN")