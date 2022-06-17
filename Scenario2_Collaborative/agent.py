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

'''
The agent layer is one of the two main ones together with the environment. 
a number of Agent objects is created by the environment once it reads the configuration file. 

Based on the information of the input file each agent can be initialized with 

- a unique id 
- a unique position in the map 
'''

class Agent:

    def __init__(self, agentId, map, position):
        self.agentId = agentId
        self.map = map
        self.pickupStation = position  # initialize them with the current position of the agent 
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

        self.Collaborating = False  # used to know if the agent is collaborating or not 
        self.collab_order = None    # initialized only if agent is deliverer 
        self.Picker = False 
        self.Deliverer = False 
        self.Met = False # The robots have not met, the class pair will take care of it 

        self.pathfinder = Pathfinder()

        # temp_dict = {"x": self.position[0], "y": self.position[1], "t": 0}
        # self.stepsHistory.append(temp_dict)


    '''
    After an agent has finished a collaborative order this function takes care of the de-initialization of the control
    variables used at the various stages of the collaboration 
    '''
    def resetCollab(self):
        self.Collaborating= False
        self.collab_order = None 
        self.Picker = False 
        self.Deliverer = False 


    '''
    This function is called by the environment layer after a collaborative order has been assigned to an agent.
    
    Inputs: 
    - ctrl (either equal 1 or 0)  1 --> Agent is Picker | 0 --> Agent is Deliverer 
    - order 


    '''
    def setCollab_state(self, ctrl, order): # ADDED   ---
        self.Collaborating = True 
        if ctrl == 1: 
            print("picker agent", self.agentId)
            self.Picker = True 
            self.collab_order = None 
            self.Deliverer = False 
            order.assign_picker_agent(True)
        elif ctrl == 0: 
            print("Deliverer agent", self.agentId)

            self.Deliverer = True 
            self.Picker = False 
            self.setCollabOrder(order)  # state of agent not changed 
            print("Deliverer state ",self.state)


    # Get the agent current position 
    def getPosition(self):
        return self.position

    # Get the agent Id 
    def getId(self):
        return self.agentId

    # Get the current order of the Agent 
    def getOrder(self):
        return self.order

    # Get the state of the Agent
    def getState(self):
        return self.state

    # Get the step history of the Agent
    def getStepsHistory(self):
        return self.stepsHistory

    '''
    Main function responsible for updating the agent state and goal. The function is called by the self.MakesMove function 
    when the agent has reached a goal or when an order is assigned. either collaborative or not. 

    Input: the value of the new state corresponding to the AGENT_STATE 
    '''
    def update_agent_state(self, newState):

        ''' DEBUGGING
        print(newState, "new state into update agent state function")
        print("agent is Picker ?", self.Picker, "agent is Deliverer ?", self.Deliverer)
        if self.order != None:
            print("order state ", self.order.get_order_state())
        '''


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

            if self.order.get_objective == False:  # Agent has finished to deliver the order 
                self.goal = self.startingPosition 
            else:
                self.goal = self.order.get_objective()
            #print("self.pickupStation24", self.goal)
        elif newState == 2:# "_Delivering"
            self.state = Agent_State._Delivering

            if self.order.get_objective == False:
                self.goal = self.startingPosition 
            else:
                self.goal = self.order.get_objective()
            print(self.order.get_order_state())
            #print("self.deliveryStation.coordinate34", self.goal)
        
        elif newState == 3 and self.Deliverer == True: # _Meeting 
            print("new state for deliverer agent")
            self.state = Agent_State._Meeting
            print(self.state)
            print(self.collab_order)

            if self.collab_order.get_objective == False:
                self.goal = self.startingPosition # check it if it gives the right objective 
            else:
                self.goal = self.collab_order.get_objective()# Meeting point coordinates  
        
        elif newState == 3 and self.Picker == True: # _Meeting 
            print("new state for picker agent ")
            self.state = Agent_State._Meeting
            if self.order.get_objective == False:
                self.goal = self.startingPosition
                return # check it if it gives the right objective 
            else:
                goal = self.order.get_objective()  # TODO: check it 
            print("new goal", goal)
            goal = list(goal)
            goal[0] = goal[0]-1 # ** this is needed otherwise the two robots would have the same coordinates as goal and therefore would never meet 
            goal = tuple(goal)
            print("new goal manipulated", goal)
            self.goal = goal

        elif newState == 4:  # _Waiting - stays where it is until the other robot has arrived 
            self.state = Agent_State._Waiting
            self.goal = self.position 
         
        elif newState == 5: # delivering collaborative order 
            self.state = Agent_State._DeliveringCollab
            self.order.set_order_state(2) 
            if self.order.get_objective == False:
                self.goal = self.startingPosition # check it if it gives the right objective 
            else:
                self.goal = self.order.get_objective()


    '''
    When the agent has reached the pick up point this function has the goal to update the agent state and communicate with the order
    layer the pick up the order by changing the order state  and registering the time-step of pick up 
    '''
    def pick_order(self, timestep):
        self.order.set_order_state(2)
        self.order.timestep_pick = timestep
        self.update_agent_state(2)
        
        #print("Order ", self.order.id_code , " picked by agent", self.agentId, ". New Goal: ", self.goal)


    '''
    When the agent has reached the Delivery point this function has the goal to update the agent state and communicate with the order
    layer the Delivery the order by changing the order state  and registering the time-step of the Delivery
    '''
    def deliver_order(self, timestep):
        self.order.set_order_state(3)
        self.order.timestep_end = timestep
        self.update_agent_state(0)
        #print("Order ", self.order.id_code , " delivered by agent", self.agentId)

    '''
    Whenever an order has been awarded to the agent from the environment layer this function is called. 
    It is mostly used when the order is non collaborative 
    
    '''

    def setOrder(self, order, timestep, ID):
        self.order = order
        self.pickupStation = order.pickupStation
        self.order.assign_order(self.agentId, timestep, self.position, self.Deliverer, self.Picker)  
        #self.order.set_order_state(1)
        self.update_agent_state(1)
    
    '''
    Function called when the object pair has acknowledged that both agents are waiting and that thus have reached the meeting point 
    the order is de assigned from the picker and its state set to _Done
    while it is assigned to the deliverer without changing the order state, by interacting directly with the order layer 
    through the function order.assign_order , while the order.state is left untouched. 
    '''
    def switch_order(self, timestep):
        if self.Deliverer: 
            self.order = self.collab_order
            self.order.assign_order(self.agentId, timestep, self.order.getMeetingPoint(), self.Deliverer, self.Picker)  
            self.update_agent_state(5)
            self.Met = True

        elif self.Picker: 
            self.order.deAssign_order()
            self.update_agent_state(0)
            self.Met = True


    '''
    Function used by the Deliverer agent when the order is not assigned to him yet in order to get the coordinates of the meeting point 
    from the order layer 
    '''
    def setCollabOrder(self, order): 
        
        self.collab_order = order
        self.meetingPoint = order.meetingPoint
       # print(self.Picker, "self.picker")
       # print(self.Deliverer, "self.deliverer" )
        self.update_agent_state(3)
       # print("agent state to be updated ")
        self.goal = order.getMeetingPoint()  # function in order to retrieve meeting point ?

   


    '''
    Similarly to the previous function this is used for picking up the order and interacting with the order layer
    Agent state in this case is changed to _Meeting instead of _Delivering as it is a collab order 
    '''
    def pick_order_collab(self, timestep):
        self.order.set_order_state(2)
        self.order.timestep_pick = timestep
        self.update_agent_state(3)


    '''
    When the Deliverer receives the order from the Picker this function is called to keep the order state to Delivering and update the agent 
    state 
    '''
    def deliver_CollaBorder(self):
        self.order.set_order_state(2)
        self.update_agent_state(5)


    '''
    Main function called at each time step for every agent in the environment layer.  It links the agent layer to the environment, 
    the order and path finding layer 
    '''

    def makesMove(self, timestep, map):   # function which does the magicccc 
        
        ''' DEBUGGING
        if self.Collaborating == True and self.state == Agent_State._Waiting or self.state == Agent_State._DeliveringCollab:
            print("----------------------------***************")
            print("agent Id", self.agentId)
            print("state of the agent", self.state)
            print("Picker", self.Picker)
            print("Deliverer", self.Deliverer)
        
            if self.order != None:
                print("order", self.order.getOrderId())
        
            print("Agents Met ?", self.Met)
            print("----------------------------***************")
            '''

        # When order is non collaborative order layer is communicated that agent is neither a picker and neither a Deliverer
        if self.Collaborating == False:  
            if self.order != None:
                self.order.assign_picker_agent(False)

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

        # meet at meeting point in the middle
        # Picker robot waits for the deliverer 
        elif self.state == Agent_State._Meeting and self.position == self.goal and self.Collaborating and self.Picker and self.Met == False : 
            print("MEETING HERE Picker agent, waiting ",self.state, Agent_State._Meeting )
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            self.update_agent_state(4)   

            return self.position  #

        

        # waiting elif for deliverer 
        elif self.state == Agent_State._Meeting and self.position == self.goal and self.Collaborating and self.Deliverer and self.Met == False: 
            print("MEETING HERE Deliverer agent, waiting ",self.state, Agent_State._Meeting )
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            self.update_agent_state(4)  

            return self.position  



        # Deliverer robot goes back to init position once it has reached its destination 
        elif self.state == Agent_State._DeliveringCollab and self.position == self.goal and self.Collaborating and self.Deliverer and self.Met == True: 
            print("ORDER DELIVERED BY Deliverer agent ",self.state, Agent_State._Meeting )
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
             
            self.deliver_order(timestep)  # action to deliver order 
            
            return self.position 

        elif self.state == Agent_State._Picking and self.position == self.goal and self.Collaborating and self.Picker:
            print("PICKING HERE COLLAB",self.state, Agent_State._Picking)
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            self.pick_order_collab(timestep) 
            return self.position
        
        #  - deliverer robot goes from _Meeting to _DeliveringCollab and becomes main robot of order assignation 
    
        elif self.state == Agent_State._Meeting and self.position == self.goal and self.Collaborating and self.Deliverer and self.Met == True: # meet at meeting point in the middle 
            print("MEETING HERE Deliverer robot, waiting",self.state, Agent_State._Meeting )
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            self.deliver_CollaBorder()  # New state -- 5 delivery for collaboration  
            return self.position  

            # come back to base 
        elif self.state == Agent_State._Waiting and self.position == self.goal and self.Collaborating and self.Picker and self.Met == True:
            print("MET HERE WITH PAIR ROBOT DONE, COMING BACK TO INIT POS",self.state, Agent_State._Meeting, self.position )
            temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
            self.stepsHistory.append(temp_dict)# Save steps for visualization
            self.update_agent_state(0)  # New state -- 5 delivery for collaboration  
            return self.position  # CHANGE





        # Find next step
        #print("self.goal)", self.goal)
        x, y = self.pathfinder.solve(self.agentId ,map.copy(), self.position, self.goal)

        self.position = (x, y)  # position updated with the results of the path finder. 
        #self.state = Agent_State._Active

        # Save steps for visualization
        temp_dict = {"x": self.position[0], "y": self.position[1], "t": timestep}
        self.stepsHistory.append(temp_dict)

        #print("End of MakesMove:", self.position)
        return self.position





