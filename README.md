# Green Grid Sim
Green Grid Sim is a Python-based discrete-event simulation tool designed to model and analyze residential renewable energy microgrids. It accurately simulates the interaction between Solar PV arrays, Battery Energy Storage Systems (BESS), household loads, and the utility grid.

Powered by SimPy, this project allows engineers and researchers to evaluate the performance, cost-efficiency, and reliability of different hardware configurations and Energy Management Strategies (EMS) under varying environmental conditions and seasonal patterns.

### Key Features
Physics-Based Modeling: Accurate simulation of battery SoC, efficiency losses, and solar generation curves.

### Stochastic Environment: Simulates realistic weather patterns (cloud coverage) and household consumption spikes.

### Configurable Scenarios: Fully customizable parameters for hardware size, location, and costs via JSON.

### Smart Control Strategies: Test and compare logic like Load Priority vs. Market Export Priority.

## 🚀 Setup & Installation
Prerequisites
Python 3.8 or higher

pip (Python package manager)

Installation Steps
Clone the repository (if you haven't already):

Bash

git clone https://github.com/SG1_Team6/GreenGridSim.git
cd GreenGridSim
Create a Virtual Environment (Recommended):

Bash

### Windows
python -m venv venv
venv\Scripts\activate

### Mac/Linux
'''
python3 -m venv venv
source venv/bin/activate
Install Dependencies:
'''

'''
Bash

pip install -r requirements.txt
⚙️ Configuration
The simulation is fully controlled via the config/simulation_config.json file. You can modify the following parameters to test different scenarios:

## Key Parameters:
simulation:

duration_days: Length of the simulation (e.g., 30).

season: affects cloud coverage probabilities ("Summer", "Winter", "Spring", "Fall").

battery: Define capacity (kWh), initial state, and round-trip efficiency.

solar: Set panel peak power (panel_peak_kw) and inverter failure rates.

load: Define the household base consumption and peak hours.

strategy: Select the Energy Management System (EMS) logic.

### Available Strategies:
Change the "name" field under "strategy" to one of the following:

LOAD_PRIORITY (Default): Prioritizes powering the house. Excess energy charges the battery, then exports to the grid.

CHARGE_PRIORITY: Prioritizes filling the battery first. Useful for backup security.

PRODUCE_PRIORITY: Prioritizes exporting energy to the grid for profit.

## ▶️ Usage
To run the simulation, execute the main.py script from the project root:
'''
Bash

python main.py
'''

## 📂 Project Structure

The project is organized into modular components to separate configuration, physical modeling, and control logic.

```text
GreenGridSim/
├── config/
│   └── simulation_config.json   # Simulation parameters (Battery size, solar capacity, strategy)
├── docs/                        # Project documentation, flowcharts, and reports
├── outputs/                     # Generated CSV logs and simulation results
├── src/                         # Source code package
│   ├── __init__.py              # Exposes main classes for cleaner imports
│   ├── components.py            # Physical models: Battery, SolarPanel, Inverter
│   ├── engine.py                # SimPy simulation loop and time management
│   ├── environment.py           # External factors: Weather, HomeLoad, UtilityGrid
│   └── strategy.py              # Energy Management Systems (Logic for LOAD_PRIORITY, etc.)
├── .devcontainer/               # Docker container configuration for development
├── .vscode/                     # VS Code settings
├── main.py                      # Entry point: Loads config and runs the simulation
├── requirements.txt             # Python dependencies (simpy, pandas, etc.)
└── README.md                    # Project documentation