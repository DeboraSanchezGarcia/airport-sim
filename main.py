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
        
        # Requesting resources from the simulation instance
        with self.simulation.gates.request() as gate_req, \
             self.simulation.ground_crew.request() as crew_req, \
             self.simulation.service_vehicles.request() as veh_req:
            
            yield gate_req & crew_req & veh_req
            
            # Servicing (Triangular Distribution)
            service_time = np.random.triangular(10, 20, 40)
            yield self.env.timeout(service_time)
            
            # Collect metrics
            self.simulation.record_metrics(self.name, arrival_time, service_time)

# Airport Simulation
class AirportSimulation:
    ARRIVAL_RATE = 0.8333 # estimating 40 planes in an 8 hour day (480 minutes)
    SIMULATION_DURATION = 480 # 8 hours in minutes

    def __init__(self, env, arrival_rate=ARRIVAL_RATE): 
        self.env = env
        self.arrival_rate = arrival_rate
        self.gates = simpy.Resource(env, capacity=4) 
        self.ground_crew = simpy.Resource(env, capacity=2)
        self.service_vehicles = simpy.Resource(env, capacity=2)
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

    def record_metrics(self, name, arrival_time, service_time):
        wait_time = self.env.now - arrival_time - service_time
        self.metrics.append({
            'aircraft': name,
            'wait_time': wait_time,
            'service_time': service_time,
            'completion_time': self.env.now
        })

    def save_to_csv(self, filename):
        df = pd.DataFrame(self.metrics)
        file_exists = os.path.isfile(filename)
        df.to_csv(filename, mode='w', index=False)
        print(f"Metrics saved to {filename}")

# Execution
env = simpy.Environment()
sim = AirportSimulation(env,)
sim.run_simulation()
sim.save_to_csv("simulation_metrics.csv")
data = pd.read_csv("simulation_metrics.csv")
print(data)