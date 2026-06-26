import simpy
import numpy as np
import pandas as pd
import os

class AirportSimulation:
    def __init__(self, env, num_gates=4, num_crew=2, num_vehicles=2):
        self.env = env
        # Resource definitions
        self.gates = simpy.Resource(env, capacity=num_gates)
        self.ground_crew = simpy.Resource(env, capacity=num_crew)
        self.service_vehicles = simpy.Resource(env, capacity=num_vehicles)
        self.metrics = []

    def aircraft_process(self, name):
        arrival_time = self.env.now
        
        # 1. Queue-Based System: Gate Request 
        with self.gates.request() as gate_req:
            yield gate_req
            
            # 2. Probability: Triangular Distribution 
            # Parameters: low, mode, high (example values)
            service_time = np.random.triangular(10, 20, 40)
            
            # Request resources
            with self.ground_crew.request() as crew_req, \
                 self.service_vehicles.request() as veh_req:
                yield crew_req & veh_req
                
                # Perform servicing
                yield self.env.timeout(service_time)
                
            wait_time = self.env.now - arrival_time
            # Initial Data Collection with example values
            self.metrics.append({
                'aircraft': name, 
                'wait_time': wait_time,
                'service_time': service_time
            })

def run_simulation():
    env = simpy.Environment()
    sim = AirportSimulation(env)
    
    # Process interaction: Add aircraft at intervals
    for i in range(10):
        env.process(sim.aircraft_process(f"Plane {i}"))
    
    env.run(until=100)
    
    # Export initial data
    file_exists = os.path.isfile("simulation_metrics.csv")
    df = pd.DataFrame(sim.metrics)
    df.to_csv("simulation_metrics.csv", mode='a', index=False, header=not file_exists)

    full_df = pd.read_csv("simulation_metrics.csv")

    pd.set_option('display.max_rows', None)
    print(full_df)

if __name__ == "__main__":
    run_simulation()