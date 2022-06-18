from enum import Enum
from numpy import empty, sqrt
from statistics import mean
import sys

import numpy
import yaml
import random

from agent import Agent, Agent_State, Pair, Pair_State
from AGV import Order, Order_State  

'''
Object used to store the information regarding the pick up stations in the initialization of
the environment class from the data in the input file 
'''
class PickupStation():
    def __init__(self, coordinate):
        self.coordinate = coordinate

    def getCoordinate(self):
        return self.coordinate

'''
Object used to store the information regarding the Delivery stations in the initialization of
the environment class from the data in the input file 
'''
class DeliveryStation():
    def __init__(self, coordinate):
        self.coordinate = coordinate
        

    def getCoordinate(self):
        return self.coordinate



'''
Object used to store the information regarding the meeting points in the initialization of
the environment class from the data in the input file 
'''
class MeetingPoint():
    def __init__(self, coordinate):
        self.coordinate = coordinate

    def getCoordinate(self):
        return self.coordinate

class WareHouse_Env():

    def __init__(self, input_config_file, render=True):
        """
        Creates a grid world of a warehouse, where multiples agents are supposed to collect items from pickup station
        and bring them to the delivery station. The Warehouse contains also obstacles and meeting points for the robots 

        :param input_config_file: yaml file that contains the word configuration
        """
        # Load experiment parameters from the input.yaml file
        params = read_config_file(input_config_file)

        # Prepare for save the history to output.yaml file
        self.output = {"schedule": None}

        # Set the world grid
        self.dimensions = params["map"]["dimensions"]
        print(self.dimensions)

        # parameter used as reference in the collaborative function to see where the agent is 
        self.HalfMap = int(self.dimensions[0]/2)
        print(self.HalfMap, "half map", "full map", self.dimensions[0])
        # 
        self.map = numpy.zeros(self.dimensions, dtype=object)

        # Add pickupStation to list deliveryStation to the map
        self.pickupStations = []
        for pickupStation in list(params["map"]["pickupStation"]):
            self.pickupStations.append(PickupStation(coordinate=pickupStation))

        # Add deliveryStation Add pickupStation to list deliveryStation to the map
        self.deliveryStations = []
        for deliveryStation in list(params["map"]["deliveryStation"]):
            self.deliveryStations.append(DeliveryStation(coordinate=deliveryStation))

        # Add obstacles to the map
        self.obstacles = []
        for obs in params["map"]["obstacles"]:
            self.obstacles.append(obs)
        #CHANGED
        # Add meeting points to the map
        self.meetingPoints = []
        for meetingPoint in params["map"]["meetingPoint"]:   # works as obstacle, change it to make it work as a delivery station or Pick up station 
            self.meetingPoints.append(MeetingPoint(coordinate = meetingPoint))   # .append(meetingPoint(coordinate = ))

        # Create agents
        self.agents = []
        for agentId, d in enumerate(params["agents"]):
            agent = Agent(d["name"], self.map, position=tuple(d["start"]))
            self.agents.append(agent)

        # Store agents init position
        self.agentsInitPos = []

        for agent in self.agents: 
            startX = agent.getPosition()[0]
            startY = agent.getPosition()[1]
            idAg = agent.getId()
            self.agentsInitPos.append([idAg, startX, startY])  # storing the init position of each agent and its id 

        # create pairs 
        m = int(len(self.agents)/2)

        self.pairs = []
        for i in range(m): 
            self.pairs.append(Pair(i))

        

        # Create Orders
        self.order_list = []
        for i in range(len(params["order"]["orders_"])):  # Create as many orders as total_orders
            id_code = params["order"]["orders_"][i]["id_code"]
            quantity = params["order"]["orders_"][i]["requested_quantities"]
            timestep_begin = params["order"]["orders_"][i]["timestep"]
            PickUP = params["order"]["orders_"][i]["pickupStation"]
            Delivery = params["order"]["orders_"][i]["deliveryStation"]  
            MeetingPoints = params["order"]["orders_"][i]["meetingPoint"]  
            order = Order(Delivery[0], PickUP[0], MeetingPoints[0], quantity, timestep_begin, id_code) 
            print("Initialization pt 1")
            print("ORDER", order.id_code, order.pickupStation, order.deliveryStation, order.meetingPoint,"quantity:", order.requested_quantities, "time_begin:",
                  order.timestep_begin)
            
            self.order_list.append(order)
            

        # control variable changed to TRUE when all orders are sorted and delivered 
        self._done = False
        

        # orders are agents are randomly shuffled so that each order can potentially be assigned to each agent 
        random.shuffle(self.order_list)  
        random.shuffle(self.agents)
        

        
        
        # Render in Terminal option
        self.renderMap(0)

    
    '''
    Main function used when running the entire program in a loop until all orders are sorted or the simualtion
    has taken longer than the max time steps decided by the user 
    '''

    def step(self, timestep):

        '''
        Assign orders until all agents are busy or orders have all been assigned. 
        It is important to note that some orders can be assigned also later on during the simulation thanks to order.getTimestep_begin. 
        '''
        for order in self.order_list:
            if order.get_order_state() == 0 and order.getTimestep_begin() <= timestep:
                winner = None
                for agent in self.agents: # A random agent which is non busy is assigned a random order 
                    if agent.getState() == Agent_State._Done:  # Agent is _Done and available reagrdless of its current location
                        
                        if winner == None:
                            winner = agent
                           
                if winner != None:   # once an ordeer is assigned it is checked if it is a collab order 
                    if self.callForCollab(winner, order) == True : # if collaborative find a pairable agent 
                        #print("entered")
                        agent2 = self.findThePair(winner)
                        if agent2 != False: 
                            print("winner of order assign", winner.getId(), "second agent", agent2.getId())
                            for pair in self.pairs:
                                
                                if pair.getState() == Pair_State._Available:  # find an available pair to take care of the collab order 
                                    
                                    pair.assign_agents(winner, agent2, order, timestep)# pair creation 
                                    
                                    break
                            
                            
                            winner.resetCollab() # reset collab order params in case of previous assignment 
                            agent2.resetCollab() 

                            winner.setOrder(order, timestep, winner.getId()) # Assign order to main winning agent 
                            for i in range(len(self.order_list)):
                                if order.getOrderId() == self.order_list[i].id_code:
                                    self.order_list[i].assign_order(winner.getId(),timestep, winner.getPosition(), winner.Deliverer, winner.Picker)   

                                    #self.order_list[i].agent_assigned = winner.getId()

                            
                           
                            
                            winner.setCollab_state(1, order) # setting collaboration within robots 
                            #print("order set up for agent 1 ", winner.getState())
                        
                            agent2.setCollab_state(0, order)
                            #print("order set up for agent 2 ", agent2.getState())


                        # if the order is collaborative but all other agents are busy then agent completes assignment alone 
                        elif agent2 == False: 
                            
                            winner.resetCollab()
                            winner.setOrder(order, timestep, winner.getId())
                            for i in range(len(self.order_list)):
                                if order.getOrderId() == self.order_list[i].id_code:
                                    self.order_list[i].assign_order(winner.getId(), timestep, winner.getPosition(), winner.Deliverer, winner.Picker)   #agent_assigned = winner.getId() 
                        
                        
                        '''
                        Order is non collaborative: Eg. agent is positioned on the right side and pick up and delivery station are also on the 
                        right side 
                        '''
                    elif self.callForCollab(winner, order) == False: 
                        
                        winner.resetCollab()
                        winner.setOrder(order, timestep, winner.getId())
                        for i in range(len(self.order_list)):
                            if order.getOrderId() == self.order_list[i].id_code:
                                self.order_list[i].assign_order(winner.getId(), timestep, winner.getPosition(), winner.Deliverer, winner.Picker)   #agent_assigned = winner.getId() 
                                
                                #self.order_list[i].agent_assigned = winner.getId() 


                        '''
                        Third order and agent location possibility:
                        Eg. the agent is on the right side and both delivery and pick up staion of the order are on the left side
                        as this would completely on the opposite side normally the order is not assigned to the robot. 

                        However in case it is the only robot available to optimize the overall efficiency the robot is assigned the order anyway
                
                        '''
                    elif self.callForCollab(winner, order) == 1: 

                        Done_agents = []
                        for agent in self.agents:  # Checl how many agents are _Done 
                            if agent.getState() == Agent_State._Done:
                                Done_agents.append()
                        
                        if len(Done_agents) == 1: 
                            winner.resetCollab()
                            winner.setOrder(order, timestep, winner.getId())
                            for i in range(len(self.order_list)):
                                if order.getOrderId() == self.order_list[i].id_code:
                                    self.order_list[i].assign_order(winner.getId(), timestep, winner.getPosition(), winner.Deliverer, winner.Picker)   #agent_assigned = winner.getId() 
                        
                        elif len(Done_agents) > 1: 
                            winner = None  # to be assigned to another agent       


        
        # Let agents make their moves
        for agent in self.agents:  # here ? 
            self.map[agent.getPosition()[0], agent.getPosition()[1]] = 0  # Reset position of agent
            agent.makesMove(timestep, self.map)
            self.renderMap(timestep)

        # Pairs make their moves
        for pair in self.pairs:
            pair.MakesMove(timestep)
        
      

        # Print for console
        self.renderMap(timestep, False)

        # Save history
        self.save_stepHistory()

    '''
    Every time an agent is assigned an order the function scans if it should a collaborative order, a normal order or due to distance constraints
    the agent should not be assigned it . 

    The logic for the decision scheme is based on the system model figure presented in the report. 
    '''
    def callForCollab(self, agent, order):
        
        if agent.getPosition()[0] > self.HalfMap and agent.getPosition()[0]< self.dimensions[0]:   
            ctrl = 1 
        elif agent.getPosition()[0] > 0 and agent.getPosition()[0]< self.HalfMap:
            ctrl = 0 

        if ctrl == 1 and order.deliveryStation[0] > self.HalfMap and order.pickupStation[0] > self.HalfMap: # A2 O4
            return False
        elif ctrl == 1 and order.deliveryStation[0] < self.HalfMap and order.pickupStation[0] > self.HalfMap:   # A2 O3 
            return True 

        elif ctrl == 1 and order.deliveryStation[0] < self.HalfMap and order.pickupStation[0] < self.HalfMap: # A2 O2 
            return 1
        elif ctrl == 1 and order.deliveryStation[0] > self.HalfMap and order.pickupStation[0] < self.HalfMap: # A1 O1 
            return 1 

        elif ctrl == 0 and order.deliveryStation[0] > self.HalfMap and order.pickupStation[0] < self.HalfMap: # A1 O1
            return True
        elif ctrl == 0 and order.deliveryStation[0] < self.HalfMap and order.pickupStation[0] < self.HalfMap: # A1 O2 
            return False  

        elif ctrl == 0 and order.deliveryStation[0] < self.HalfMap and order.pickupStation[0] > self.HalfMap: # A1 O3 
            return 1 
        elif ctrl == 0 and order.deliveryStation[0] > self.HalfMap and order.pickupStation[0] > self.HalfMap: # A1 O4 
            return 1 
        else: 
            return 1  
        
    
    '''
    When an order is indeed collaborative this function is responible for finding an agent to pair 
    '''
    def findThePair(self, agentRef):  # agentRef is the agent to which the order has been assigned 
        
        def is_not_busy(agent):  # internal function which checks that an agent is not busy 
            if agent.getState() == Agent_State._Done:
                return True
            else:
                return False

        differences = [] # a list where the differences in distances on the y-axis of the agents opposite to the winner is created 
        ids = []
        value = 0 
        

        for agentPos in self.agentsInitPos:  # check initial positions 
            value = 0
            if agentRef.getPosition()[0] != agentPos[1]: # make sure other agent is not on the same side 
                value = agentRef.getPosition()[1] - agentPos[2]   
                if agentRef.getId() != agentPos[0]:   # just in case agent does not get paired with itself 
                    differences.append(abs(value))
                    ids.append(agentPos[0])

        '''
        # find min difference -- check if agent is not busy, if not then return the found agent, if 
        # agent is busy find the other one which is closest and on the other side and so on
        # every time an agent is busy then it is removed from the list of possible candidates. 

        Eg. closest agent is busy, the second closest will be the next taken into consideration 

        '''
        minDiff = 0
        minDiffIndex = 0

        while len(differences) != 0:  # until we find a free agent or we are sure all the others are busy 

            for agent in self.agents:
                if len(differences) > 0:
                    minDiff = min(differences)  
                    minDiffIndex = differences.index(minDiff)

                    if ids[minDiffIndex] == agent.getId() and ids and differences:
                        candidate = agent
                        if is_not_busy(candidate):
                            print("Pair found! for ",agentRef.getId(),"paired with :", candidate.getId())
                            return candidate 
                        elif is_not_busy(candidate) == False:
                            differences.remove(minDiff)
                        ids.remove(ids[minDiffIndex])
                    elif differences == [] and ids == []: # if all agents are busy then it is impossible to pair 
                            print("All agents busy, sorry")
                else:
                    return False

        return False
        
        


    # Render stations
    def renderMap(self, timestep, printBool=False):
        """
        Renders the map completely new everytime.
        """

        # Render everything to zero
        self.map = numpy.zeros(self.dimensions, dtype=object)

        # Add obstacles
        for obs in self.obstacles:
            self.map[obs] = "*"

        # Add pickup stations
        for pickupStation in self.pickupStations:
            self.map[pickupStation.getCoordinate()] = "P"

        # Add delivery stations -- follow same logic as for pickup stations 
        
        for deliveryStation in self.deliveryStations:
            self.map[deliveryStation.getCoordinate()] = "D"

        
        # Add meeting points 
        for meetingPoint in self.meetingPoints:
            self.map[meetingPoint.getCoordinate()] = "M"  

        # Add agents
        for agent in self.agents:
            if self.is_in_P_station(agent):
                self.map[agent.getPosition()] = f"P@A{agent.agentId}"   # check what this does TODO
            elif self.is_in_D_station(agent):  # change it ---> how ? 
                self.map[agent.getPosition()] = f"D@A{agent.agentId}"
            elif self.is_in_M_station(agent):
                self.map[agent.getPosition()] = f"D@A{agent.agentId}"
            else:
                self.map[agent.getPosition()] = f"A{agent.getId()}"

        if printBool:
            print("#################", timestep)
            print(self.map)

    def is_in_P_station(self, agent):
        for pickupStation in self.pickupStations:
            if pickupStation.getCoordinate() == agent.getPosition():
                return True
        return False

    def is_in_D_station(self, agent):
        for deliveryStation in self.deliveryStations:
            if deliveryStation.getCoordinate() == agent.getPosition():
                return True 
        return False
     
    def is_in_M_station(self, agent):
        for meetingpoints in self.meetingPoints:
            if meetingpoints.getCoordinate() == agent.getPosition():
                return True 
        return False

    def allOrdersDone(self):
        """
        Return true if all orders are delivered
        """
        for order in self.order_list:
            if order.get_order_state() != 3:
                return False
        return True

    def save_stepHistory(self):
        data = {}
        for agent in self.agents:
            data[agent.getId()] = agent.getStepsHistory()
        self.output["schedule"] = data

    # Update env state to done if all agents are _Done and no more orders
    def everythingDone(self):
        """
        End simulation if all orders had been delivered.
        """
        if self.order_list != []:
            return False
        for agent in self.agents:
            if agent.state != Agent_State._Done:
                return False
        return True


