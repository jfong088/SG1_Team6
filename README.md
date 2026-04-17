# Green Grid Sim

**Green Grid Sim** is a Python-based discrete-event simulation tool designed to model and analyze residential renewable energy microgrids. It accurately simulates the interaction between **Solar PV arrays**, **Battery Energy Storage Systems (BESS)**, household loads, and the utility grid.

Built with `SimPy`, this project allows for the evaluation of performance, cost-efficiency, and reliability across various neighborhood configurations and Energy Management Strategies (EMS).

---

## 📂 Project Structure

The project is organized into modular components to separate configuration, physical modeling, and control logic:

```text
GreenGridSim
├── .devcontainer/              # Development container configuration (Docker)
├── config/
│   └── simulation_config.yaml  # Simulation parameters (Battery, Solar, Strategy)
├── docs/                       # Web dashboard (GitHub Pages) and reports
├── outputs/                    # Generated CSV results
├── simulator
|   ├─ src/                     # Source code package
│   |  ├── components.py        # Hardware models (Battery, Inverter, Panels)
│   |  ├── engine.py            # SimPy orchestration logic
│   |  ├── environment.py       # Weather and Load stochastic models
│   |  ├── neighborhood.py      # Neighborhood and House entity logic
│   |  ├── preparation.py       # Data processing for the dashboard
│   |  └── strategy.py          # Energy Management Strategies (EMS)
|   └── main.py                 # Entry point to run the simulation
└── README.md
```

---

## 🛠️ Setup & Environment

