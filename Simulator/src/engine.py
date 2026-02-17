import simpy
import pandas as pd
from src.components import Battery, SolarPanel, Inverter
from src.environment import Weather, HomeLoad, UtilityGrid
from src.strategy import EnergyManager

class SimulationEngine:
    """
    Orchestrates the simulation using SimPy.
    Connects all physical components, environment, and strategy logic.
    """

    def __init__(self, config):
        """
        Initializes the simulation engine.
        
        Args:
            config (dict): The full simulation_config.json loaded as a dict.
        """
        self.config = config
        
        # 1. Setup SimPy Environment
        self.env = simpy.Environment()
        
        # 2. Extract Simulation Parameters
        sim_config = config['simulation']
        self.duration_hours = sim_config['duration_days'] * 24
        self.step_minutes = sim_config.get('time_step_minutes', 60)
        
        # 3. Initialize Components (The Hardware)
        self.battery = Battery(config['battery'])
        self.solar_panel = SolarPanel(config['solar'])
        self.inverter = Inverter(config['solar'])
        
        # 4. Initialize Environment (The World)
        self.weather = Weather(sim_config)
        self.home_load = HomeLoad(config['load'])
        self.grid = UtilityGrid(config['grid'])
        
        # 5. Initialize Brain (Strategy)
        self.energy_manager = EnergyManager(config['strategy'])
        
        # 6. Data Logging
        self.results = []

    def run(self):
        """
        Starts the simulation loop.
        """
        # Tell SimPy to start our process
        self.env.process(self._simulation_loop())
        
        # Run until the configured duration
        self.env.run(until=self.duration_hours * 60) # Run in minutes
        
        # Return results as a DataFrame for easy analysis
        return pd.DataFrame(self.results)

    def _simulation_loop(self):
        """
        The main heartbeat of the simulation.
        Runs every 'step_minutes' (e.g., every hour).
        """
        while True:
            # 1. Determine Current Time 
            current_time_min = self.env.now
            current_hour = (current_time_min / 60) % 24
            day_number = int(current_time_min / (60 * 24))
            
            #  2. Get Environmental Data 
            # Cloud coverage is determined daily or hourly? Let's assume daily for simplicity,
            # or we could make it hourly. For now, let's regenerate it every step for variability.
            cloud_cover = self.weather.get_cloud_coverage()
            
            #  3. Calculate Physics 
            # a) Solar Generation (DC)
            dc_solar_kw = self.solar_panel.get_generation(current_hour, cloud_cover)
            
            # b) Inverter Conversion (DC -> AC) & Clipping
            ac_solar_kw = self.inverter.clip_power(dc_solar_kw)
            
            # c) House Consumption
            load_kw = self.home_load.get_current_load(current_hour)
            
            #  4. Strategy Decision (The Brain) 
            # The manager decides where energy goes.
            # We pass the battery object so it can charge/discharge it internally.
            flow_decision = self.energy_manager.decide_energy_flow(
                solar_gen_kw = ac_solar_kw,
                load_demand_kw = load_kw,
                battery = self.battery,
                grid_limit_kw = self.grid.export_limit_kw
            )
            
            #  5. Calculate Costs 
            grid_import = flow_decision['grid_import']
            grid_export = flow_decision['solar_to_grid']
            step_cost = self.grid.calculate_cost(grid_import, grid_export)
            
            #  6. Log Data 
            self.results.append({
                'time_min': current_time_min,
                'day': day_number,
                'hour': current_hour,
                'solar_gen_kw': ac_solar_kw,
                'load_kw': load_kw,
                'battery_soc_kwh': self.battery.current_energy_kwh,
                'grid_import_kw': grid_import,
                'grid_export_kw': grid_export,
                'cost_cents': step_cost,
                'cloud_cover': cloud_cover
            })
            
            #  7. Wait for next step 
            yield self.env.timeout(self.step_minutes)