# airport-sim

This project simulates the gate operations of a regional airport, including handling of arrivals, departures,
and finite resources such as gates, ground crew, and service vehicles. It will also optimize usage time and
make decisions based on random delays.

--- Project Status ---
The project has entered the implementation phase, with the core discrete-event simulation logic now operational. The simulation follows OOP paradigms, featuring an Aircraft class for active processes and separate resource classes for passive resources such as gates, ground crews, and service vehicles.

A Poisson process has been implemented for aircraft arrivals using the exponential distribution to model traffic, enabling a realistic 8-hour operational cycle. Currently, the system manages resources through a FIFO queuing logic and logs all key performance metrics, such as wait times and service durations, directly into a CSV file for later analysis. The simulation is now stable, and work is shifting toward tuning probability with initial data produced, developing a scheduling algorithm, and including a Weibull algorithm to simulate weather delays.

Using Python 3.12.3

To Set Up:
- require Python 3.12.3
- Github (clone https://github.com/DeboraSanchezGarcia/airport-sim.git)
- install requirements.txt

Expected Behavior:
A CSV will be produced that holds all the arrivals for that iteration (time units are given in minutes.)

Main Component Classes:
Entities - Gates, Service Vehicles, Ground Crew, Aircraft
AirportSimulation: handles random arrivals using exponential distribution, initates requests for resources, and stores data

Overall classes and architecture are quite similar to UML design for M1, with the change that the ResourceManager has been absorbed into each class using simpy.

IMPORTANT!!! Information about simulation runs.

    {"run_id": 1, "arrival_rate": 0.0833, "gates": 4, "crew": 2, "vehicles": 2},    base state, 4 gates, 2 crew, 2 vehicles
    {"run_id": 2, "arrival_rate": 0.0833, "gates": 4, "crew": 3, "vehicles": 2},    3 crews
    {"run_id": 3, "arrival_rate": 0.0833, "gates": 4, "crew": 2, "vehicles": 3},    3 vehicles
    {"run_id": 4, "arrival_rate": 0.0833, "gates": 4, "crew": 4, "vehicles": 4},    4 crews, 4 vehicles
    {"run_id": 5, "arrival_rate": 0.12,   "gates": 4, "crew": 2, "vehicles": 2},    0.12 arrival rate as opposed to original 0.08333 (more arrivals)
    {"run_id": 6, "arrival_rate": 0.12,   "gates": 4, "crew": 4, "vehicles": 4},    0.12 arrival rate and 4 crews, 4 vehicles (more arrivals but more resources)
    {"run_id": 7, "arrival_rate": 0.0833, "gates": 5, "crew": 2, "vehicles": 2},    5 gates
    {"run_id": 8, "arrival_rate": 0.0833, "gates": 3, "crew": 2, "vehicles": 2},    3 gates
    {"run_id": 9, "arrival_rate": 0.15,   "gates": 6, "crew": 4, "vehicles": 4},    0.15 arrival rate, 6 gates, 4 crews, 4 vehicles (more everything)
    {"run_id": 10,"arrival_rate": 0.05,   "gates": 4, "crew": 1, "vehicles": 1}     0.05 arrival rate, 1 crew, 1 vehicle (less arrivals but less resources)