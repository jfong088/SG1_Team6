import random
import math

class Battery:
    """
    Represents a residential battery energy storage system.
    
    Models the physical constraints including capacity, state of charge (SoC),
    round-trip efficiency, and discharge depth limits.
    """

    def __init__(self, config_data):
        """
        Initializes the battery with configuration parameters.

        Args:
            config_data (dict): Dictionary containing battery specifications 
                                from simulation_config.json.
        """
        # --- Physical Attributes (Constants) ---
        # Default: 13.5 kWh (Tesla Powerwall standard) [cite: 48, 84]
        self.capacity_kwh = config_data.get('capacity', 13.5)
        
        # Round-trip efficiency (e.g., 0.90 means 10% loss total) [cite: 50, 95]
        self.efficiency_rt = config_data.get('efficiency', 0.90)
        
        # Minimum allowed discharge depth (e.g., 0.05 or 5%) [cite: 49]
        self.min_soc_limit_pct = config_data.get('discharge_depth', 0.05)

        # --- Dynamic State (Variables) ---
        # Initial State of Charge (SoC) as a percentage (0.0 to 1.0)
        initial_state_pct = config_data.get('initial_state', 0.0)
        
        # Convert initial percentage to actual energy in kWh
        self.current_energy_kwh = self.capacity_kwh * initial_state_pct

        # Calculate One-Way Efficiency
        # Since efficiency is round-trip (Charge -> Discharge), we apply 
        # the square root for a single direction (Input -> Storage).
        # sqrt(0.90) approx 0.948
        self.efficiency_ow = math.sqrt(self.efficiency_rt)

    def charge(self, energy_input_kwh):
        """
        Attempts to charge the battery with a specific amount of energy.

        Args:
            energy_input_kwh (float): Energy provided by solar or grid.

        Returns:
            float: The actual energy consumed from the source. 
                   (May be less than input if battery is full).
        """
        # 1. Calculate potential energy to store after efficiency loss
        #  - Modeling loss in energy during charge
        energy_to_store = energy_input_kwh * self.efficiency_ow

        # 2. Calculate available space in the battery
        space_available = self.capacity_kwh - self.current_energy_kwh

        # 3. Check for overflow (Clipping)
        if energy_to_store > space_available:
            energy_to_store = space_available
            # Reverse calculation: How much input was actually needed to fill this space?
            real_input = space_available / self.efficiency_ow
        else:
            real_input = energy_input_kwh

        # 4. Update state
        self.current_energy_kwh += energy_to_store

        return real_input

    def discharge(self, energy_needed_kwh):
        """
        Attempts to discharge the battery to meet a load demand.

        Args:
            energy_needed_kwh (float): Energy required by the house.

        Returns:
            float: The actual energy supplied by the battery.
        """
        # 1. Calculate the energy floor (minimum charge level) [cite: 49]
        min_energy_kwh = self.capacity_kwh * self.min_soc_limit_pct
        
        # 2. Calculate usable energy above that floor
        available_energy = self.current_energy_kwh - min_energy_kwh

        # If battery is too low, we cannot provide anything
        if available_energy <= 0:
            return 0.0

        # 3. Calculate internal energy drain required
        # To output 1 kWh, we must drain >1 kWh due to internal resistance/losses.
        energy_to_drain = energy_needed_kwh / self.efficiency_ow

        # 4. Check if we have enough energy
        if energy_to_drain > available_energy:
            # We don't have enough; drain everything usable
            energy_to_drain = available_energy
            # Output is what we drained * efficiency
            real_output = available_energy * self.efficiency_ow
        else:
            # We have enough
            real_output = energy_needed_kwh

        # 5. Update state
        self.current_energy_kwh -= energy_to_drain

        return real_output


