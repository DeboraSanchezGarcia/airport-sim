import simpy
import numpy as np
import pandas as pd
import os

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
    # 10 required parameter variations
    scenarios = [
        {'run_id': 1, 'arrival_rate': 0.0833, 'gates': 4, 'crew': 2, 'vehicles': 2}, # 1. Baseline
        {'run_id': 2, 'arrival_rate': 0.0833, 'gates': 4, 'crew': 3, 'vehicles': 2}, # 2. Extra Crew
        {'run_id': 3, 'arrival_rate': 0.0833, 'gates': 4, 'crew': 2, 'vehicles': 3}, # 3. Extra Vehicles
        {'run_id': 4, 'arrival_rate': 0.0833, 'gates': 4, 'crew': 4, 'vehicles': 4}, # 4. High Resources
        {'run_id': 5, 'arrival_rate': 0.12,   'gates': 4, 'crew': 2, 'vehicles': 2}, # 5. High Traffic (Stress Test)
        {'run_id': 6, 'arrival_rate': 0.12,   'gates': 4, 'crew': 4, 'vehicles': 4}, # 6. High Traffic + High Resources
        {'run_id': 7, 'arrival_rate': 0.0833, 'gates': 5, 'crew': 2, 'vehicles': 2}, # 7. Extra Gate, Base Resources
        {'run_id': 8, 'arrival_rate': 0.0833, 'gates': 3, 'crew': 2, 'vehicles': 2}, # 8. Reduced Gates (Bottleneck)
        {'run_id': 9, 'arrival_rate': 0.15,   'gates': 6, 'crew': 4, 'vehicles': 4}, # 9. Mega Airport Expansion
        {'run_id': 10,'arrival_rate': 0.05,   'gates': 4, 'crew': 1, 'vehicles': 1}, # 10. Low Traffic, Low Resources
    ]

    # Master dataframe to hold all results
    all_metrics = pd.DataFrame()

    print("Starting 10-Run Simulation Suite...")
    
    for config in scenarios:
        print(f"Executing Run {config['run_id']}...")
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
        
        # Convert this run's metrics to a dataframe and append to master
        run_df = pd.DataFrame(sim.metrics)
        all_metrics = pd.concat([all_metrics, run_df], ignore_index=True)

    # Save the aggregated results
    all_metrics.to_csv("simulation_metrics.csv", index=False)
    print("\nSuccess! All 10 runs complete. Data saved to simulation_metrics.csv.")