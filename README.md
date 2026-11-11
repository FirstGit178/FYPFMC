# FYPFMC  Hipot System Control Panel

FYPFMC is a prototype control panel project for a hipot (high Voltage) test system. It includes a desktop control panel that runs test sequences against simulated hardware, plus a separate browser based emulator which was the first attempt at this project.

> **Safety:** This project is currently for simulation and demonstration. The real tester and ESP32 drivers are incomplete placeholders. Do not use this software to control real high voltage equipment.

## Running it on another PC

For the desktop simulator, the other PC needs Python 3 with Tkinter available. Git is needed to clone the repository (or download the repository as a ZIP from GitHub instead). No hardware or extra Python packages are needed for the simulation.

On Windows, install Python 3 from [python.org](https://www.python.org/downloads/) and make sure the Tcl/Tk and IDLE option is selected in the installer. Install Git if you plan to clone the repository. Then open PowerShell and run:

```powershell
git clone https://github.com/FirstGit178/FYPFMC.git
cd FYPFMC
python .\Simulator\main.py
```

If `python` is not recognized, try `py` in its place. The desktop app starts in simulation mode by default. To run the optional browser based emulator instead, install Streamlit and launch it:

```powershell
python -m pip install streamlit
python -m streamlit run .\basic_emulator.py
```

On macOS or Linux, install Python 3 and Tkinter for your distribution if Tkinter is not already included, then clone the repository and run `python3 Simulator/main.py` from the cloned folder. Streamlit is only needed for the browser based emulator.

## Interfaces

### Desktop simulator

The Tkinter application is the main interface. It displays the test state, voltage, leakage reading, HVIL interlock state, and the status of each test. In the default simulation mode, no voltage is applied to hardware.

Start it from the repository root:

```powershell
python .\Simulator\main.py
```

The app opens with the **Main Control** and **Emulator Settings** tabs. The interlock starts as `UNKNOWN`; close it before starting a test:

| Action | Button | Keyboard |
| --- | --- | --- |
| Run standard sequence | Run Standard | `S` |
| Run fault demonstration | Demo Fault | `F` |
| Emergency stop | STOP | `E` |
| Reset the panel | Reset | `R` |
| Close the simulated interlock | — | `C` |
| Open the simulated interlock (triggers stop) | — | `O` |

In the **Emulator Settings** tab, adjust the simulated leakage values (in µA) used for the 1500 V and 500 V tests. The default readings are 250 µA and 50 µA; the corresponding test limits are 500 µA and 100 µA. Settings can only be changed when a test is not running.

### Browser based emulator

`basic_emulator.py` is a separate Streamlit demo with its own status display and controls. It does not use the desktop controller or its hardware adapters.

Install Streamlit if needed, then launch it from the repository root:

```powershell
python -m pip install streamlit
python -m streamlit run .\basic_emulator.py
```

Streamlit prints a local URL to open in your browser. Use **Run Standard Sequence**, **Demo Fault Handling**, or **EMERGENCY STOP** to explore the demo UI.

## Requirements

  Python 3
  Tkinter, included with most standard Python installations (required for the desktop simulator)
  Streamlit (required only for the browser based emulator)

No separate hardware or third party packages are needed for the desktop simulator's default simulation mode.

## Project layout

```text
.
├── basic_emulator.py       # Standalone Streamlit UI demo
└── Simulator/
    ├── main.py             # Tkinter desktop application
    ├── controller.py       # Test sequencing, state, and safety stop behavior
    ├── hardware_sim.py     # Simulated tester and ESP32 adapters
    └── hardware_real.py    # Incomplete real hardware adapter placeholders
```

## Hardware integration status

`Simulator/main.py` selects simulated hardware by default (`use_sim = True`). The real hardware adapters in `Simulator/hardware_real.py` are not ready for operation: tester communication is placeholder code, and ESP32 communication raises `NotImplementedError`. Keep the application in simulation mode; switching to real hardware is not a supported or safe operating mode.
