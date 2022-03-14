import random
from enum import Enum

from numpy import sqrt
from main import Pathfinder

class Order_State(Enum):
    _Not_Assigned = 0
    _Received = 1
    _Picked  = 2
    _Delivered = 3


class Agent_State(Enum):
    _Off = 0
    _Active = 1
    _Shipping = 2
    _Done = 3
    _Out_of_Order = 4

class Pair_state(Enum):  # treat the pair of agents as a 'special' case of agents 
    _Off = 0
    _Active = 1 
    _Met = 2 
    _Shipping = 3 
    _Done = 4 
    _Out_of_Order = 5 


class Order:
    current_objective = []

    def __init__(self, deliveryStation, pickupStation, requested_quantities, timestep_begin, id_code, state=0):
        self.id_code = id_code
        self.agent_assigned = None
        self.pickupStation = pickupStation
        self.deliveryStation = deliveryStation

        self.distance = sqrt((pickupStation[0][0] - deliveryStation.coordinate[0][0])**2 + (pickupStation[0][1] - deliveryStation.coordinate[0][1])**2)
        self.requested_quantities = requested_quantities
        self.timestep_begin = timestep_begin
        self.timestep_pick = None
        self.timestep_end = None
        self.state = state

    def assign_order(self, agentId, timestep, pickup):
        self.agentId = agentId
        #self.pickupStation = pickup
        self.state = 1
        self.timestep_of_assignment = timestep

    def update_order_state(self, New_State):
        self.state = New_State

    def get_order_state(self):
        return self.state

    # Picks randomly a requested good and set it as first objective
    def get_objective(self):
        for i in range(len(self.requested_quantities)):
            if self.requested_quantities[i] > 0:
                self.current_objective = self.pickupStation
                return self.current_objective
        self.state = 1
        return None

###################################################################################


# TODO: build it similarly as the Agent 

class pair:
    def __init__(self): 
        self.initialized = True 


#####################################################################################

# TODO Agent can get an order
# TODO Agent can carry certain amount of goods
# TOOD Agent needs to save every step for visualization later on
# Agent can take only one item TODO extend agent capacity
class Agent:

    def __init__(self, agentId, map, deliveryStation, currentPosition, max_storage=3):
        self.agentId = agentId
        self.map = map
        self.pickupStation = currentPosition
        self.deliveryStation = deliveryStation
        #self.currentGoal
        self.currentPosition = currentPosition
        self.startingPosition = currentPosition # Return here after orders are finished
        self.stepsHistory = []
        self.state = Agent_State._Off
        self.order = None
        self.max_storage=3
        #self.storage = [0] * len(self.pickupStation.coordinate)

        self.currentGoal = currentPosition

    def setCurrentPosition(self, currentPosition):
        self.currentPosition = currentPosition

    def getCurrentPosition(self):
        return self.currentPosition

    def setOrder(self, order, timestep, ID):
        self.order = order
        self.pickupStation = order.pickupStation
        self.order.assign_order(self.agentId, timestep, order.pickupStation)
        self.state = Agent_State._Active
        self.order.update_order_state(1)
        self.currentGoal = self.order.get_objective()
        print("Agent", ID,": Order ", order.id_code, " received at timestep ", timestep, " by agent ", self.agentId)

    def getOrder(self):
        return self.order

    # Get the state of the Agent
    def getState(self):
        return self.state

    # Get the step history  of the Agent
    def getStepsHistory(self):
        return self.stepsHistory

    # Check agent state by checking the order state TODO normally check state the other way agent --> order
    def update_agent_state(self):

        ''' class Order_State(Enum):
            _Not_Assigned = 0
            _Received = 1
            _Picked  = 2
            _Delivered = 3


        class Agent_State(Enum):
            _Off = 0
            _Active = 1
            _Shipping = 2
            _Done = 3
            _Out_of_Order = 4 '''

        if self.order == None:
            return
        elif self.order.state == 0:# "_Not_Assigned"
            self.state = Agent_State._Off
            self.currentGoal = self.startingPosition
        elif self.order.state == 1:# "_Received"
            self.state = Agent_State._Active
            self.currentGoal = self.pickupStation
        elif self.order.state == 2:# "_Picked"
            self.state = Agent_State._Shipping
            self.currentGoal = self.deliveryStation.coordinate
        elif self.order.get_order_state() == 3:# "_Delivered"
            self.state = Agent_State._Done
            self.currentGoal = self.startingPosition



    # # Agent Pick an order item from the Pickupsation A :
    def pick_order(self):
        self.order.update_order_state(2)
        print("Order ", self.order.id_code , " picked by agent", self.agentId)
        self.update_agent_state()


    # Agent delivers an order to the DeliveryStation B :
    def deliver_order(self):
        self.order.update_order_state(3)
        print("Order ", self.order.id_code , " delivered by agent", self.agentId)
        self.update_agent_state()

    def go_idle(self):
        self.order.update_order_state(0)
        self.update_agent_state()

    # check if agent is still in the Map
    def is_in_map(self, x, y):
        return (x >= 0) and (x < self.map.shape[0]) and \
               (y >= 0) and (y < self.map.shape[0])

    # Avoid obstacles
    #def no_obstacle(self, x, y):
    #    return self.map[x][y] != "*"

    # Avoid other agents
    def no_agent(self, x, y):
        if isinstance(self.map[x][y], int):
            return True
        elif "A" in self.map[x][y]:
            return False
        else:
            return True

    # Makes random moves. TODO It should at least move into the right direction
    def makesMove(self, timestep):

        if self.state == Agent_State._Off:
            return self.currentPosition

        #TODO This needs to be the right goal, derived from order, from location of delivery station or when returing back to starting position

        ''' class Order_State(Enum):
            _Not_Assigned = 0
            _Received = 1
            _Picked  = 2
            _Delivered = 3


        class Agent_State(Enum):
            _Off = 0
            _Active = 1
            _Shipping = 2
            _Done = 3
            _Out_of_Order = 4 '''


        # Find next step
        for i in range(20):

            x = self.currentPosition[0]
            y = self.currentPosition[1]

            pathfinder = Pathfinder()

            #format check
            if len(self.currentGoal) <2:
                self.currentGoal = self.currentGoal[0]

            if i == 0 and pathfinder.solve(self.agentId ,self.map.copy(), self.currentPosition, self.currentGoal):
                x, y = pathfinder.getNextMove()
            else:
                if random.randint(0, 1) == 1:
                    if random.randint(0, 1) == 1:
                        x = x + 1
                    else:
                        x = x - 1
                else:
                    if random.randint(0, 1) == 1:
                        y = y + 1
                    else:
                        y = y - 1

            # Check if move is possible. TODO Check if position is same as before
            if self.is_in_map(x,y)  and self.no_agent(x,y):  # and self.no_obstacle(x,y)
                self.currentPosition = [x, y]
                self.state = Agent_State._Active
                break

        # Save steps for visualization
        temp_dict = {"x": self.currentPosition[0], "y": self.currentPosition[1], "t": timestep}
        self.stepsHistory.append(temp_dict)

        return self.currentPosition
