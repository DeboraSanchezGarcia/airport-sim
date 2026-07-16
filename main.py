import simpy
import numpy as np
import pandas as pd
import os
import json
import time
import random

# Passive Entities
class Gate:
    def __init__(self, env):
        self.resource = simpy.Resource(env, capacity=1)

class GroundCrew:
    def __init__(self, env):
        self.resource = simpy.Resource(env, capacity=1)

class ServiceVehicles:
    def __init__(self, env):
        self.resource = simpy.Resource(env, capacity=1)

# Active Entity
class Aircraft:
    def __init__(self, name, env, simulation):
        self.name = name
        self.env = env
        self.simulation = simulation

    def process_turnaround(self):
        arrival_time = self.env.now

        # Calculate shortest time to implement SJF priority
        service_time = np.random.triangular(10, 20, 40)

        # Weibull Distribution for weather delays
        weather_delay = 0.0
        # Assume a 15% chance a flight experiences a weather delay
        if np.random.rand() < 0.15: 
            weather_delay = np.random.weibull(1.5) * 15

        # service time including optional weather delays
        total_service_time = service_time + weather_delay
        
        # Requesting resources, gates are FIFO, crew and vehicles SJF

        # Gete is requested first to ensure aircraft requests crew and vehicles only after it has parked
        with self.simulation.gates.request() as gate_req:
            yield gate_req

        with self.simulation.ground_crew.request(priority=total_service_time) as crew_req, \
             self.simulation.service_vehicles.request(priority=total_service_time) as veh_req:
            
            yield crew_req & veh_req
            
            # Servicing (Triangular Distribution)
            yield self.env.timeout(total_service_time)
            
            # Collect metrics
            self.simulation.record_metrics(self.name, arrival_time, service_time, weather_delay)

# Airport Simulation
class AirportSimulation:
    SIMULATION_DURATION = 480 # 8 hours in minutes

    def __init__(self, env, run_id, arrival_rate, num_gates, num_crew, num_vehicles): 
        self.env = env
        self.run_id = run_id
        self.arrival_rate = arrival_rate

        # Dynamic capacities based on parameters
        self.gates = simpy.Resource(env, capacity=4) 
        self.ground_crew = simpy.PriorityResource(env, capacity=2)
        self.service_vehicles = simpy.PriorityResource(env, capacity=2)

        self.metrics = []
        self.state_metrics = [] # state metrics in response to M3 review

    # Response to M3 review for state metrics 
    def state_monitor(self):
        # Records the state of the airport resources every 1 minute (tick).
        while True:
            self.state_metrics.append({
                'run_id': self.run_id,
                'time_tick': self.env.now,
                'gates_in_use': self.gates.count,
                'gates_queue': len(self.gates.queue),
                'crew_in_use': self.ground_crew.count,
                'crew_queue': len(self.ground_crew.queue),
                'vehicles_in_use': self.service_vehicles.count,
                'vehicles_queue': len(self.service_vehicles.queue)
            })
            yield self.env.timeout(1) # Wait 1 minute before recording again

    def arrival_generator(self):
        count = 1
        while True:
            # Exponential Distribution 
            yield self.env.timeout(np.random.exponential(1.0 / self.arrival_rate))
            
            # New Aircraft
            plane = Aircraft(f"Plane {count}", self.env, self)
            self.env.process(plane.process_turnaround())
            count += 1

    def run_simulation(self, duration=SIMULATION_DURATION):
        self.env.process(self.arrival_generator())
        self.env.process(self.state_monitor()) # start monitor process for state metrics
        self.env.run(until=duration)

    def record_metrics(self, name, arrival_time, base_service_time, weather_delay):
        # total time spent at gate
        total_service_time = base_service_time + weather_delay

        wait_time = self.env.now - arrival_time - total_service_time
        total_turnaround_time = wait_time + total_service_time

        # Show departure time in 12 hour format
        departure_minute = self.env.now
        shift_start = pd.to_datetime('08:00:00')
        actual_time = shift_start + pd.to_timedelta(departure_minute, unit='m')
        clock_time_str = actual_time.strftime('%I:%M %p')


        self.metrics.append({
            'run_id': self.run_id,
            'aircraft': name,
            'wait_time': round(wait_time, 2),          # Rounded for cleaner CSV
            'base_service_time': round(base_service_time, 2),    # Rounded for cleaner CSV
            'weather_delay_mins': round(weather_delay, 2),
            'total_turnaround_time': round(total_turnaround_time, 2),
            'departure_clock_time': clock_time_str
            
        })

    def save_to_csv(self, filename):
        df = pd.DataFrame(self.metrics)
        file_exists = os.path.isfile(filename)
        df.to_csv(filename, mode='w', index=False)
        print(f"Metrics saved to {filename}")

