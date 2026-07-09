import pandas as pd

def generate_m3_summary():
    print("Loading simulation metrics...")
    
    try:
        # Load the newly generated data
        df = pd.read_csv("simulation_metrics.csv")
    except FileNotFoundError:
        print("Error: simulation_metrics.csv not found. Please run main.py first.")
        return

    # Group by run_id and calculate our key metrics
    summary = df.groupby('run_id').agg(
        Total_Planes_Processed=('aircraft', 'count'),
        Avg_Wait_Time_mins=('wait_time', 'mean'),
        Avg_Weather_Delay_mins=('weather_delay_mins', 'mean'),
        Avg_Turnaround_Time_mins=('total_turnaround_time', 'mean'),
        Max_Wait_Time_mins=('wait_time', 'max')
    ).round(2)

    # Add descriptive scenario names to match the 10 variations
    scenario_names = [
        "1. Baseline (4 Gates, 2 Crew, 2 Veh)", 
        "2. Extra Crew (+1)", 
        "3. Extra Vehicles (+1)", 
        "4. High Resources (4 Crew, 4 Veh)", 
        "5. High Traffic (Stress Test)", 
        "6. High Traffic + High Resources", 
        "7. Extra Gate (5 Gates)", 
        "8. Reduced Gates (Bottleneck, 3 Gates)", 
        "9. Mega Airport Expansion (6 Gates)", 
        "10. Low Traffic, Low Resources"
    ]
    
    # Insert the scenario names as the first column
    summary.insert(0, 'Scenario_Description', scenario_names)

    # Print the table in Markdown format (Perfect for copy-pasting into reports!)
    print("\n" + "="*60)
    print("MILESTONE 3: RUN SUMMARY TABLE")
    print("="*60 + "\n")
    print(summary.to_markdown(index=False))
    print("\n" + "="*60)

if __name__ == "__main__":
    generate_m3_summary()