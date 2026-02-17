class EnergyManager:
    """
    The 'Brain' of the system.
    Decides how to distribute energy based on the selected priority strategy.
    Reference: PDF Page 4 [cite: 100]
    """

    def __init__(self, config_data):
        """
        Initializes the Energy Management System (EMS).

        Args:
            config_data (dict): The 'strategy' section from simulation_config.json.
        """
        # Strategies: 'LOAD_PRIORITY', 'CHARGE_PRIORITY', 'PRODUCE_PRIORITY'
        self.strategy_name = config_data.get('name', 'LOAD_PRIORITY')

    def decide_energy_flow(self, solar_gen_kw, load_demand_kw, battery, grid_limit_kw):
        """
        Executes the logic for the current time step.
        
        Args:
            solar_gen_kw (float): Current solar generation.
            load_demand_kw (float): Current house consumption.
            battery (Battery): The battery object (to check/update state).
            grid_limit_kw (float): Max export limit.

        Returns:
            dict: A report of where energy went (useful for logging).
        """
        # Initialize the log for this minute
        flow_log = {
            'solar_to_load': 0.0,
            'solar_to_battery': 0.0,
            'solar_to_grid': 0.0,
            'grid_import': 0.0,
            'battery_discharge': 0.0,
            'curtailed': 0.0  # Wasted energy
        }

        # Dispatch to the correct logic based on configuration
        if self.strategy_name == 'LOAD_PRIORITY':
            self._run_load_priority(solar_gen_kw, load_demand_kw, battery, grid_limit_kw, flow_log)
        elif self.strategy_name == 'CHARGE_PRIORITY':
            self._run_charge_priority(solar_gen_kw, load_demand_kw, battery, grid_limit_kw, flow_log)
        elif self.strategy_name == 'PRODUCE_PRIORITY':
            self._run_produce_priority(solar_gen_kw, load_demand_kw, battery, grid_limit_kw, flow_log)
        else:
            # Default fallback
            self._run_load_priority(solar_gen_kw, load_demand_kw, battery, grid_limit_kw, flow_log)

        return flow_log

    #  STRATEGY 1: LOAD PRIORITY (Default) 
    # "Power the house load first, charge the battery second, export excess last" [cite: 101]
    def _run_load_priority(self, solar, load, battery, grid_limit, log):
        
        # 1. Power the House
        if solar >= load:
            # Solar covers everything
            log['solar_to_load'] = load
            excess_solar = solar - load
        else:
            # Solar is not enough
            log['solar_to_load'] = solar
            excess_solar = 0.0
            deficit = load - solar
            
            # Try to cover deficit with Battery
            discharged = battery.discharge(deficit)
            log['battery_discharge'] = discharged
            
            # If still not enough, buy from Grid
            remaining_deficit = deficit - discharged
            if remaining_deficit > 0:
                log['grid_import'] = remaining_deficit

        # 2. Charge Battery with Excess
        if excess_solar > 0:
            charged = battery.charge(excess_solar)
            log['solar_to_battery'] = charged
            excess_solar -= charged # Remaining after charging

        # 3. Export to Grid
        if excess_solar > 0:
            to_export = min(excess_solar, grid_limit)
            log['solar_to_grid'] = to_export
            excess_solar -= to_export
        
        # 4. Curtailment (Waste)
        if excess_solar > 0:
            log['curtailed'] = excess_solar

    #  STRATEGY 2: CHARGE PRIORITY 
    # Charge the battery first, power the house load second, export excess last
    def _run_charge_priority(self, solar, load, battery, grid_limit, log):
        
        remaining_solar = solar

        # 1. Charge Battery First
        if remaining_solar > 0:
            charged = battery.charge(remaining_solar)
            log['solar_to_battery'] = charged
            remaining_solar -= charged

        # 2. Power House Second
        # Calculate what the house needs (Battery didn't help here, logic is strict)
        # Note: If solar was used by battery, house might need to import.
        if remaining_solar >= load:
            log['solar_to_load'] = load
            remaining_solar -= load
        else:
            log['solar_to_load'] = remaining_solar
            deficit = load - remaining_solar
            remaining_solar = 0.0
            
            # In Charge Priority, do we discharge battery to help load? 
            # Usually NO during solar generation, but YES if solar is 0 (night).
            # For simplicity: If we just charged it, we shouldn't discharge it immediately.
            # So deficit comes from grid.
            log['grid_import'] = deficit

        # 3. Export Third
        if remaining_solar > 0:
            to_export = min(remaining_solar, grid_limit)
            log['solar_to_grid'] = to_export
            remaining_solar -= to_export
            
        log['curtailed'] = remaining_solar

    #  STRATEGY 3: PRODUCE PRIORITY 
    # Export all energy up to threshold first, charge battery second, house last
    def _run_produce_priority(self, solar, load, battery, grid_limit, log):
        
        remaining_solar = solar

        # 1. Export First
        to_export = min(remaining_solar, grid_limit)
        log['solar_to_grid'] = to_export
        remaining_solar -= to_export

        # 2. Charge Battery Second
        if remaining_solar > 0:
            charged = battery.charge(remaining_solar)
            log['solar_to_battery'] = charged
            remaining_solar -= charged
            
        # 3. Power House Last
        if remaining_solar >= load:
            log['solar_to_load'] = load
            remaining_solar -= load
        else:
            log['solar_to_load'] = remaining_solar
            deficit = load - remaining_solar
            remaining_solar = 0.0
            
            # House needs energy. (Try battery first) 
            # Logic implies preserving export, but if we have battery we use it.
            discharged = battery.discharge(deficit)
            log['battery_discharge'] = discharged
            
            remaining_deficit = deficit - discharged
            log['grid_import'] = remaining_deficit

        log['curtailed'] = remaining_solar