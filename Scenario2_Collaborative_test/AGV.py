from enum import Enum
from numpy import sqrt



class Order_State(Enum):
    _Not_Assigned = 0
    _Assigned = 1
    _Picked  = 2
    _Delivered = 3
    _Meeting = 4 # changed 

class Order:
    current_objective = ()

    def __init__(self, deliveryStation, pickupStation, meetingPoint, requested_quantities, timestep_begin, id_code, state=0):
        self.id_code = id_code
        self.agent_assigned = None
        self.pickupStation = pickupStation
        self.deliveryStation = deliveryStation
        self.meetingPoint = meetingPoint
        self.distance = sqrt((pickupStation[0] - deliveryStation[0])**2 + (pickupStation[1] - deliveryStation[1])**2)
        self.distAG1 = sqrt((pickupStation[0] - meetingPoint[0])**2 + (pickupStation[1] - meetingPoint[1])**2)
        self.distAG2 = sqrt((deliveryStation[0] - meetingPoint[0])**2 + (deliveryStation[1] - meetingPoint[1])**2)
        self.requested_quantities = requested_quantities
        self.timestep_begin = timestep_begin
        self.agent_pos = None #agent_pos_at_timestep_pick
        self.timestep_pick = None
        self.timestep_end = None
        self.timestep_middle = None # changed 
        self.state = state
        self.agentId = None
        self.timestep_of_assignment = None # changed -- added as additional parameters the second agent 
        
        self.collaborativeOrder = False 
        self.agent2_Id = None 

    def assign_order(self, agentId, timestep, agent_pos): # modify it so that it can assigned to 2 ? 
        self.agentId = agentId
        self.state = 1 # picking -- 
        self.timestep_of_assignment = timestep
        self.agent_pos = agent_pos

    def assign_orderCollab_Delivery(self, agentId, timestep, agent_pos):
        self.agentId = agentId
        self.state = 2 # delivering 
        self.timestep_of_assignment = timestep 
        self.agent_pos = agent_pos 

        
    def switch_order(self, agent1ID, agent2ID, timestep, agent1_pos, agent2_pos):
        
        current_agentID = self.agentId

        if current_agentID == agent1ID:
            self.assign_order(self, agent2ID, timestep, agent2_pos)
        elif current_agentID == agent2ID:
            self.assign_order(self, agent1ID, timestep, agent1_pos)


    def collaborative_order(self, agentId, agent2Id, timestep, agent_pos, meetingPoint):
        return

    def deAssign_order(self):
        
        '''
        Used for eCNP to remove assignment of order.
        '''
        self.agentId = None
        self.state = 0
        self.timestep_of_assignment = None

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

    def getMeetingPoint(self):
        return self.meetingPoint


    def get_objective(self, collabGoal = None):  # Add optional argument 
        if self.state == 1:
            return self.pickupStation
        elif self.state == 2:
            return self.deliveryStation
        elif self.state == 3: 
            return self.meetingPoint
        #elif self.state 
        else:
            print("exit() in order get_objective")
            exit()
            return None
