# Swarm-robots-warehouse

This project consists in the development of a distributed system where a multi-agent order sorting in a simulated warehouse is presented. 
The project is divided into 2 scenarios. 
- Multi-agent non collaborative 
- Multi-agent collaborative 

In the first case the agents are assigned the orders based on a distance optimized bid carried out by the master node (environment layer) 
In the second case the agents are assigned orders randomly and based on distance constraints another agent to collaborate with is paired with it. 

### Commands

To easily execute the program follow these 4 steps:

1. Install dependency: `python3 -m pip install --user tcod`
2. Execute simulation: `python3 environment.py`
3. Execute visualization: `python3 visualize.py`
4. Execute both: python3 `environment.py && python3 visualize.py`


## Scenario 1: non collaborative multi-agent delivery 

- blue = pickup stations 
- yellow = delivery stations
- red = obstacles 



https://user-images.githubusercontent.com/101090050/164981122-a18348d7-4a82-4fa0-b542-797332762318.mp4



## Scenario 2: collaborative multi-agent delivery

- blue = pickup stations 
- yellow = delivery stations
- red = obstacles 
- green = meeting points 


https://user-images.githubusercontent.com/101090050/173695695-16ee0691-7a35-4a3d-b834-073b317f350e.mp4

