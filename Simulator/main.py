import yaml
import os
import pandas as pd
from src.engine import SimulationEngine
from datetime import datetime

def load_config(config_path):
    """
    Loads the simulation configuration from a YAML file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def generate_neighborhood(config):
    """
    Generates individual house configurations based on profiles and wealth multipliers.
    """
    houses = {}
    house_counter = 1

    profiles = config.get('house_profiles', {})
    multipliers = config.get('wealth_multipliers', {})
    composition = config.get('neighborhood_composition', [])

    for group in composition:
        profile_name = group['profile']
        wealth_level = group['wealth']
        count = group['count']

        base_stats = profiles[profile_name]
        wealth_factor = multipliers[wealth_level]

        for _ in range(count):
            house_id = f"house_{house_counter}"

            # Apply Wealth Effect multiplying the base and peak loads
            houses[house_id] = {
                "type": profile_name,
                "wealth": wealth_level,
                "load": {
                    "base_load_kw": base_stats['load']['base_load_kw'] * wealth_factor,
                    "peak_load_kw": base_stats['load']['peak_load_kw'] * wealth_factor,
                    "peak_start_hour": base_stats['load']['peak_start_hour'],
                    "peak_end_hour": base_stats['load']['peak_end_hour']
                },
                "battery": base_stats['hardware']['battery'],
                "solar": base_stats['hardware']['solar']
            }
            house_counter += 1

    return houses

def save_results(df_results, output_dir='outputs'):
    """
    Saves the simulation results to a CSV file with a timestamp.
    """
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Generate a timestamp string (e.g., "2023-10-27_14-30-00")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create a unique filename
    filename = os.path.join(output_dir, f'simulation_results_{timestamp}.csv')
    
    # Save the file
    df_results.to_csv(filename, index=False)
    print(f"\n✅ Results saved to: {filename}")

def print_summary(df):
    """
    Prints a quick summary of the simulation to the console.
    """
    print("\n" + "="*40)
    print("       SIMULATION SUMMARY")
    print("="*40)
    
    total_days = df['day'].max() + 1
    total_solar = df['solar_gen_kw'].sum()
    total_load = df['load_kw'].sum()
    total_import = df['grid_import_kw'].sum()
    total_export = df['grid_export_kw'].sum()
    net_cost = df['cost_cents'].sum() / 100  # Convert cents to dollars/pesos

    print(f"Duration:      {total_days} Days")
    print(f"Total Load:    {total_load:.2f} kWh")
    print(f"Total Solar:   {total_solar:.2f} kWh")
    print(f"Grid Import:   {total_import:.2f} kWh")
    print(f"Grid Export:   {total_export:.2f} kWh")
    print("-" * 40)
    print(f"NET COST:      ${net_cost:.2f}")
    print("="*40)

if __name__ == "__main__":
    # 1. Define paths
    CONFIG_PATH = 'config/simulation_config.yaml'

    try:
        print("🚀 Starting GreenGridSim...")

        # 2. Load Configuration
        config = load_config(CONFIG_PATH)
        print(f"   Configuration loaded from {CONFIG_PATH}")

        # 3. Generate Neighborhood
        config['houses'] = generate_neighborhood(config)
        print(f"   Generated {len(config['houses'])} houses in the neighborhood.")

        # 4. Initialize and Run Engine
        engine = SimulationEngine(config)
        print("   Running simulation...")
        results_df = engine.run()

        # 5. Save and Show Results
        save_results(results_df)
        print_summary(results_df)

    except Exception as e:
        print(f"\n❌ Error running simulation: {e}")