class Pair_State(Enum):
    _Available = 0
    _Busy = 1


'''
The purpose is to make sure that once on of the agents has reached the meeting point it waits until the other 
arrives for the next step. and order gets passed from one agent to the other 
'''
class Pair():  

    def __init__(self, Id):
        self.Id = Id 
        self.agent1 = None  # picker 
        self.agent2 = None # deliverer 
        self.order = None 
        self.state = Pair_State._Available
        self.pairLog = []  # history of the pair for analizing it later. 

    # Get coordinates of both agents 
    def getCoordinate(self): 
        return self.agent1.getPosition(), self.agent2.getPosition()

    '''
    Main function: 
    it checks at every time step that both agents are waiting , and if they are it executes the switch of order from one agent to the 
    other 
    '''
    def agents_met(self, timestep):

        if self.agent1 != None and self.agent2 != None:
            if self.agent1.getState() == Agent_State._Waiting and self.agent2.getState() == Agent_State._Waiting:
                self.agent1.switch_order(timestep)
                self.agent2.switch_order(timestep)

                self.update_pair_state(0)


    '''
    Once a collaborative order is found and a collaborative agent too this function is 
    called to assign the two agents and order to the pair 
    '''
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

    # Once the agents have met this is called to free the pair 
    def free_pair(self):
        self.agent1 = None 
        self.agent2 = None
        self.order = None

    '''
    Pair becomes available again once agents have met and becomes busy when agents are assigned to it 
    '''
    def update_pair_state(self, NewState): 
        if NewState == 0: 
            self.free_pair()
            self.state = Pair_State._Available
        elif NewState == 1: 
            self.state = Pair_State._Busy

    '''
    Function which connects the pair layer with the environment layer at each time step.
    '''
    def MakesMove(self, timestep):  
        self.agents_met(timestep)

