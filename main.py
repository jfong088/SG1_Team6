import json
import os
import pandas as pd
from src.engine import SimulationEngine
from datetime import datetime

def load_config(config_path):
    """
    Loads the simulation configuration from a JSON file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
        
    with open(config_path, 'r') as f:
        return json.load(f)

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
    CONFIG_PATH = 'config/simulation_config.json'

    try:
        print("🚀 Starting GreenGridSim...")

        # 2. Load Configuration
        config = load_config(CONFIG_PATH)
        print(f"   Configuration loaded from {CONFIG_PATH}")

        # 3. Initialize and Run Engine
        engine = SimulationEngine(config)
        print("   Running simulation...")
        results_df = engine.run()

        # 4. Save and Show Results
        save_results(results_df)
        print_summary(results_df)

    except Exception as e:
        print(f"\n❌ Error running simulation: {e}")