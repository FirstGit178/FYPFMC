# This file imports the other modules and connects them together.
import tkinter as tk
from tkinter import ttk

# IMPORT other files
from controller import TestController
from hardware_sim import SimulatedTester, SimulatedESP32
from hardware_real import ActualHipotTester, ActualESP32

class TabbedHipotGUI:
    def __init__(self, root, tester, esp32):
        self.tester = tester
        self.root = root
        self.root.title("Hipot System Control Panel")
        self.root.geometry("650x600")

        # Connect the Controller to the Hardware
        self.controller = TestController(on_update=self.schedule_display_update, tester=tester, esp32=esp32)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.main_tab = ttk.Frame(self.notebook)
        self.emu_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main Control")
        self.notebook.add(self.emu_tab, text="Emulator Settings")

        self.setup_main_tab() 
        self.setup_emu_tab()

        self.root.bind_all("<KeyPress>", self.handle_keypress)
        self.refresh_display_loop()

    def setup_main_tab(self):
        self.status_banner = tk.Frame(self.main_tab, bg="#2C3E50", height=80)
        self.status_banner.pack(fill="x", side="top")
        self.status_banner.pack_propagate(False)
        self.lbl_headline = tk.Label(self.status_banner, text="READY", font=("Arial", 16, "bold"), fg="white", bg="#2C3E50")
        self.lbl_headline.pack(expand=True)
        self.lbl_meters = tk.Label(self.main_tab, text="0 V | 0.00 mA", font=("Consolas", 26, "bold"))
        self.lbl_meters.pack(pady=20)
        self.lbl_hvil = tk.Label(self.main_tab, text="HVIL: UNKNOWN", font=("Arial", 12))
        self.lbl_hvil.pack()
        self.matrix_box = tk.LabelFrame(self.main_tab, text=" Operations ")
        self.matrix_box.pack(fill="both", expand=True, padx=20, pady=10)
        self.lbl_t1_light = tk.Label(self.matrix_box, text="STANDBY", width=12, relief="sunken")
        self.lbl_t1_light.pack(pady=10)
        self.lbl_t2_light = tk.Label(self.matrix_box, text="STANDBY", width=12, relief="sunken")
        self.lbl_t2_light.pack(pady=10)
        self.btn_frame = tk.Frame(self.main_tab)
        self.btn_frame.pack(fill="x", side="bottom", pady=20)
        ttk.Button(self.btn_frame, text="Run Standard", command=lambda: self.controller.start(False)).pack(side="left", padx=5, expand=True)
        # To be removed, as settings tab now allows to simulate fault.
        ttk.Button(self.btn_frame, text="Demo Fault", command=lambda: self.controller.start(True)).pack(side="left", padx=5, expand=True)
        tk.Button(self.btn_frame, text="STOP", bg="red", fg="white", command=self.controller.emergency_shutdown).pack(side="left", padx=5, expand=True)
        ttk.Button(self.btn_frame, text="Reset", command=self.controller.reset).pack(side="left", padx=5, expand=True)

    def setup_emu_tab(self):
        ttk.Label(
            self.emu_tab,
            text="Simulation Settings — leakage readings in µA",
            font=("Arial", 14, "bold")
        ).pack(pady=20)

        # Do not show editable simulation settings for a real tester.
        if not isinstance(self.tester, SimulatedTester):
            ttk.Label(self.emu_tab, text="Settings are available only in simulation mode.").pack()
            return

        self.leakage_1500_var = tk.StringVar(value=str(self.tester.leakage_1500v_ua))
        self.leakage_500_var = tk.StringVar(value=str(self.tester.leakage_500v_ua))

        ttk.Label(self.emu_tab, text="Leakage at 1500 V (µA):").pack()
        ttk.Entry(self.emu_tab, textvariable=self.leakage_1500_var).pack()

        ttk.Label(self.emu_tab, text="Leakage at 500 V (µA):").pack()
        ttk.Entry(self.emu_tab, textvariable=self.leakage_500_var).pack()

        ttk.Button(
            self.emu_tab,
            text="Apply Simulation Settings",
            command=self.apply_sim_settings
        ).pack(pady=10)

        self.emu_status = ttk.Label(self.emu_tab, text="")
        self.emu_status.pack()


    def apply_sim_settings(self):
    # Avoid changing simulated readings while a test is running.
        if self.controller.snapshot()["state"] == "TESTING":
            self.emu_status.config(text="Stop the test before changing settings.")
            return

        try:
            leakage_1500 = float(self.leakage_1500_var.get())
            leakage_500 = float(self.leakage_500_var.get())

            if leakage_1500 < 0 or leakage_500 < 0:
                raise ValueError

            self.tester.leakage_1500v_ua = leakage_1500
            self.tester.leakage_500v_ua = leakage_500
            self.emu_status.config(text="Simulation settings applied.")

        except ValueError:
                self.emu_status.config(text="Enter valid non-negative numbers.")
        
    def schedule_display_update(self):
        try: self.root.after(0, self.update_display)
        except tk.TclError: pass

    def update_display(self):
        data = self.controller.snapshot()
        self.lbl_meters.config(text=f'{data["voltage"]} V | {data["leakage"]:.2f} mA')
        self.lbl_t1_light.config(text=data["test1"], fg=self._test_color(data["test1"]))
        self.lbl_t2_light.config(text=data["test2"], fg=self._test_color(data["test2"]))
        self.lbl_hvil.config(text=f"HVIL: {data['hvil_state']}")
        self.lbl_headline.config(text=f"STATUS: {data['state']}")

    def _test_color(self, status):
        return {"STANDBY": "gray", "RUNNING": "orange", "PASSED": "green", "FAILED": "red"}.get(status, "gray")

    def refresh_display_loop(self):
        self.update_display()
        self.root.after(100, self.refresh_display_loop)

    def handle_keypress(self, event):
        key = event.keysym.lower()
        if key == "s": self.controller.start(False)
        elif key == "f": self.controller.start(True)
        elif key == "e": self.controller.emergency_shutdown()
        elif key == "r": self.controller.reset()
        elif key == "c": self.controller.set_hvil_state("CLOSED")
        elif key == "o": self.controller.set_hvil_state("OPEN")

if __name__ == "__main__":
    root = tk.Tk()

    # ============================================================
    # CONFIGURATION SWITCH
    # ============================================================
    # To use simulation:
    use_sim = True 

    if use_sim:
        selected_tester = SimulatedTester()
        selected_esp32 = SimulatedESP32()
    else:
        selected_tester = ActualHipotTester()
        selected_esp32 = ActualESP32()
    # ============================================================

    app = TabbedHipotGUI(root, selected_tester, selected_esp32)
    root.mainloop()