# Execution
if __name__ == "__main__":
    try:
        with open('scenarios.json', 'r') as file:
            scenarios = json.load(file)
    except FileNotFoundError:
        print("Error: Configuration file 'scenarios.json' not found.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: 'scenarios.json' contains invalid JSON format.")
        exit(1)

    # Define the number of independent replications (response to M3 review)
    NUM_REPLICATIONS = 10

    # Master dataframe to hold all results
    all_metrics = pd.DataFrame()
    # Dataframe for state data
    all_state_metrics = pd.DataFrame()

    print(f"Starting Simulation Suite ({NUM_REPLICATIONS} replications per scenario)...")

    for config in scenarios:
        if config['gates'] <= 0 or config['crew'] <= 0 or config['vehicles'] <= 0:
            print(f"Error in Run {config['run_id']}: Resource amounts must be positive integers. Skipping...")
            continue
        if config['arrival_rate'] <= 0:
            print(f"Error in Run {config['run_id']}: Arrival rate must be greater than 0. Skipping...")
            continue

        print(f"Executing Scenario {config['run_id']}...")  

        for rep in range(1, NUM_REPLICATIONS + 1):
            
            # Multiply run_id by 100 and add the rep number so Scenario 1 Rep 1 is seed 101, Scenario 2 Rep 1 is 201, etc.
            seed_value = int(config['run_id']) * 100 + rep
            np.random.seed(seed_value)
            random.seed(seed_value)

            start_time = time.time()
            env = simpy.Environment()
            
            # Initialize simulation with dynamic parameters
            sim = AirportSimulation(
                env=env,
                run_id=config['run_id'],
                arrival_rate=config['arrival_rate'],
                num_gates=config['gates'],
                num_crew=config['crew'],
                num_vehicles=config['vehicles']
            )
            
            sim.run_simulation()

            end_time = time.time() 
            cpu_execution_time = round(end_time - start_time, 4)
            
            # Append aircraft metrics
            run_df = pd.DataFrame(sim.metrics)
            if not run_df.empty:
                run_df['cpu_execution_time_sec'] = cpu_execution_time
                # Track which replication this came from
                run_df['replication_id'] = rep
                all_metrics = pd.concat([all_metrics, run_df], ignore_index=True)
                
            # Append state metrics
            state_df = pd.DataFrame(sim.state_metrics)
            if not state_df.empty:
                # Track which replication this came from
                state_df['replication_id'] = rep 
                all_state_metrics = pd.concat([all_state_metrics, state_df], ignore_index=True)

        print(f"  -> Finished {NUM_REPLICATIONS} replications for Scenario {config['run_id']}.")

    
    # Save the aggregated results
    if not all_metrics.empty:
        all_metrics.to_csv("simulation_metrics.csv", index=False)
        all_state_metrics.to_csv("system_state_metrics.csv", index=False)
        print("\nSuccess! All runs complete. Data saved to simulation_metrics.csv and and system_state_metrics.csv.")
    else:
        print("\nSimulation completed, but no metrics were collected (check your parameters).")