from enum import Enum
from numpy import sqrt

from main import Pathfinder
from AGV import Order, Order_State

class Agent_State(Enum):
    _Done = 0
    _Picking = 1
    _Delivering = 2
    _Meeting = 3 
    _Waiting = 4 
    _DeliveringCollab = 5 

class Agent:

    def __init__(self, agentId, map, position):
        self.agentId = agentId
        self.map = map
        self.pickupStation = position
        self.deliveryStation = position
        self.meetingPoint = position 
        self.startingPosition = position # Return here after orders are finished
        self.position = position
        self.stepsHistory = []
        self.state = Agent_State._Done
        self.order_switchcount = 0
        self.order_log = []
        self.order = None
        self.goal = position
        self.Collaborating = False
        self.collab_order = None 
        self.Picker = False 
        self.Deliverer = False 

        self.Met = False # The robots have not met, the class pair will take care of it 
        self.pathfinder = Pathfinder()

        # temp_dict = {"x": self.position[0], "y": self.position[1], "t": 0}
        # self.stepsHistory.append(temp_dict)

    def resetCollab(self):
        self.Collaborating= False
        self.collab_order = None 
        self.Picker = False 
        self.Deliverer = False 

    def setCollab_state(self, ctrl, order): # ADDED   ---
        self.Collaborating = True 
        if ctrl == 1: 
            print("picker agent", self.agentId)
            self.Picker = True 
            self.collab_order = None 
            self.Deliverer = False 
        elif ctrl == 0: 
            print("Deliverer agent", self.agentId)

            self.Deliverer = True 
            self.Picker = False 
            self.setCollabOrder(order)  # state of agent not changed 
            print("Deliverer state ",self.state)


    def getPosition(self):
        return self.position

    def getId(self):
        return self.agentId

    def getOrder(self):
        return self.order

    # Get the state of the Agent
    def getState(self):
        return self.state

    # Get the step history of the Agent
    def getStepsHistory(self):
        return self.stepsHistory

    # Check agent state by checking the order state TODO normally check state the other way agent --> order
    def update_agent_state(self, newState):
        print(newState, "new state into update agent state function")
        if self.order == None and self.Deliverer == False and self.Picker == False:  # this oooneeeee 
            return
        elif newState == 0:# "_Done"
            self.state = Agent_State._Done
            self.goal = self.startingPosition
            #print("self.startingPosition14", self.goal)
        elif newState == 1:# "_Picking"
            self.order_switchcount += 1
            self.order_log.append(self.order.id_code)
            self.state = Agent_State._Picking
            self.goal = self.order.get_objective()
            #print("self.pickupStation24", self.goal)
        elif newState == 2:# "_Delivering"
            self.state = Agent_State._Delivering
            self.goal = self.order.get_objective()
            #print("self.deliveryStation.coordinate34", self.goal)
        
        elif newState == 3 and self.Deliverer == True: # differentiate between agent ref and agent 2 
            print("new state for deliverer agent")
            self.state = Agent_State._Meeting
            print(self.state)
            print(self.collab_order)
            self.goal = self.collab_order.get_objective() #-- Add coordinate of meeting point, how ??    # change it 
        
        elif newState == 3 and self.Picker == True:
            print("new state for picker agent ")
            self.state = Agent_State._Meeting
            goal = self.order.get_objective()
            print("new goal",goal)
            goal = list(goal)
            goal[0] = goal[0]-1 # ** this is needed otherwise the two robots would have the same coordinates as goal and therefore would never meet 
            goal = tuple(goal)
            print("new goal manipulated", goal)
            self.goal = goal

        elif newState == 4:  # stays where it is until the other robot has arrived 
            self.state = Agent_State._Waiting
            self.goal = self.position 
         
        elif newState == 5: # delivering collaborative order 
            self.state = Agent_State._DeliveringCollab
            self.goal = self.order.get_objective()
            

    def pick_order(self, timestep):
        self.order.set_order_state(2)
        self.order.timestep_pick = timestep
        self.update_agent_state(2)
        
        #print("Order ", self.order.id_code , " picked by agent", self.agentId, ". New Goal: ", self.goal)

    def deliver_order(self, timestep):
        self.order.set_order_state(3)
        self.order.timestep_end = timestep
        self.update_agent_state(0)
        #print("Order ", self.order.id_code , " delivered by agent", self.agentId)

    def Meet(self, timestep):
        self.order.set_order_state(4) 
        self.order.timestep_middle = timestep
        self.update_agent_state(3)

    def setOrder(self, order, timestep, ID):
        self.order = order
        self.pickupStation = order.pickupStation
        self.order.assign_order(self.agentId, timestep, self.position)
        #self.order.set_order_state(1)
        self.update_agent_state(1)

    
    def switch_order(self, timestep):
        if self.Deliverer: 
            self.order = self.collab_order
            self.order.assign_order(self.agentId, timestep, self.order.getMeetingPoint())
            self.update_agent_state(5)
            self.Met = True

        elif self.Picker: 
            self.order.deAssign_order()
            self.update_agent_state(0)
            self.Met = True

    def setCollabOrder(self, order): 
        print("collab order function entered ")
        self.collab_order = order
        self.meetingPoint = order.meetingPoint
        print(self.Picker, "self.picker")
        print(self.Deliverer, "self.deliverer" )
        self.update_agent_state(3)
        print("agent state to be updated ")
        self.goal = order.getMeetingPoint()  # function in order to retrieve meeting point ?

    '''   *** FUNCTION NEEDS TO BE SPLIT -- ONE FUNCTION FOR DELIVERING AND ONE FUNCTION FOR ASSIGNING THE ORDER DEPENDENT OF THE PAIR CLASS 

    def DeliverAfterMeet(self, order, timestep, ID): # function for second paired robot 
        self.order = order
        self.deliveryStation = order.deliveryStation
        self.order.assign_order(self.agentId, timestep, self.position)
        #self.order.set_order_state(1)
        self.update_agent_state(2)
    '''

    def pick_order_collab(self, timestep):
        self.order.set_order_state(2)
        self.order.timestep_pick = timestep
        self.update_agent_state(3)

    def deliver_CollaBorder(self):
        self.order.set_order_state(2)
        self.update_agent_state(5)


    ''' ORDER ASSIGNATION SWITCHING TO BE IMPLEMENTED IN THE PAIR CLASS 
    def GoToMeetingPoint(self, order, timestep, ID): # function for second paired robot 
        self.order = order 
        self.meetingPoint= order.meetingPoint
        self.order.assign_order(self.agentId, timestep, self.position)
        self.update_agent_state(3)
    '''

    def setNewOrder(self, order, timestep, ID):
        '''
        eCNP: Agent accepts new order, and removes the old one
        '''
        self.order.deAssign_order()
        self.setOrder(order, timestep, ID)

    def makesMove(self, timestep, map):   # function which does the magicccc 
        if self.Collaborating == True:
            print("----------------------------***************")
            print("agent Id", self.agentId)
            print("state of the agent", self.state)
            print("Picker", self.Picker)
            print("Deliverer", self.Deliverer)
        
            if self.order != None:
                print("order", self.order.getOrderId())
        
            print("Agents Met ?", self.Met)
            print("----------------------------***************")

        if self.state == Agent_State._Done and self.position == self.goal:
            print("DONE HERE",self.state, Agent_State._Done)
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            return self.position
        elif self.state == Agent_State._Picking and self.position == self.goal and self.Picker == False and self.Collaborating == False:# Picks up good for order
            print("PICKING HERE",self.state, Agent_State._Picking)
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            self.pick_order(timestep) # it' s ittttt  TODO 
            return self.position
        elif self.state == Agent_State._Delivering and self.position == self.goal and self.Collaborating == False:# Delivers good
            print("DELIVERING HERE",self.state, Agent_State._Delivering)
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            self.deliver_order(timestep)
            return self.position
        
        # Non collaborative actions   above 

        # meet at meeting point in the middle AND COLLABORATIVE ORDER 
        # Picker robot waits for the deliverer 

        elif self.state == Agent_State._Meeting and self.position == self.goal and self.Collaborating and self.Picker and self.Met == False : 
            print("MEETING HERE Picker agent, waiting ",self.state, Agent_State._Meeting )
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            self.update_agent_state(4)  # drops the package in the meeting point and waits for 

            return self.position  # CHANGED 

        

        # waiting elif for deliverer 
        elif self.state == Agent_State._Meeting and self.position == self.goal and self.Collaborating and self.Deliverer and self.Met == False: 
            print("MEETING HERE Deliverer agent, waiting ",self.state, Agent_State._Meeting )
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            self.update_agent_state(4)  # drops the package in the meeting point and waits for 

            return self.position  # CHANGED 



        # Deliverer robot goes back to init position once it has reached its destination 
        elif self.state == Agent_State._DeliveringCollab and self.position == self.goal and self.Collaborating and self.Deliverer and self.Met == True: 
            print("ORDER DELIVERED BY Deliverer agent ",self.state, Agent_State._Meeting )
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            #self.Met = False # reset as order is delivered 
            self.deliver_order(timestep)  # action to deliver order 
            #self.resetCollab()
            return self.position  # CHANGED 

        elif self.state == Agent_State._Picking and self.position == self.goal and self.Collaborating and self.Picker:
            print("PICKING HERE COLLAB",self.state, Agent_State._Picking)
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            self.pick_order_collab(timestep) # it' s ittttt  TODO 
            return self.position
        
        #  - deliverer robot goes from _Meeting to _DeliveringCollab and becomes main robot of order assignation ( we need a new external function for that , function similar to the one at line 130)
    
        elif self.state == Agent_State._Meeting and self.position == self.goal and self.Collaborating and self.Deliverer and self.Met == True: # meet at meeting point in the middle AND COLLABORATIVE ORDER 
            print("MEETING HERE Deliverer robot, waiting",self.state, Agent_State._Meeting )
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            self.deliver_CollaBorder()  # New state -- 5 delivery for collaboration  
            return self.position  # CHANGED 

            # come back to base 
        elif self.state == Agent_State._Waiting and self.position == self.goal and self.Collaborating and self.Picker and self.Met == True:
            print("MET HERE WITH PAIR ROBOT DONE, COMING BACK TO INIT POS",self.state, Agent_State._Meeting, self.position )
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            self.Met = False # reset it for the next collaborative iteration
            #self.resetCollab()
            self.update_agent_state(0)  # New state -- 5 delivery for collaboration  
            return self.position  # CHANGE





        # Find next step
        #print("self.goal)", self.goal)
        x, y = self.pathfinder.solve(self.agentId ,map.copy(), self.position, self.goal)

        self.position = (x, y)
        #self.state = Agent_State._Active

        # Save steps for visualization
        temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
        self.stepsHistory.append(temp_dict)

        #print("End of MakesMove:", self.position)
        return self.position



