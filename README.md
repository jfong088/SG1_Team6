# Green Grid Sim

**Green Grid Sim** is a Python-based discrete-event simulation tool designed to model and analyze residential renewable energy microgrids. It accurately simulates the interaction between **Solar PV arrays**, **Battery Energy Storage Systems (BESS)**, household loads, and the utility grid.

Powered by `SimPy`, this project allows engineers and researchers to evaluate the performance, cost-efficiency, and reliability of different hardware configurations and Energy Management Strategies (EMS) under varying environmental conditions and seasonal patterns.

### Key Features
* **Physics-Based Modeling:** Accurate simulation of battery SoC, efficiency losses, and solar generation curves.
* **Stochastic Environment:** Simulates realistic weather patterns (cloud coverage) and household consumption spikes.
* **Configurable Scenarios:** Fully customizable parameters for hardware size, location, and costs via JSON.
* **Smart Control Strategies:** Test and compare logic like *Load Priority* vs. *Market Export Priority*.

---

## 📂 Project Structure

The project is organized into modular components to separate configuration, physical modeling, and control logic.

```text
Simulator/
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
```

---

## 🚀 Setup & Installation
**Prerequisites**
- Python 3.8 or higher
- pip (Python package manager)

**Installation Steps**
1. Clone the repository:

```Bash

git clone [https://github.com/SG1_Team6/GreenGridSim.git](https://github.com/SG1_Team6/GreenGridSim.git)
cd GreenGridSim
```

2. **Create a Virtual Environment** (Recommended):

```Bash

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```
3. **Install Dependencies**:

```Bash

pip install -r requirements.txt
```

---

## ⚙️ Configuration
The simulation is fully controlled via the config/simulation_config.json file. You can modify any of the following parameters to test different scenarios.

1. **Simulation Settings** `(simulation)`
General parameters defining the scope and environment of the run.

    - `duration_days` (int): Total number of days to simulate (e.g., 30).

    - `time_step_minutes` (int): The granularity of the simulation step in minutes (e.g., 60 for hourly steps).

    - `season` (string): Defines weather patterns and cloud coverage probabilities.

    - Options: `"Summer"`, `"Winter"`, `"Spring"`, `"Fall"`.

    - `start_date` (string): The start date for the data logs in YYYY-MM-DD format (e.g., "2026-06-01").

2. **Battery Storage** `(battery)`
Physical specifications of the home battery system.

    - `capacity` (float): Total energy capacity in kWh (e.g., 13.5).

    - `initial_state` (float): Starting State of Charge (SoC) as a decimal percentage (e.g., 0.0 for empty, 1.0 for full).

    - `efficiency` (float): Round-trip efficiency of the battery (e.g., 0.90 implies 10% energy loss).

    - `discharge_depth` (float): Minimum allowable SoC limit to protect battery health (e.g., 0.05 means the battery stops discharging at 5%).

3. **Solar Generation** `(solar)`
Parameters for the PV array and inverter hardware.

    - `panel_peak_kw` (float): Maximum DC power output of the solar panels in kW (e.g., 5.0).

    - `inverter_max_kw` (float): Maximum AC power output of the inverter (clipping limit) in kW (e.g., 4.0).

    - `inverter_failure_rate` (float): Probability of inverter failure per simulation step (e.g., 0.005 for 0.5%).

    - `failure_duration_min_hours` (int): Minimum downtime in hours if a failure occurs (e.g., 4).

    - `failure_duration_max_hours` (int): Maximum downtime in hours if a failure occurs (e.g., 72).

4. **Household Load** `(load)`
Consumption profile of the house.

    - `base_load_kw` (float): Constant background power demand (fridge, router, standby) in kW (e.g., 0.5).

    - `peak_load_kw` (float): Maximum random consumption spike added during peak hours in kW (e.g., 3.0).

    - `peak_start_hour` (int): Start hour (0-23) of the peak demand window (e.g., 18 for 6 PM).

    - `peak_end_hour` (int): End hour (0-23) of the peak demand window (e.g., 21 for 9 PM).

5. **Utility Grid** `(grid)`
Economic and physical connection to the grid.

    - `export_limit_kw` (float): Maximum power allowed to be sent back to the grid in kW (e.g., 20.0).

    - `cost_import_cents` (float): Cost to buy electricity from the grid in cents/kWh (e.g., 0.75).

    - `price_export_cents` (float): Earnings for selling electricity to the grid in cents/kWh (e.g., 0.90).

6. **Strategy** `(strategy)`
The "Brain" of the system.

    - `name` (string): The Energy Management Strategy (EMS) to use.

        - `"LOAD_PRIORITY"`: Powers house first, then charges battery, then exports.

        - `"CHARGE_PRIORITY"`: Charges battery first, then powers house, then exports.

        - `"PRODUCE_PRIORITY"`: Exports to grid first, then charges battery, then powers house.

---

## ▶️ Usage
To run the simulation, execute the main.py script from the project root:

```Bash

python main.py
```

**What happens next?**
The system loads the configuration from config/simulation_config.json.

The engine runs the simulation step-by-step using simpy.

A summary is printed to the console.

Detailed logs are saved to the outputs/ director.

---

## 📊 Outputs
Results are generated in CSV format in the outputs/ folder.
Filenames include a timestamp to prevent overwriting previous runs:

```text
outputs/simulation_results_YYYY-MM-DD_HH-MM-SS.csv
```

Data Columns:
- `time_min`: Simulation time in minutes.

- `day`: Current day number of the simulation.

- `hour`: Current hour of the day (0-23).

- `solar_gen_kw`: Energy generated by panels.

- `load_kw`: House energy consumption.

- `battery_soc_kwh`: Current energy stored in the battery.

- `grid_import_kw`: Power purchased from the grid.

- `grid_export_kw`: Power sold to the grid.

- `cost_cents`: Net financial balance for that step (Positive = Cost, Negative = Profit).

- `cloud_cover`: Cloud coverage percentage (0.0 = Clear, 1.0 = Overcast).
