from enum import Enum
from numpy import sqrt


'''
This class is used for updating the order state

'''

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
        self.agent_pos = None 
        self.timestep_pick = None
        self.timestep_end = None
        self.timestep_middle = None 
        self.state = state
        self.agentId = None
        self.timestep_of_assignment = None 
        self.agent_assigned_Picker = None 
        self.agent_assigned_Deliverer = None



    '''
    function used to assign the order: 
    in case the agent is a delivery agent of a collaborative order then the order state is automatically kept to 2 
    otherwise to 1 as it still needs to be delivered 
    '''
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


    '''
    De assignment of order. For simplicity it is assumed that in case an agent has picked the order and then it gets de assigned the 
    order is automatically agin in the pick up station
    '''
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



    '''
    Main function used by the agent layer to update its objective and the order state. 

    From here it can retrieve the new coordinates of the new goal positions connected to the order (pick up ,meeting & Delivery point  )
    
    output: coordinates of new goal 
    '''
    def get_objective(self):  
        
        '''  DEBUGGING 
        if self.agent_assigned_Deliverer != None: 
            print("deliverer agent order ", self.agent_assigned_Deliverer)

        if self.agent_assigned_Picker != None: 
            print("picker agent order", self.agent_assigned_Picker)
        

        if self.agent_assigned_Deliverer == None and self.agent_assigned_Picker == None:
            print("agent neither deliverer neither picker but values not set to FALSE but to NONE")
        '''

        if self.state == 1:
            return self.pickupStation
        elif self.state == 2 and self.agent_assigned_Picker == False and self.agent_assigned_Deliverer == False:
            return self.deliveryStation
        elif self.state == 3: 
            return False  # agent is done here : gets assigned new order or goes to initial position 
        elif self.state == 2 and self.agent_assigned_Picker == True:
            return self.meetingPoint
        elif self.state == 2 and self.agent_assigned_Deliverer == True: 
            return self.deliveryStation
        else:
            print("exit() in order get_objective")
            print("self state of the order", self.state)
            exit()
            return None

