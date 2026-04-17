import pandas as pd
import glob
import os
import json
from pathlib import Path

def get_latest_csv(output_dir='outputs'):
    """Finds the most recently generated CSV file."""
    list_of_files = glob.glob(f'{output_dir}/*.csv')
    if not list_of_files:
        raise FileNotFoundError("No CSV files were found in the outputs folder.")
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def process_simulation_data(csv_path):
    """Processes the CSV and extracts metrics for the Dashboard."""
    df = pd.read_csv(csv_path)

    # Prepare the Duck Curve & Battery Utilization
    # Calculate the net load (Consumption - Solar) for each hour
    df['net_load_kw'] = df['load_kw'] - df['solar_gen_kw']
    # ADDED: 'battery_soc_kwh' to see how the battery behaves during the day
    duck_curve = df.groupby('hour')[['load_kw', 'solar_gen_kw', 'net_load_kw', 'battery_soc_kwh']].mean().reset_index()

    # Grouping by House Type
    by_house_type = df.groupby('house_type').agg({
        'load_kw': 'sum',
        'solar_gen_kw': 'sum',
        'self_consumption_kw': 'sum'
    }).reset_index()

    # Grouping by Wealth Level
    by_wealth = df.groupby('wealth_level').agg({
        'load_kw': 'sum',
        'solar_gen_kw': 'sum',
        'self_consumption_kw': 'sum'
    }).reset_index()

    # By House 
    by_house = df.groupby(['house_id', 'house_type', 'wealth_level']).agg({
        'grid_export_kw': 'sum',
        'cost_cents': lambda x: (x.sum() / 100), # Net cost
        'self_consumption_kw': 'sum'
    }).reset_index()

    # Calculate savings per house (Self-consumption * rate)
    by_house['savings_dollars'] = (by_house['self_consumption_kw'] * 75) / 100

    # Peak times calculations
    peak_load_hour = df.groupby('hour')['load_kw'].mean().idxmax()
    peak_solar_hour = df.groupby('hour')['solar_gen_kw'].mean().idxmax()
    
    # Self-consumption savings (Assuming $0.75 import cost from config)
    # We calculate the money saved by consuming our own solar energy
    total_self_consumed_kwh = float(df['self_consumption_kw'].sum())
    savings_dollars = (total_self_consumed_kwh * 75) / 100 

    # General Summary (Enhanced)
    summary = {
        'total_load': float(df['load_kw'].sum()),
        'total_solar': float(df['solar_gen_kw'].sum()),
        'total_import': float(df['grid_import_kw'].sum()),
        'total_export': float(df['grid_export_kw'].sum()),
        'net_cost': float(df['cost_cents'].sum() / 100),
        'total_self_consumption': total_self_consumed_kwh,
        'estimated_savings_dollars': float(savings_dollars),
        'peak_load_hour': int(peak_load_hour),
        'peak_solar_hour': int(peak_solar_hour)
    }

    # Structure everything into a single giant dictionary
    dashboard_data = {
        "summary": summary,
        "duck_curve": duck_curve.to_dict(orient='records'),
        "by_house_type": by_house_type.to_dict(orient='records'),
        "by_wealth": by_wealth.to_dict(orient='records'),
        "by_house": by_house.to_dict(orient='records')
    }

    return dashboard_data

def export_to_dashboard(dashboard_data):
    """Saves the JSON directly to the GitHub Pages web folder."""
    # Go up two levels from src/ and enter docs/
    base_dir = Path(__file__).resolve().parent.parent.parent  
    data_dir = base_dir / 'docs' / 'data'
    # Create the folder if it doesn't exist
    data_dir.mkdir(exist_ok=True)
    
    json_path = data_dir / 'dashboard_data.json'
    
    with open(json_path, 'w') as f:
        json.dump(dashboard_data, f, indent=4)
    
    print(f"📊 Data successfully processed and exported to: {json_path}")

def run_pipeline():
    """Main function to run the entire preparation workflow."""
    latest_csv = get_latest_csv()
    print(f"Processing file: {latest_csv}")
    data = process_simulation_data(latest_csv)
    export_to_dashboard(data)

if __name__ == "__main__":
    run_pipeline()