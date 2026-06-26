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

