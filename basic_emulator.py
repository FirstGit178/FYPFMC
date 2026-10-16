import streamlit as strt
import time

# --- INITIALIZE WEB SESSION MEMORY STORES ---
if "state" not in strt.session_state:
    strt.session_state.state = "IDLE"
if "voltage" not in strt.session_state:
    strt.session_state.voltage = 0
if "current" not in strt.session_state:
    strt.session_state.current = 0.0
if "t1_status" not in strt.session_state:
    strt.session_state.t1_status = "STANDBY"
if "t2_status" not in strt.session_state:
    strt.session_state.t2_status = "STANDBY"

# --- PAGE LAYOUT CONFIG ---
strt.set_page_config(page_title="Hipot System Web Control Panel", layout="centered")
strt.title("🔌 Hipot System & Interface Box Emulator")

# --- PANEL 1: MAIN SYSTEM STATUS HEADLINE INDICATOR ---
state_colors = {
    "IDLE": ("🟢 SYSTEM READY / IDLE", "#D4EFDF"),
    "TESTING": ("⚡ DANGER: HIGH VOLTAGE ACTIVE", "#FCF3CF"),
    "PASS": ("✅ CYCLE COMPLETION: ALL PASSED", "#D5F5E3"),
    "FAIL": ("❌ INSULATION BREAKDOWN REJECTED", "#FADBD8"),
    "ERROR": ("🚨 EMERGENCY HARDWARE ABORT ACTIVE", "#E6B0AA")
}
headline_text, bg_color = state_colors[strt.session_state.state]
strt.markdown(f"<div style='padding:20px; border-radius:10px; background-color:{bg_color}; text-align:center;'><h3>{headline_text}</h3></div>", unsafe_allow_html=True)

# --- PANEL 2: DIGITAL MULTIMETER METER READOUTS ---
strt.markdown(f"<h1 style='text-align: center; font-family: monospace;'>{strt.session_state.voltage} V  |  {strt.session_state.current:.2f} mA</h1>", unsafe_allow_html=True)

# --- PANEL 3: SEQUENTIAL STEPS TRACKING BOX ---
strt.subheader("Sequential Operations Matrix")
col1, col2 = strt.columns([3, 1])
with col1:
    strt.text("Test Profile 1: High-Voltage Strength (1500V Target)")
    strt.text("Test Profile 2: Insulation Resistance (500V Target)")
with col2:
    strt.markdown(f"**{strt.session_state.t1_status}**")
    strt.markdown(f"**{strt.session_state.t2_status}**")

# --- EXECUTION ENGINE FUCTIONS ---
def run_standard_sequence():
    strt.session_state.state = "TESTING"
    strt.session_state.t1_status = "RUNNING"
    strt.session_state.t2_status = "STANDBY"
    
    # Test 1 ramp updates
    progress_placeholder = strt.empty()
    for v in range(300, 1501, 300):
        strt.session_state.voltage = v
        strt.session_state.current = round(0.4 + (v / 1500), 2)
        progress_placeholder.markdown(f"<h1 style='text-align: center; font-family: monospace;'>{strt.session_state.voltage} V  |  {strt.session_state.current:.2f} mA</h1>", unsafe_allow_html=True)
        time.sleep(0.4)
        
    strt.session_state.t1_status = "PASSED"
    strt.session_state.t2_status = "RUNNING"
    time.sleep(0.8)
    
    # Test 2 run update
    strt.session_state.voltage = 500
    strt.session_state.current = 0.28
    time.sleep(0.8)
    
    strt.session_state.t2_status = "PASSED"
    strt.session_state.state = "PASS"
    strt.rerun()

def run_fault_sequence():
    strt.session_state.state = "TESTING"
    strt.session_state.t1_status = "RUNNING"
    strt.session_state.t2_status = "STANDBY"
    
    time.sleep(0.6)
    strt.session_state.voltage = 750
    strt.session_state.current = 0.95
    time.sleep(0.6)
    
    # Spike breakdown trigger
    strt.session_state.voltage = 1200
    strt.session_state.current = 19.45
    strt.session_state.t1_status = "FAILED"
    strt.session_state.t2_status = "BYPASSED"
    strt.session_state.state = "FAIL"
    strt.rerun()

def run_emergency_stop():
    strt.session_state.state = "ERROR"
    strt.session_state.voltage = 0
    strt.session_state.current = 0.0
    strt.session_state.t1_status = "ABORTED"
    strt.session_state.t2_status = "ABORTED"
    strt.rerun()

# --- PANEL 4: OPERATOR CLICK CONTROLS ---
strt.write("---")
ctrl_col1, ctrl_col2, ctrl_col3 = strt.columns(3)
with ctrl_col1:
    if strt.button("Run Standard Sequence", use_container_width=True):
        run_standard_sequence()
with ctrl_col2:
    if strt.button("Demo Fault Handling", use_container_width=True):
        run_fault_sequence()
with ctrl_col3:
    if strt.button("EMERGENCY STOP", type="primary", use_container_width=True):
        run_emergency_stop()