# TODO 

'''
1] Implement the new elif statements for the collaborative robots  in line 159 

The statements needed are: 
                        - Waiting for the deliverer at the meeting point - DONE 
                        - Deliverer robot goes back to init position once it has reached its destination - DONE
                        - deliverer robot goes from _Meeting to _DeliveringCollab and becomes main robot of order assignation ( we need a new external function for that , function similar to the one at line 130)


2] create the implementation of new state _DeliveringCollab -- line 84 - DONE 

Similarly to state 2 its goal is the delivery station but in addition it becomes the main robot of assignation when it comes to the order -- 

- in class pair 

when both robots state == waiting then deliverer becomes main assignatory of order (order switch from robot 1 to robot 2) and then -->
                                                                                                                        - Deliverer.state = _DeliveringCollab -- goes to delivery station DONE
                                                                                                                        - Picker.state = done -- goes back to init pos. DONE
'''

class Pair_State(Enum):
    _Available = 0
    _Busy = 1

class Pair():  # the purpose is to make sure that once on of the agents has reached the meeting point it waits until the other arrives for the next step. and order gets passed from one agent to the other 

    def __init__(self, Id):
        self.Id = Id 
        self.agent1 = None  # picker 
        self.agent2 = None # deliverer 
        self.order = None 
        self.state = Pair_State._Available
        self.pairLog = []  # history of the pair for analizing it later. 

    def getCoordinate(self): #TODO
        return self.agent1.getPosition(), self.agent2.getPosition()

    def agents_met(self, timestep):

        if self.agent1 != None and self.agent2 != None:
            if self.agent1.getState() == Agent_State._Waiting and self.agent2.getState() == Agent_State._Waiting:
                self.agent1.switch_order(timestep)
                self.agent2.switch_order(timestep)

                self.update_pair_state(0)

    def assign_agents(self, agent1, agent2, order, timestep):
        print("pair assignment called")
        if self.state == Pair_State._Available:
            self.agent1 = agent1 
            print(self.agent1.getId())
            self.agent2 = agent2 
            print(self.agent2.getId())

            self.order = order 
            print(self.order.getOrderId())
            self.update_pair_state(1)

    def getId(self):
        return self.Id

    def getState(self):
        return self.state

    def free_pair(self):
        self.agent1 = None 
        self.agent2 = None
        self.order = None

    def update_pair_state(self, NewState): 
        if NewState == 0: 
            self.free_pair()
            self.state = Pair_State._Available
        elif NewState == 1: 
            self.state = Pair_State._Busy


    def MakesMove(self, timestep):  # function which is called in loop -- need to be sum all functionalities in here 
        self.agents_met(timestep)

