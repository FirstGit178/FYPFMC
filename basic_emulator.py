import tkinter as tk
from tkinter import ttk
import threading
import time

class BasicHipotEmulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hipot System & Interface Box Emulator")
        self.root.geometry("600x480")
        self.root.resizable(False, False)
        
        # ----------------------------------------------------
        # SYSTEM MEMORY BANK (TRACKS DATA STATE CHANGES)
        # ----------------------------------------------------
        self.current_state = "IDLE"  # Options: IDLE, TESTING, PASS, FAIL, ERROR
        self.active_voltage = 0
        self.measured_leakage = 0.0
        self.is_sequence_running = False

        # Build the user interface frames
        self.create_visual_layout()
        
        # Start a continuous loop to force redraws of text and lights
        self.refresh_display_loop()

    def create_visual_layout(self):
        """Builds clear, easy-to-track visual panels on the desktop window."""
        
        # PANEL 1: MAIN SYSTEM STATUS HEADLINE INDICATOR
        self.status_banner = tk.Frame(self.root, bg="#2C3E50", height=80)
        self.status_banner.pack(fill="x", side="top")
        self.status_banner.pack_propagate(False) # Prevent shrinking
        
        self.lbl_headline = tk.Label(
            self.status_banner, text="SYSTEM STATUS: INITIALIZING", 
            font=("Arial", 16, "bold"), fg="#FFFFFF", bg="#2C3E50"
        )
        self.lbl_headline.pack(expand=True)

        # PANEL 2: DIGITAL MULTIMETER METER READOUTS
        self.meter_frame = tk.Frame(self.root, pady=15)
        self.meter_frame.pack(fill="x")
        
        self.lbl_meters = tk.Label(
            self.meter_frame, text="0 V  |  0.00 mA", 
            font=("Consolas", 26, "bold"), fg="#2C3E50"
        )
        self.lbl_meters.pack()

        # PANEL 3: SEQUENTIAL STEPS TRACKING BOX
        self.matrix_box = tk.LabelFrame(
            self.root, text=" Sequential Operations Overview ", 
            font=("Arial", 10, "bold"), padx=20, pady=15
        )
        self.matrix_box.pack(fill="both", expand=True, padx=25, pady=10)
        
        # Row 0: Profile Test Phase 1
        self.lbl_t1_text = tk.Label(self.matrix_box, text="Test Profile 1: High-Voltage Strength (1500V Target)", font=("Arial", 11))
        self.lbl_t1_text.grid(row=0, column=0, sticky="w", pady=10)
        self.lbl_t1_light = tk.Label(self.matrix_box, text="STANDBY", font=("Arial", 10, "bold"), fg="gray", width=12, relief="sunken")
        self.lbl_t1_light.grid(row=0, column=1, padx=25)

        # Row 1: Profile Test Phase 2
        self.lbl_t2_text = tk.Label(self.matrix_box, text="Test Profile 2: Insulation Resistance (500V Target)", font=("Arial", 11))
        self.lbl_t2_text.grid(row=1, column=0, sticky="w", pady=10)
        self.lbl_t2_light = tk.Label(self.matrix_box, text="STANDBY", font=("Arial", 10, "bold"), fg="gray", width=12, relief="sunken")
        self.lbl_t2_light.grid(row=1, column=1, padx=25)

        # PANEL 4: OPERATOR CLICK CONTROLS (TRIGGERS SIMULATION)
        self.interaction_bar = tk.Frame(self.root, pady=20)
        self.interaction_bar.pack(fill="x", side="bottom")

        # Command Button 1: Happy Path
        self.btn_nominal = ttk.Button(self.interaction_bar, text="Run Standard Sequence", command=self.trigger_standard_sequence)
        self.btn_nominal.pack(side="left", padx=15, expand=True)

        # Command Button 2: Fault Handling Path
        self.btn_fault = ttk.Button(self.interaction_bar, text="Demo Fault Handling", command=self.trigger_fault_sequence)
        self.btn_fault.pack(side="left", padx=15, expand=True)

        # Command Button 3: Immediate Emergency Kill Switch
        self.btn_abort = tk.Button(
            self.interaction_bar, text="EMERGENCY SHUTDOWN", 
            bg="#E74C3C", fg="white", font=("Arial", 9, "bold"), command=self.execute_immediate_safety_shutdown
        )
        self.btn_abort.pack(side="left", padx=15, expand=True)

    # ----------------------------------------------------
    # CORE LOGIC OPERATIONS ENGINE
    # ----------------------------------------------------
    def trigger_standard_sequence(self):
        """Starts the successful dual-test sequence in a background worker thread."""
        if not self.is_sequence_running and self.current_state != "ERROR":
            # Running this inside a thread stops the window from 'freezing' during time.sleep pauses
            threading.Thread(target=self._logic_standard_process, daemon=True).start()

    def _logic_standard_process(self):
        self.is_sequence_running = True
        self.current_state = "TESTING"
        self.lbl_t1_light.config(text="RUNNING", fg="orange")
        self.lbl_t2_light.config(text="STANDBY", fg="gray")
        
        print("[PROCESS] Initiating Test 1: Ramping voltage to 1500V...")
        for steps in range(300, 1501, 300):
            if self.current_state == "ERROR": return # Stop processing instantly if kill switch pressed
            self.active_voltage = steps
            self.measured_leakage = round(0.4 + (steps / 1500), 2)
            time.sleep(0.7) # Deliberate visual delay so you can observe values changing

        print("[PROCESS] Test 1 Completed successfully. Checking condition to advance...")
        self.lbl_t1_light.config(text="PASSED", fg="green")
        time.sleep(1.2) # Holding delay between stages
        
        # --- SEQUENTIAL ASSESSMENT LINK ---
        print("[PROCESS] Condition Met. Launching Test 2 at 500V...")
        self.lbl_t2_light.config(text="RUNNING", fg="orange")
        self.active_voltage = 500
        self.measured_leakage = 0.28
        time.sleep(1.5)
        
        if self.current_state != "ERROR":
            print("[PROCESS] Entire testing routine passed.")
            self.lbl_t2_light.config(text="PASSED", fg="green")
            self.current_state = "PASS"
        
        self.is_sequence_running = False

    def trigger_fault_sequence(self):
        """Starts a failing sequence to demonstrate how the software responds to a defect."""
        if not self.is_sequence_running and self.current_state != "ERROR":
            threading.Thread(target=self._logic_fault_process, daemon=True).start()

    def _logic_fault_process(self):
        self.is_running = True
        self.current_state = "TESTING"
        self.lbl_t1_light.config(text="RUNNING", fg="orange")
        self.lbl_t2_light.config(text="STANDBY", fg="gray")
        
        print("[PROCESS] Initiating Test 1...")
        time.sleep(0.8)
        self.active_voltage = 600
        self.measured_leakage = 0.85
        time.sleep(0.8)
        
        # Simulate high current leakage breakdown breach event
        print("[ALERT] Excessive breakdown current observed on Test 1!")
        self.active_voltage = 1150
        self.measured_leakage = 18.95  # Simulated current failure spike
        time.sleep(0.5)
        
        # Abort system and skip profile 2 safely
        self.current_state = "FAIL"
        self.lbl_t1_light.config(text="FAILED", fg="red")
        self.lbl_t2_light.config(text="BYPASSED", fg="#8B0000")
        self.is_sequence_running = False

    def execute_immediate_safety_shutdown(self):
        """Forces the machine loop to safe out all voltages and currents instantly."""
        print("[SAFETY] Emergency intervention command received. Tripping loop links.")
        self.current_state = "ERROR"
        self.active_voltage = 0
        self.measured_leakage = 0.0
        self.lbl_t1_light.config(text="ABORTED", fg="red")
        self.lbl_t2_light.config(text="ABORTED", fg="red")
        self.is_sequence_running = False

    # ----------------------------------------------------
    # UI REPAINT CONTROLLER (RUNS ON A TICK TIMER)
    # ----------------------------------------------------
    def refresh_display_loop(self):
        """Checks the backend memory variables and updates what you see in real-time."""
        
        # Push variables to the center metric layout label
        self.lbl_meters.config(text=f"{self.active_voltage} V  |  {self.measured_leakage:.2f} mA")
        
        # Change colors and text header boxes depending on system state values
        if self.current_state == "IDLE":
            self.lbl_headline.config(text="SYSTEM STATUS: READY / IDLE", fg="#2ECC71", bg="#2C3E50")
            self.status_banner.config(bg="#2C3E50")
        elif self.current_state == "TESTING":
            self.lbl_headline.config(text="SYSTEM STATUS: DANGER - HIGH VOLTAGE ACTIVE", fg="#111111", bg="#F1C40F")
            self.status_banner.config(bg="#F1C40F")
        elif self.current_state == "PASS":
            self.lbl_headline.config(text="SYSTEM STATUS: PASS (PROFILE ENTIRELY CLEAR)", fg="#FFFFFF", bg="#27AE60")
            self.status_banner.config(bg="#27AE60")
        elif self.current_state == "FAIL":
            self.lbl_headline.config(text="SYSTEM STATUS: DEVICE REJECTED (INSULATION FAULT)", fg="#FFFFFF", bg="#C0392B")
            self.status_banner.config(bg="#C0392B")
        elif self.current_state == "ERROR":
            self.lbl_headline.config(text="SYSTEM STATUS: EMERGENCY HARDWARE INTERRUPT ACTIVE", fg="#F1C40F", bg="#000000")
            self.status_banner.config(bg="#000000")

        # Run this check loop again in 50 milliseconds
        self.root.after(50, self.refresh_display_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = BasicHipotEmulatorGUI(root)
    root.mainloop()
