from src.components import Battery, SolarPanel, Inverter
from src.environment import HomeLoad

class House:
    """
    Represents a single household in the simulation.
    Contains its own hardware and acts as an independent SimPy process.
    """
    def __init__(self, house_id, config_data):
        self.house_id = house_id
        self.house_type = config_data['type']
        self.wealth = config_data['wealth']
        
        # Initialize individual hardware
        self.battery = Battery(config_data['battery'])
        self.solar_panel = SolarPanel(config_data['solar'])
        self.inverter = Inverter(config_data['solar'])
        self.home_load = HomeLoad(config_data['load'])

    def live(self, env, step_minutes, weather_state, grid, energy_manager, results):
        """
        SimPy generator process. Simulates the house's activity over time.
        """
        while True:
            # 1. Understand current time
            current_time_min = env.now
            current_hour = (current_time_min / 60) % 24
            day_number = int(current_time_min / (60 * 24))

            # 2. Get global weather for this timestep
            cloud_cover = weather_state.get('cloud_cover', 0.0)

            # 3. Calculate Physics
            dc_solar_kw = self.solar_panel.get_generation(current_hour, cloud_cover)
            ac_solar_kw = self.inverter.clip_power(dc_solar_kw)
            load_kw = self.home_load.get_current_load(current_hour)

            # 4. Execute Strategy
            flow = energy_manager.decide_energy_flow(
                solar_gen_kw=ac_solar_kw, 
                load_demand_kw=load_kw, 
                battery=self.battery, 
                grid_limit_kw=grid.export_limit_kw
            )

            # 5. Calculate Economics
            step_cost = grid.calculate_cost(flow['grid_import'], flow['solar_to_grid'])

            # 6. Log Data (Including self-consumption)
            self_consumption = flow.get('solar_to_load', 0.0) + flow.get('solar_to_battery', 0.0)
            
            results.append({
                'time_min': current_time_min,
                'day': day_number,
                'hour': current_hour,
                'house_id': self.house_id,
                'house_type': self.house_type,
                'wealth_level': self.wealth,
                'solar_gen_kw': ac_solar_kw,
                'load_kw': load_kw,
                'battery_soc_kwh': self.battery.current_energy_kwh,
                'grid_import_kw': flow['grid_import'],
                'grid_export_kw': flow['solar_to_grid'],
                'self_consumption_kw': self_consumption,
                'cost_cents': step_cost
            })

            # 7. Yield control back to SimPy until the next step
            yield env.timeout(step_minutes)


class Neighborhood:
    """
    A container class that builds and holds all the houses.
    """
    def __init__(self, houses_config):
        self.houses = []
        for house_id, house_data in houses_config.items():
            self.houses.append(House(house_id, house_data))
            