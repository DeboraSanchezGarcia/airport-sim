import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Got rid of generate_m3_summary()

def generate_statistical_summary(df):
    print("--- M4 Statistical Summary (Wait Times) ---")
    
    # Group by run_id and replication_id to get the daily averages
    daily_averages = df.groupby(['run_id', 'replication_id'])['wait_time'].mean().reset_index()

    # Group by run_id to calculate the overall stats across the 10 replications
    summary_stats = daily_averages.groupby('run_id')['wait_time'].agg(
        mean_wait='mean',
        std_wait='std',
        min_wait='min',
        max_wait='max',
        n_runs='count'
    ).reset_index()

    # Calculate the 95% Confidence Interval using the M4 Formula
    # CI = mean +/- 1.96 * (std / sqrt(n))
    summary_stats['margin_of_error'] = 1.96 * (summary_stats['std_wait'] / np.sqrt(summary_stats['n_runs']))
    summary_stats['ci_lower'] = summary_stats['mean_wait'] - summary_stats['margin_of_error']
    summary_stats['ci_upper'] = summary_stats['mean_wait'] + summary_stats['margin_of_error']

    # Format
    summary_stats = summary_stats.round(2)
    
    for index, row in summary_stats.iterrows():
        print(f"Run {int(row['run_id'])}:")
        print(f"  Mean Wait: {row['mean_wait']} mins (Std Dev: {row['std_wait']})")
        print(f"  95% CI:    [{row['ci_lower']}, {row['ci_upper']}]")
        print(f"  Range:     {row['min_wait']} to {row['max_wait']} mins\n")

    return summary_stats

# based on M3 findings
def calculate_sensitivity(df, base_run, test_run, input_name, base_input_val, test_input_val):
    # Get the overall mean wait time for the base run and test run
    base_mean = df[df['run_id'] == base_run]['wait_time'].mean()
    test_mean = df[df['run_id'] == test_run]['wait_time'].mean()
    
    # Calculate percentage changes
    pct_change_input = (test_input_val - base_input_val) / base_input_val
    pct_change_output = (test_mean - base_mean) / base_mean
    
    # Calculate sensitivity
    sensitivity = pct_change_output / pct_change_input
    
    print(f"--- Sensitivity Analysis: {input_name} (Run {base_run} vs Run {test_run}) ---")
    print(f"Base Wait Time: {base_mean:.2f} mins | Test Wait Time: {test_mean:.2f} mins")
    print(f"% Change Input ({input_name}): {pct_change_input*100:.2f}%")
    print(f"% Change Output (Wait Time): {pct_change_output*100:.2f}%")
    print(f"Sensitivity: {sensitivity:.2f}\n")
    return sensitivity

if __name__ == "__main__":

    try:
        df = pd.read_csv("simulation_metrics.csv")
    except FileNotFoundError:
        print("Error: simulation_metrics.csv not found. Make sure you run main.py first!")
        exit()

    # Generate the stats and Confidence Intervals
    stats = generate_statistical_summary(df)

    # Calculate Sensitivity for Gates (Run 1 vs Run 8: Gates go from 4 to 3)
    calculate_sensitivity(df, base_run=1, test_run=8, input_name="Gates", base_input_val=4, test_input_val=3)
    # Calculate Sensitivity for Gates (Run 1 vs Run 7: Gates go from 4 to 5)
    calculate_sensitivity(df, base_run=1, test_run=7, input_name="Gates +1", base_input_val=4, test_input_val=5)

    
    # Calculate Sensitivity for Crew and Vehicles(Run 1 vs Run 10: Crew and Vehicles go from 2 each to 1 each)
    calculate_sensitivity(df, base_run=1, test_run=10, input_name="Ground Crew and Service Vehicles", base_input_val=2, test_input_val=1)

    calculate_sensitivity(df, base_run=1, test_run=4, input_name="4 Ground Crew and 4 Service Vehicles", base_input_val=2, test_input_val=4)


