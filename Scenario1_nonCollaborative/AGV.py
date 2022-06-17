from enum import Enum
from numpy import sqrt



class Order_State(Enum):
    _Not_Assigned = 0
    _Assigned = 1
    _Picked  = 2
    _Delivered = 3


'''
An object of class order is created by the environment layer following the data in the input file for each of the orders present 
in the input file 
'''

class Order:
    #current_objective = ()

    '''
    Inputs: 
     - coordinates of the delivery station 
     - coordinates of the pick up station 
     - coordinates of the meeting point 
     - quantities of the order needed to sort 
     - timestep of initialization 
    '''

    def __init__(self, deliveryStation, pickupStation, requested_quantities, timestep_begin, id_code, state=0):
        self.id_code = id_code
        self.agent_assigned = None
        self.pickupStation = pickupStation
        self.deliveryStation = deliveryStation
        self.distance = sqrt((pickupStation[0] - deliveryStation[0])**2 + (pickupStation[1] - deliveryStation[1])**2)
        self.requested_quantities = requested_quantities
        self.timestep_begin = timestep_begin
        self.agent_pos = None #agent_pos_at_timestep_pick
        self.timestep_pick = None
        self.timestep_end = None
        self.state = state
        self.agentId = None
        self.timestep_of_assignment = None


    '''
    function used to assign the order: 
    register where the agent is and change the order state to assigned 
    '''

    def assign_order(self, agentId, timestep, agent_pos):
        self.agentId = agentId
        self.state = 1
        self.timestep_of_assignment = timestep
        self.agent_pos = agent_pos


    def getTimestep_begin(self):
        return self.timestep_begin

    def getAgentId(self):
        return self.agentId

    def getOrderId(self):
        return self.id_code

    def get_order_state(self):
        return self.state

    def set_order_state(self, state):
        self.state = state

    def getPickupStation(self):
        return self.pickupStation

    def getDeliveryStation(self):
        return self.deliveryStation

    def get_objective(self):
        if self.state == 1:
            return self.pickupStation
        elif self.state == 2:
            return self.deliveryStation
        else:
            print("exit() in order get_objective")
            exit()
            return None
