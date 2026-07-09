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
        
        # Requesting resources, gates are FIFO, crew and vehicles SJF

        # Gete is requested first to ensure aircraft requests crew and vehicles only after it has parked
        with self.simulation.gates.request() as gate_req:
            yield gate_req

        with self.simulation.ground_crew.request(priority=service_time) as crew_req, \
             self.simulation.service_vehicles.request(priority=service_time) as veh_req:
            
            yield crew_req & veh_req
            
            # Servicing (Triangular Distribution)
            yield self.env.timeout(service_time)
            
            # Collect metrics
            self.simulation.record_metrics(self.name, arrival_time, service_time)

# Airport Simulation
class AirportSimulation:
    ARRIVAL_RATE = 0.08333 # estimating 40 planes in an 8 hour day (480 minutes)
    SIMULATION_DURATION = 480 # 8 hours in minutes

    def __init__(self, env, arrival_rate=ARRIVAL_RATE): 
        self.env = env
        self.arrival_rate = arrival_rate
        self.gates = simpy.Resource(env, capacity=4) 
        self.ground_crew = simpy.PriorityResource(env, capacity=2)
        self.service_vehicles = simpy.PriorityResource(env, capacity=2)
        self.metrics = []

    def arrival_generator(self):
        count = 1
        while True:
            # Exponential Distribution 
            yield self.env.timeout(np.random.exponential(1.0 / self.ARRIVAL_RATE))
            
            # New Aircraft
            plane = Aircraft(f"Plane {count}", self.env, self)
            self.env.process(plane.process_turnaround())
            count += 1

    def run_simulation(self, duration=SIMULATION_DURATION):
        self.env.process(self.arrival_generator())
        self.env.run(until=duration)

    def record_metrics(self, name, arrival_time, service_time):
        wait_time = self.env.now - arrival_time - service_time
        completion_time_minutes = self.env.now

        shift_start = pd.to_datetime('08:00:00')
        actual_time = shift_start + pd.to_timedelta(completion_time_minutes, unit='m')
        clock_time_str = actual_time.strftime('%I:%M %p')


        self.metrics.append({
            'aircraft': name,
            'wait_time': round(wait_time, 2),          # Rounded for cleaner CSV
            'service_time': round(service_time, 2),    # Rounded for cleaner CSV
            'departure_clock_time': clock_time_str
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