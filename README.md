# Multi-agent warehouse order sorting 

This project consists in the development of a distributed system where a multi-agent order sorting in a simulated warehouse is presented. 
The project is divided into 2 scenarios. 
- Multi-agent non collaborative 
- Multi-agent collaborative 

In the first case the agents are assigned the orders based on a distance optimized bid carried out by the master node (environment layer). 

In the second case the agents are assigned orders randomly and based on distance constraints another agent to collaborate with is paired with it. 

For both scenarios the library tcod is used to calculate through the **A** **star** algorithm the shortest path from its position to the current goal

### Commands

To easily execute the program follow these 4 steps:

1. Install dependency: `python3 -m pip install --user tcod`
2. Execute simulation: `python3 environment.py`
3. Execute visualization: `python3 visualize.py`
4. Execute both: `python3 environment.py && python3 visualize.py`

----------
## Scenario 1: non collaborative multi-agent delivery 

After an agent gets an order from the master node of the system, it retrieves the coordinates of the order pick up station directly from the order layer. 
Similarly once the agent reaches the pick up station it receives the coordinates of the delivery station, its new goal. 
Finally once the order is delivered the agent goes back to its initial position if no order orders need to be sorted. 

- blue = pickup stations 
- yellow = delivery stations
- red = obstacles 


https://user-images.githubusercontent.com/101090050/164981122-a18348d7-4a82-4fa0-b542-797332762318.mp4


-----------

## Scenario 2: collaborative multi-agent delivery

A similar logic is compared to scenario 1 is employed. Let's differentiate. 

In this scenario the order assigned to an agent can be: 

- collaborative 
- non collaborative 

For the non collaborative case the exact same logic as for scenario 1 is used. 

#### Collaborative order 
The agent can either be: 

1. Picker 
2. Deliverer

##### Picker

the agent is main assignatory of the order. its steps are: 

1. navigate to pick up station 
2. reach meeting point and meet with Deliverer
3. order gets deassigned from it and passed to Deliverer 
4. goes back to init position or gets assigned a new order or assist another agent in a collab order 


##### Deliverer 

Auxiliary agent to the main assignatory. its steps are: 


1. receives coordinates of meeting point 
2. reach meeting point and circle around it waiting for the Picker 
3. receive order from Picker 
4. receive corodinates of delivery station from order layer 
5. deliver order 
6. goes back to init position or gets assigned a new order or assist another agent in a collab order 

- blue = pickup stations 
- yellow = delivery stations
- red = obstacles 
- green = meeting points 


https://user-images.githubusercontent.com/101090050/173695695-16ee0691-7a35-4a3d-b834-073b317f350e.mp4

