from enum import Enum
from numpy import empty, sqrt
from statistics import mean
import sys

import numpy
import yaml
import random

from agent import Agent, Agent_State, Pair, Pair_State
from AGV import Order, Order_State  


class PickupStation():
    def __init__(self, coordinate):
        self.coordinate = coordinate

    def getCoordinate(self):
        return self.coordinate


class DeliveryStation():
    def __init__(self, coordinate):
        self.coordinate = coordinate
        

    def getCoordinate(self):
        return self.coordinate



#changed
class MeetingPoint():
    def __init__(self, coordinate):
        self.coordinate = coordinate

    def getCoordinate(self):
        return self.coordinate

class WareHouse_Env():

    def __init__(self, input_config_file, render=True):
        """
        Creates a grid world of a warehouse, where multiples agents are supposed to collect items from pickup station
        and bring them to the delivery station. The Warehouse contains also obstacles

        :param input_config_file: yaml file that contains the word configuration
        """
        # Load experiment parameters from the input.yaml file
        params = read_config_file(input_config_file)

        # Prepare for save the history to output.yaml file
        self.output = {"schedule": None}

        # Set the world grid
        self.dimensions = params["map"]["dimensions"]
        self.map = numpy.zeros(self.dimensions, dtype=object)

        # Add pickupStation to list deliveryStation to the map
        self.pickupStations = []
        for pickupStation in list(params["map"]["pickupStation"]):
            self.pickupStations.append(PickupStation(coordinate=pickupStation))

        # Add deliveryStation to list
        # create similar for loop as above 

        ##################################################################################################
        ## NEWLY ADDED TODO: test and debug 
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

        self.agentsInitPos = []

        for agent in self.agents: 
            startX = agent.getPosition()[0]
            startY = agent.getPosition()[1]
            idAg = agent.getId()
            self.agentsInitPos.append([idAg, startX, startY])  # storing the init position of each agent 

        # create pairs 
        m = int(len(self.agents)/2)

        self.pairs = []
        for i in range(m): 
            self.pairs.append(Pair(i))

        # Create Orders
        self.order_list = []
        # self.order_stats = []
        # add delivery station in order details 
        for i in range(len(params["order"]["orders_"])):  # Create as many orders as total_orders
            id_code = params["order"]["orders_"][i]["id_code"]
            quantity = params["order"]["orders_"][i]["requested_quantities"]
            timestep_begin = params["order"]["orders_"][i]["timestep"]
            PickUP = params["order"]["orders_"][i]["pickupStation"]
            Delivery = params["order"]["orders_"][i]["deliveryStation"]  # added line 
            MeetingPoints = params["order"]["orders_"][i]["meetingPoint"]  # added line 
            order = Order(Delivery[0], PickUP[0], MeetingPoints[0], quantity, timestep_begin, id_code) # check --- #CHANGED
            print("ORDER", order.id_code, order.pickupStation, order.deliveryStation, "quantity:", order.requested_quantities, "time_begin:",
                  order.timestep_begin)
            self.order_list.append(order)
            # self.order_stats.append(order)

        # Check if all agents are done
        self._done = False

        # Render in Terminal option
        self.renderMap(0)

    def step(self, timestep):

        # Assign orders to agents
        '''
            CNP: Orders are distributed here. Agent bid with distance to pickup station of order.
        '''
        for order in self.order_list:
            if order.get_order_state() == 0 and order.getTimestep_begin() <= timestep:
                winner = None
                winnerDistance = None
                for agent in self.agents:
                    if agent.getState() == Agent_State._Done:  # Agent is _Done
                        #distance = self.callForProposal(agent, order)
                        if winner == None: #or distance < winnerDistance:
                            #winnerDistance = distance
                            winner = agent
                           
                if winner != None:
                    # check if order should be collaborative 
                    if self.callForCollab(winner, order): 
                        agent2 = self.findThePair(winner)
                        if agent2 != False: 
                            winner.Collaborating = True; winner.Picker = True  # roles defined 
                            agent2.Collaborating = True; agent2.Deliverer = True 

                            # Create PAIR -- HOW ??? 
                            
                            winner.setOrder(order, timestep, winner.getId())
                            for i in range(len(self.order_list)):
                                if order.getOrderId() == self.order_list[i].id_code:
                                    self.order_list[i].agent_assigned = winner.getId()

        '''
            eCNP: All agents get orders proposed, also agent who already working on an order.
        '''

        '''
        for order in self.order_list: #to turn off eCMP comment it out
            if order.get_order_state() == 1 and order.getTimestep_begin() <= timestep:
                winner = None
                winnerDistance = None
                for agent in self.agents:
                    if agent.getState() == Agent_State._Done or agent.getState() == Agent_State._Picking:  # Agent is _Done
                        distance = self.callForProposal(agent, order)
                        if winner == None or distance < winnerDistance:
                            winnerDistance = distance
                            winner = agent
                         # created the first time it runs and resets per every order. 
                if winner != None:
                    winner.setOrder(order, timestep, winner.getId())
                    for i in range(len(self.order_list)):
                        if order.getOrderId() == self.order_list[i].id_code:
                            self.order_list[i].agent_assigned = winner.getId()
        '''
        # Let agents make their moves
        for agent in self.agents:  # here ? 
            self.map[agent.getPosition()[0], agent.getPosition()[1]] = 0  # Reset position of agent
            agent.makesMove(timestep, self.map)
            self.renderMap(timestep)
        
        # same thing as above but for the Pair class   
        # TODO: create 3 pairs and do not initialize them -- follow same pattern as for order for assignment ( put the agents) and de assignment when order is delivered 


        # Print for console
        self.renderMap(timestep, False)

        # Save history
        self.save_stepHistory()

    def callForCollab(self, agent, order):
        # what is needed: order details, namely delivery station coordinates and assigned robot initial position 
        if agent.getPosition()[0] > 25 and agent.getPosition()[0]< 50:
            ctrl = 1 
        elif agent.getPosition()[0] > 0 and agent.getPosition()[0]< 26:
            ctrl = 0 

        if ctrl == 1 and order.deliveryStation[0] > 25: 
            return False
        elif ctrl == 1 and order.deliveryStation[0] > 25: 
            return True 
        elif ctrl == 0 and order.deliveryStation[0] > 25: 
            return True
        elif ctrl == 0 and order.deliveryStation[0] > 25: 
            return False  
        else: 
            return False # check if delivery station x - coordinate is within a certain threshold  < 25 , if not then create pairs 
        

    def findThePair(self, agentRef):  # agentRef is the agent to which the order has been assigned 
        
        def is_not_busy(agent):
            if agent.getState() == 0:
                return True
            else:
                return False

        differences = []
        ids = []
        value = 0 
        for agentPos in self.agentsInitPos:  # check initial positions 
            value = 0
            value = agentRef.getPosition()[1] - agentPos[2]  # check this TODO
            differences.append(value)
            ids.append(agentPos[0])
            
        #TODO -- finish to implement the pair matching 
        # find min difference -- check if agent is not busy, if not then return the found agent, if 
        # agent is busy find the other one which is closest and on the other side and so on, make it in a for loop which scans it 

        minDiff = 0
        minDiffIndex = 0

        while differences != empty: 
            for agent in self.agents:
                minDiff = min(differences)   
                minDiffIndex = differences.index(minDiff)

                if ids[minDiffIndex] == agent.getId() and ids and differences:
                    candidate = agent
                    if is_not_busy(candidate):
                        print("Pair found!", candidate.getId())
                        return candidate 
                    elif is_not_busy(candidate) == False:
                        differences.remove(minDiff)
                        ids.remove(ids[minDiffIndex])
                elif differences != True and ids != True: # if all agents are busy then it is impossible to pair 
                        print("All agents busy, sorry")
        return False
        
        
        
            
            
    def createPair(self, agentRef):
        
        agent2 = self.findThePair(agentRef)

        if agent2 == False:
            return False 
        else:
            #self.pairIDs = [[agentRef, agent2]] # store it 
            return agentRef.getId(), agent2.agentId # the pair is created based on the agents which lay within the same horizontal line 


    def BothRobotMet(self, agent1, agent2):
        # function shold check that both robots are at the meeting points to change 'winner' 
        if self.is_in_M_station(agent1) and self.is_in_M_station(agent2):
            return True 
        else: 
            return False 


    def callForProposal(self, agent, order):
        """
        Return distance of agent to orders pickupstation
    
        """
        return sqrt((order.getPickupStation()[0] - agent.getPosition()[0]) ** 2 + (
                    order.getPickupStation()[1] - agent.getPosition()[1]) ** 2)

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

        #CHANGED
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
    #CHANGED
    # similar logic for meeting points 
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
            # print("agent.state != Agent_State._Done", agent.state, Agent_State._Done, agent.state != Agent_State._Done)
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
    input_file ="input.yaml" #sys.argv[1]
    env = WareHouse_Env(input_config_file=input_file)
    timestep = 0
    while True:
        env.step(timestep)

        timestep += 1

        if timestep > 20000000 or env.allOrdersDone():
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

        print("agent:", agent.agentId, ", number of order-changes:", agent.order_switchcount, ', unequal changes: ', i)
        orderchangelist.append(i)

    print('average order switches ' + str(mean(orderchangelist)))
    write_output_file("./output.yaml", env.output)
    print(" avg delivery: " + str(mean(deliverytimelist)) + " avg total: " + str(
        mean(totallist)) + " avg waitinglist: " + str(mean(waitingtimelist)))

    #print(sys.argv[1])

    filehandler0 = open('averageorderswitches.txt', 'a')
    filehandler0.write(str(mean(orderchangelist)))
    filehandler0.write("\n")
    filehandler0.close()

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



    filehandler5.write("average order changes \n")
    filehandler5.write(str(mean(orderchangelist)))
    filehandler5.write("\n")

  #'''


    filehandler5.close()