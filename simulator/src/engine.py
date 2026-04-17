import simpy
import pandas as pd
from src.neighborhood import Neighborhood
from src.environment import Weather, UtilityGrid
from src.strategy import EnergyManager

class SimulationEngine:
    """
    Orchestrates the simulation using SimPy.
    Connects the global environment with the individual house processes.
    """

    def __init__(self, config):
        self.config = config
        self.env = simpy.Environment()
        
        sim_config = config['simulation']
        self.duration_hours = sim_config['duration_days'] * 24
        self.step_minutes = sim_config.get('time_step_minutes', 60)
        
        # 1. Initialize Global Entities
        self.weather = Weather(sim_config)
        self.grid = UtilityGrid(config['grid'])
        self.energy_manager = EnergyManager(config['strategy'])
        
        # 2. Initialize the Neighborhood
        self.neighborhood = Neighborhood(config['houses'])
        
        # 3. Shared state & Data Logging
        # This allows all houses to see the exact same weather at any given minute
        self.weather_state = {'cloud_cover': 0.0}
        self.results = []

    def _global_clock(self):
        """
        SimPy generator process. Acts as the global environment updater.
        Updates the weather just before the houses react to it.
        """
        while True:
            self.weather_state['cloud_cover'] = self.weather.get_cloud_coverage()
            yield self.env.timeout(self.step_minutes)

    def run(self):
        """
        Starts the simulation loop using multiple generators.
        """
        # 1. Start the global clock process
        self.env.process(self._global_clock())
        
        # 2. Start an independent process for EACH house
        for house in self.neighborhood.houses:
            self.env.process(house.live(
                env=self.env,
                step_minutes=self.step_minutes,
                weather_state=self.weather_state,
                grid=self.grid,
                energy_manager=self.energy_manager,
                results=self.results
            ))
        
        # 3. Run the simulation
        self.env.run(until=self.duration_hours * 60) # Run in minutes
        
        # 4. Return results as a DataFrame
        return pd.DataFrame(self.results)