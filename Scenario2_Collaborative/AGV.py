from enum import Enum
from numpy import sqrt

class Order_State(Enum):
    _Not_Assigned = 0
    _Assigned = 1
    _Picked  = 2
    _Delivered = 3

class Order:
    current_objective = ()

    def __init__(self, deliveryStation, pickupStation, meetingPoint, requested_quantities, timestep_begin, id_code, state=0):
        self.id_code = id_code
        self.agent_assigned = None
        self.agent_in_charge = None 
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
        self.agent_assigned_Picker = None 
        self.agent_assigned_Deliverer = None

    def assign_order(self, agentId,timestep, agent_pos, Deliverer, Picker): # modify it so that it can assigned to 2 ? 
        if Deliverer == False: 
            self.agent_assigned_Deliverer = False
            self.agentId = agentId
            self.state = 1 # picking -- 
            self.timestep_of_assignment = timestep
            self.agent_pos = agent_pos

        elif Deliverer == True:
            self.agent_assigned_Deliverer = True 
            self.agentId = agentId
            self.state = 2 # delivering -- 
            self.timestep_of_assignment = timestep
            self.agent_pos = agent_pos


    def deAssign_order(self):
        
        self.agentId = None
        self.state = 0
        self.timestep_of_assignment = None
        self.agent_assigned_Deliverer = None 
        self.agent_assigned_Picker = None

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

    def assign_picker_agent(self, PickerVal):
        self.agent_assigned_Picker = PickerVal


    def get_objective(self):  # Add optional argument 
        
        if self.agent_assigned_Deliverer != None: 
            print("deliverer agent order ", self.agent_assigned_Deliverer)

        if self.agent_assigned_Picker != None: 
            print("picker agent order", self.agent_assigned_Picker)
        

        if self.agent_assigned_Deliverer == None and self.agent_assigned_Picker == None:
            print("agent neither deliverer neither picker but values not set to FALSE but to NONE")

        if self.state == 1:
            return self.pickupStation
        elif self.state == 2 and self.agent_assigned_Picker == False and self.agent_assigned_Deliverer == False:
            return self.deliveryStation
        elif self.state == 3: 
            return False  # agent is done here : --- 
        elif self.state == 2 and self.agent_assigned_Picker == True:
            return self.meetingPoint
        elif self.state == 2 and self.agent_assigned_Deliverer == True: 
            return self.deliveryStation
        else:
            print("exit() in order get_objective")
            print("self state of the order", self.state)
            exit()
            return None


        # _Not_Assigned = 0
        # _Assigned = 1
        # _Picked  = 2
        # _Delivered = 3
        # _Meeting = 4 