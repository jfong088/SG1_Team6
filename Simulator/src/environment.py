import random

class Weather:
    """
    Simulates environmental conditions, specifically cloud coverage.
    
    Uses weighted probabilities based on the current season to determine
    daily cloud patterns.
    """

    def __init__(self, config_data):
        """
        Initializes the weather model.

        Args:
            config_data (dict): The 'simulation' section from simulation_config.json.
        """
        self.season = config_data.get('season', 'Summer')

        # Probability weights for cloud coverage levels:
        # (Clear, Partly Cloudy, Mostly Cloudy, Overcast)
        self.season_weights = {
            'Spring': [0.1, 0.3, 0.4, 0.2],
            'Summer': [0.05, 0.15, 0.3, 0.5],
            'Fall':   [0.2, 0.4, 0.3, 0.1],
            'Winter': [0.3, 0.4, 0.2, 0.1]
        }

    def get_cloud_coverage(self):
        """
        Generates a random cloud coverage factor for the day.
        
        Returns:
            float: A value between 0.0 (Clear) and 1.0 (Overcast).
        """
        # 1. Get weights for the current season
        weights = self.season_weights.get(self.season, [0.25, 0.25, 0.25, 0.25])
        
        # 2. Select a weather category based on weights
        # Categories: 0=Clear, 1=Partly, 2=Mostly, 3=Overcast
        category = random.choices([0, 1, 2, 3], weights=weights, k=1)[0]
        
        # 3. Generate specific coverage percentage based on category ranges
        if category == 0:   # Clear (0.0 - 0.2)
            return random.uniform(0.0, 0.2)
        elif category == 1: # Partly Cloudy (0.2 - 0.6)
            return random.uniform(0.2, 0.6)
        elif category == 2: # Mostly Cloudy (0.6 - 0.8)
            return random.uniform(0.6, 0.8)
        else:               # Overcast (0.8 - 1.0) - PDF says 0.8-0.9, but 1.0 is safer cap
            return random.uniform(0.8, 1.0)


class HomeLoad:
    """
    Represents the 'AC Home Load' from the diagram.
    
    Simulates household energy consumption with a base load and 
    stochastic spikes during peak hours.
    """

    def __init__(self, config_data):
        """
        Initializes the load profile.

        Args:
            config_data (dict): The 'load' section from simulation_config.json.
        """
        self.base_load_kw = config_data.get('base_load_kw', 0.5)
        self.peak_load_kw = config_data.get('peak_load_kw', 3.0)
        self.peak_start = config_data.get('peak_start_hour', 18) # 6 PM
        self.peak_end = config_data.get('peak_end_hour', 21)     # 9 PM

    def get_current_load(self, hour_of_day):
        """
        Calculates the instantaneous power demand of the house.
        
        Args:
            hour_of_day (float): Current hour (0-23).
            
        Returns:
            float: Power demand in kW.
        """
        # 1. Start with the base load (Fridge, Router, etc.)
        current_load = self.base_load_kw

        # 2. Add random noise/spikes
        # Random spikes up to 3 kW during peak hours (6-9 PM)"
        if self.peak_start <= hour_of_day <= self.peak_end:
            # Higher probability of high spikes during peak time
            spike = random.uniform(0, self.peak_load_kw)
        else:
            # Lower spikes during off-peak (occasional usage)
            spike = random.uniform(0, self.peak_load_kw * 0.1) # 10% of peak

        return current_load + spike


class UtilityGrid:
    """
    Represents the 'Utility Grid' from the diagram.
    
    Defines the constraints and costs for importing/exporting energy.
    """

    def __init__(self, config_data):
        """
        Initializes grid parameters.

        Args:
            config_data (dict): The 'grid' section from simulation_config.json.
        """
        self.export_limit_kw = config_data.get('export_limit_kw', 20.0)
        self.cost_import = config_data.get('cost_import_cents', 0.75)
        self.price_export = config_data.get('price_export_cents', 0.90)

    def calculate_cost(self, imported_kwh, exported_kwh):
        """
        Calculates the financial balance for a time period.
        
        Args:
            imported_kwh (float): Energy bought from grid.
            exported_kwh (float): Energy sold to grid.
            
        Returns:
            float: Net cost (positive = you pay, negative = you earn).
        """
        cost = imported_kwh * self.cost_import
        earnings = exported_kwh * self.price_export
        return cost - earnings