class SolarPanel:
    """
    Represents the 'Solar panels' from the diagram.
    
    Converts solar irradiance into DC power using a sinusoidal model 
    adjusted for time of day and cloud coverage.
    """

    def __init__(self, config_data):
        """
        Initializes the solar array.

        Args:
            config_data (dict): The 'solar' section from simulation_config.json.
        """
        # [cite_start]Peak generation capacity in kW (e.g., 5.0 kW) [cite: 88]
        self.peak_power_kw = config_data.get('panel_peak_kw', 5.0)

    def get_generation(self, time_of_day_hour, cloud_coverage_pct):
        """
        Calculates solar power output for a specific time and weather condition.
        
        Args:
            time_of_day_hour (float): Current hour (0.0 to 23.99).
            [cite_start]cloud_coverage_pct (float): 0.0 (Clear) to 1.0 (Overcast)[cite: 106].
            
        Returns:
            float: Generated power in kW.
        """
        # Solar generation window: roughly 6:00 AM to 6:00 PM
        sunrise_hour = 6
        sunset_hour = 18

        # 1. Check if it's night time
        if time_of_day_hour < sunrise_hour or time_of_day_hour > sunset_hour:
            return 0.0

        # 2. Calculate Sun Angle (0 to Pi radians)
        # [cite_start]We map the 12 hours of daylight to Pi radians (180 degrees) [cite: 89-90]
        daylight_duration = sunset_hour - sunrise_hour
        sun_angle = (time_of_day_hour - sunrise_hour) * (math.pi / daylight_duration)

        # 3. Calculate Base Generation using Sine Wave
        base_generation = self.peak_power_kw * math.sin(sun_angle)

        # 4. Apply Cloud Factor
        # [cite_start]"cloud coverage of 0.3 would reduce generation by 30%" [cite: 107]
        actual_generation = base_generation * (1 - cloud_coverage_pct)

        return max(0.0, actual_generation)

class Inverter:
    """
    Represents the 'Inverter' from the diagram.
    
    Acts as the bridge between DC components and AC loads. 
    Handles power clipping logic and simulates random hardware failures.
    """

    def __init__(self, config_data):
        """
        Initializes the inverter parameters.

        Args:
            config_data (dict): The 'solar' section from simulation_config.json.
        """
        # [cite_start]Maximum power output (Clipping limit) [cite: 52, 96]
        self.max_output_kw = config_data.get('inverter_max_kw', 4.0)
        
        # [cite_start]Failure probability per step (e.g., 0.005 for 0.5%) [cite: 117]
        self.failure_probability = config_data.get('inverter_failure_rate', 0.005)
        
        # [cite_start]Duration limits for failure (in hours) [cite: 117]
        self.min_repair_time = config_data.get('failure_duration_min_hours', 4)
        self.max_repair_time = config_data.get('failure_duration_max_hours', 72)

        # Internal State
        self.is_broken = False
        self.hours_until_repair = 0

    def check_status(self):
        """
        Updates and checks the operational status of the inverter.
        Must be called once per time step.
        
        Returns:
            bool: True if working, False if broken.
        """
        # 1. If currently broken, decrease repair timer
        if self.is_broken:
            self.hours_until_repair -= 1
            if self.hours_until_repair <= 0:
                self.is_broken = False  # Fixed!
            else:
                return False  # Still broken

        # 2. If working, roll the dice for a new failure
        # [cite_start]"random failure event that occurs on average once every 200 days" [cite: 117]
        if random.random() < self.failure_probability:
            self.is_broken = True
            # [cite_start]Duration between 4 to 72 hours [cite: 117]
            self.hours_until_repair = random.randint(
                self.min_repair_time, 
                self.max_repair_time
            )
            return False

        return True

    def clip_power(self, dc_power_kw):
        """
        Limits the power output based on inverter capacity.
        
        Args:
            dc_power_kw (float): Raw power from solar panels.
            
        Returns:
            float: AC power output (clipped if necessary, 0 if broken).
        """
        # [cite_start]If broken, solar generation is zero regardless of conditions [cite: 118]
        if not self.check_status():
            return 0.0
            
        # [cite_start]Apply Clipping: "If solar generation exceeds this limit, the excess is lost" [cite: 97]
        return min(dc_power_kw, self.max_output_kw)
    