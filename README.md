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