def read_config_file(config_file):
    with open(config_file, 'r') as input_file:
        try:
            params = yaml.load(input_file, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)
    return params


def write_output_file(output_file, output):
    with open(output_file, 'w') as output_yaml:
        yaml.safe_dump(output, output_yaml)


if __name__ == "__main__":
    input_file ="input.yaml" 
    env = WareHouse_Env(input_config_file=input_file)
    timestep = 0

    agentState =[]
    pairsState = []

    while True:
        env.step(timestep)

        timestep += 1
        
        if timestep > 500 or env.allOrdersDone():  
            print("Done with", timestep, "timesteps.")
            break

    # Print results 
    totallist = []
    deliverytimelist = []
    waitingtimelist = []
    t_difflist = []
    losslist = []
    maxdeliverylist = []
    dperformedlist = []
    mindistancelist = []
    performeddistancelist = []
    simulationtimelist = []

    # add delivery station to the list 
    for j in range(len(env.order_list)):
        E = env.order_list[j]
        print("Order;", E.id_code, "; agent", E.agent_assigned, "; agent pos:", E.agent_pos, "; pickup:",
              E.pickupStation,  "; delivery:", E.deliveryStation , "; d_required:", round(E.distance, 1), "; t_begin:", E.timestep_begin, "; t_pick:",
              E.timestep_pick, "; t_end:", E.timestep_end, "; t_diff:", (E.timestep_pick - E.timestep_begin),
              "; d_performed:", (E.timestep_end - E.timestep_pick), "; loss:",
              round((E.timestep_end - E.timestep_pick - E.distance), 2))

            # Add delivery station to the metrics 

        # print("Order", E.id_code, " agent", E.agent_assigned)
        # print("agent pos:", E.agent_pos, "pickup: ", E.pickupStation, "distance: ", round( sqrt((E.agent_pos[0] - E.pickupStation[0])**2 + (E.agent_pos[1] - E.pickupStation[1])**2), 1))
        # print("quantity:", E.requested_quantities, " t_begin:", E.timestep_begin)
        # print("t_begin:", E.timestep_begin, "t_pick:", E.timestep_pick, " t_end: ",  E.timestep_end)
        # print("d_performed:", (E.timestep_end - E.timestep_pick))
        # print("loss: ", round((E.timestep_end - E.timestep_pick - E.distance), 2))
        totallist.append(E.timestep_end - E.timestep_begin)
        waitingtimelist.append(E.timestep_pick - E.timestep_begin)
        deliverytimelist.append(E.timestep_end - E.timestep_pick)
        t_difflist.append(E.timestep_pick - E.timestep_begin) #DISTANCE T_DIFF

        maxdeliverylist.append(E.timestep_end)
        dperformedlist.append((E.timestep_end - E.timestep_pick))

        mindistancelist.append(round(E.distance, 1))
        performeddistancelist.append((E.timestep_end - E.timestep_pick))
        losslist.append(round((E.timestep_end - E.timestep_pick - E.distance), 2))  # losslist
        simulationtimelist.append(E.timestep_end)

    orderchangelist = []
   
    for agent in env.agents:
        i = 0
        for first, second in zip(agent.order_log, agent.order_log[1 : ] + agent.order_log[ : 1]):
            if (first != second):
                i = i + 1


    for agent in env.agents:
            agentState.append([agent.state, agent.agentId, "\n"])

    for pair in env.pairs:
        if pair.agent1 != None:
            pairsState.append([pair.agent1.getId(), "Picker",pair.agent1.Picker ,pair.agent1.getState(), pair.agent2.getId(), "Deliverer",pair.agent2.Deliverer, pair.agent2.getState(), "\n"])


    #print('average order switches ' + str(mean(orderchangelist)))
    write_output_file("./output.yaml", env.output)
    #print(" avg delivery: " + str(mean(deliverytimelist)) + " avg total: " + str(
    #   mean(totallist)) + " avg waitinglist: " + str(mean(waitingtimelist)))

    #print(sys.argv[1])
    

    '''
    save metrics of the simulation for data analysis 
    '''
    

    filehandler2 = open('maxdeliverytimeagents.txt', 'a')
    filehandler2.write(str(max(maxdeliverylist)))
    filehandler2.write("\n")
    filehandler2.close()


    filehandler3 = open('averagelosstime.txt', 'a')
    filehandler3.write(str(mean(losslist)))
    filehandler3.write("\n")
    filehandler3.close()

    filehandler4 = open('average_d_performed.txt', 'a')
    filehandler4.write(str(mean(dperformedlist)))
    filehandler4.write("\n")
    filehandler4.close()

    filehandler5 = open('Exp_mapArea_results.txt', 'a')
    #filehandler5.write(sys.argv[1] + '''
    #'''

    #''')
    filehandler5.write("\n\n")
    filehandler5.write("average min distance \n")
    filehandler5.write(str(mean(mindistancelist)))
    filehandler5.write("\n")


    filehandler5.write("average performed distance \n")#
    filehandler5.write(str(mean(performeddistancelist)))
    filehandler5.write("\n")


    filehandler5.write("average loss \n")#
    filehandler5.write(str(mean(losslist)))
    filehandler5.write("\n")


    filehandler5.write("max loss \n")#
    filehandler5.write(str(max(losslist)))
    filehandler5.write("\n")


    filehandler5.write("max simulation time \n")
    filehandler5.write(str(max(simulationtimelist)))
    filehandler5.write("\n")
    filehandler5.close()