This project is designed to run within a **Dev Container** to ensure a consistent development environment across any machine. This setup automatically handles all system dependencies and Python libraries using Docker.

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* [Visual Studio Code](https://code.visualstudio.com/)
* [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code

### Getting Started
1.  Open the project folder in VS Code.
2.  A notification will appear in the bottom-right corner; click **"Reopen in Container"**.
3.  VS Code will build the Docker image and install all necessary requirements (SimPy, Pandas, PyYAML, etc.).
4.  Once the build is complete, the terminal will be ready to execute the simulation.

---

## ⚙️ Configuration
The simulation is fully controlled via the `config/simulation_config.yaml` file. Because the system is entirely data-driven, you can modify any of the following parameters to test different scenarios and scale from a single house to a complete neighborhood.

### I. Global Settings
These parameters apply to the entire simulation environment.

1. **Simulation Settings** `(simulation)`
General parameters defining the scope and environment of the run.
    - `duration_days` (int): Total number of days to simulate (e.g., 30).
    - `time_step_minutes` (int): The granularity of the simulation step in minutes (e.g., 60 for hourly steps).
    - `season` (string): Defines weather patterns and cloud coverage probabilities. Options: `"Summer"`, `"Winter"`, `"Spring"`, `"Fall"`.
    - `start_date` (string): The start date for the data logs in YYYY-MM-DD format (e.g., "2026-12-24").

2. **Utility Grid** `(grid)`
Economic and physical connection to the grid.
    - `export_limit_kw` (float): Maximum power allowed to be sent back to the grid for the entire neighborhood in kW (e.g., 500.0).
    - `cost_import_cents` (float): Cost to buy electricity from the grid in cents/kWh (e.g., 0.75).
    - `price_export_cents` (float): Earnings for selling electricity to the grid in cents/kWh (e.g., 0.90).

3. **Strategy** `(strategy)`
The "Brain" of the system.
    - `name` (string): The Energy Management Strategy (EMS) to use for all connected houses.
        - `"LOAD_PRIORITY"`: Powers house first, then charges battery, then exports.
        - `"CHARGE_PRIORITY"`: Charges battery first, then powers house, then exports.
        - `"PRODUCE_PRIORITY"`: Exports to grid first, then charges battery, then powers house.

### II. House Profiles `(house_profiles)`
You can define multiple archetypes of homes (e.g., `Studio`, `Small_Family`, `Large_Family`). Each profile contains its own specific load behavior and hardware limits:

4. **Household Load** `(load)`
Consumption profile of the specific house archetype.
    - `base_load_kw` (float): Constant background power demand (fridge, router, standby) in kW (e.g., 0.4).
    - `peak_load_kw` (float): Maximum random consumption spike added during peak hours in kW (e.g., 4.5).
    - `peak_start_hour` (int): Start hour (0-23) of the peak demand window (e.g., 18 for 6 PM).
    - `peak_end_hour` (int): End hour (0-23) of the peak demand window (e.g., 21 for 9 PM).

5. **Battery Storage** `(hardware.battery)`
Physical specifications of the home battery system.
    - `capacity` (float): Total energy capacity in kWh (e.g., 13.5).
    - `initial_state` (float): Starting State of Charge (SoC) as a decimal percentage (e.g., 0.0 for empty, 1.0 for full).
    - `efficiency` (float): Round-trip efficiency of the battery (e.g., 0.90 implies 10% energy loss).
    - `discharge_depth` (float): Minimum allowable SoC limit to protect battery health (e.g., 0.05 means the battery stops discharging at 5%).

6. **Solar Generation** `(hardware.solar)`
Parameters for the PV array and inverter hardware.
    - `panel_peak_kw` (float): Maximum DC power output of the solar panels in kW (e.g., 5.0).
    - `inverter_max_kw` (float): Maximum AC power output of the inverter (clipping limit) in kW (e.g., 4.0).
    - `inverter_failure_rate` (float): Probability of inverter failure per simulation step (e.g., 0.005 for 0.5%).
    - `failure_duration_min_hours` (int): Minimum downtime in hours if a failure occurs (e.g., 4).
    - `failure_duration_max_hours` (int): Maximum downtime in hours if a failure occurs (e.g., 72).

### III. Neighborhood Generation
These settings control how the individual profiles are scaled and deployed into the simulation.

7. **Wealth Multipliers** `(wealth_multipliers)`
Applies socio-economic scaling factors to the base house profiles. This multiplier affects both the energy consumption and the size of the hardware (batteries and panels).
    - `Low_Income` (float): Scales down the base profile (e.g., 0.7).
    - `Middle_Income` (float): Leaves the base profile as defined (e.g., 1.0).
    - `Luxury` (float): Scales up the base profile for high-end consumers (e.g., 1.5).

8. **Neighborhood Composition** `(neighborhood_composition)`
A dynamic list that populates the simulation with actual houses based on your profiles and multipliers. You can add as many groups as needed.
    - `profile` (string): The house archetype to use (e.g., `"Small_Family"`).
    - `wealth` (string): The socio-economic multiplier to apply (e.g., `"Middle_Income"`).
    - `count` (int): The number of identical houses to generate with these exact parameters (e.g., 15).

---

## ▶️ Usage

To execute the simulation and update the results dashboard, run the following command in the terminal:

```bash
python main.py
```

**What happens next?**
- The system loads settings from the YAML config.
- The engine runs the discrete-event simulation via SimPy.
- A summary is printed to the console, and a CSV log is saved in outputs/.
- The data is automatically processed and exported to docs/dashboard_data.json for the web dashboard.

---

## 📈 Interactive Dashboard

The project features a high-fidelity web dashboard located in the `docs/` folder. It provides a visual narrative to help stakeholders understand the benefits of the microgrid through real-time data analysis.

**Key Features:**
* **The Duck Curve:** Visualizes the "belly" of net load during peak solar hours and the evening ramp, highlighting grid stress points.
* **Energy Independence:** Compares solar self-consumption vs. grid imports across different wealth levels and house profiles.
* **Economic Impact:** Displays estimated financial savings derived from solar adoption and smart energy management.
* **Battery Utilization:** Tracks how storage systems mitigate grid stress by storing energy during surplus and discharging during peaks.
* **Household Analytics:** A detailed bubble chart mapping individual house performance, comparing cost savings against energy exported to the grid.

To view the dashboard, you can access the hosted webpage [Green Grid Simulation Results Dashboard](https://jfong088.github.io/SG1_Team6/), or serve the `docs/` folder using a local web server (e.g., `python -m http.server` inside the `docs/` directory) and open `index.html` in your browser at `localhost:8000`.

---

## 📊 Outputs & Visualization
Results are generated in CSV format in the outputs/ folder. For a visual and interactive analysis, open the docs/index.html file using a local web server to view the results on the Results Dashboard by following the instructions above.

---