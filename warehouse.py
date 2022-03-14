from enum import Enum

import numpy
import yaml
import random

from AGV import Agent, Agent_State, Order, Order_State


class Station_State(Enum):
    _Empty = 0
    _Full = 1


class PickupStation():
    def __init__(self, coordinate):
        self.coordinate = coordinate

class DeliveryStation():
    def __init__(self, coordinate):
        self.coordinate = coordinate

class MeetingStations():  # We added the meeting point stations am
    def __init__(self, coordinate):
        self.coordinate = coordinate 

# TODO: add meeting point stations 

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

        # Add pickupStation and deliveryStation to the map
        self.pickupStation = params["map"]["pickupStation"]

        self.deliveryStation = DeliveryStation(coordinate=list(params["map"]["deliveryStation"])) # should be changed to the same format of pickupStation as we have several ones 

        # Add obstacles to the map
        self.obstacles = params["map"]["obstacles"]

        for obs in self.obstacles:
            self.map[obs[0], obs[1]] = "*"

        # Add Agents to the map according to their starting postion
        self.Agents = {}
        for (agentId, d) in enumerate(params["agents"]):
            agent = Agent(d["name"], self.map, self.deliveryStation, currentPosition=d["start"])
            self.map[agent.currentPosition[0], agent.currentPosition[1]] = f"A{agentId}"
            self.Agents[d["name"]] = agent
            self.render_stations(agent)

        #Create Orders
        self.order_list = []
        self.order_stats = []

        for i in range(len(params["order"]["orders_"])):# Create as many orders as total_orders
            #total_quantity = 3# For all goods

            id_code = params["order"]["orders_"][i]["id_code"]
            quantity = params["order"]["orders_"][i]["requested_quantities"]
            timestep_begin = params["order"]["orders_"][i]["timestep"]
            PickUP = params["order"]["orders_"][i]["pickupStation"]
            # TODO: add delivery station
            order = Order(self.deliveryStation, PickUP, quantity, timestep_begin, id_code)
            print("ORDER", order.id_code, order.pickupStation, "quantity:", order.requested_quantities, "time_begin:", order.timestep_begin)
            self.order_list.append(order)
            self.order_stats.append(order)
                # TODO Create orders with random requested_quantities, total order needs to be lower then total_quantity and higher then 0
                #requested_quantity = random.randint(0, total_quantity)# For each good

        #self.order_stats = self.order_list
        #print(self.order_list)

        # TODO
        self._done = [False] * len(self.Agents)
        # Render in Terminal option
        self.rendering = render

    def step(self, timestep):
        # Agents make one move, sequentially
        if timestep == 0:
            timestep += 1
            return

        for agentId, (_, agent) in enumerate(self.Agents.items()):


            self.update_env_state()
            agent.update_agent_state()

            # Assign orders to agents
            #ACCORDING TO TIMESTPE DIOCANE
            if self.order_list != []:
                i=0
                while (i < (len(self.order_list))):
                    #print("i:",i)
                    O = self.order_list[i]
                    if O.timestep_begin <= timestep and (agent.state == Agent_State._Off or agent.state == Agent_State._Done) :
                        agent.setOrder(self.order_list.pop(i), timestep, agentId)
                        for j in range(len(self.order_stats)):
                            if O.id_code == self.order_stats[j].id_code:
                                self.order_stats[j].agent_assigned = agentId
                        i=0
                    i+=1

            # Check if Agent X at the pickupstation and ready to pick
            if self.is_in_P_station(agent) and agent.state == Agent_State._Active:
                agent.pick_order()
                for j in range(len(self.order_stats)):
                            if agent.order.id_code == self.order_stats[j].id_code:
                                self.order_stats[j].timestep_pick = timestep

                self.map[agent.currentPosition[0], agent.currentPosition[1]] = f"P/A{agentId}"

            # Check if the Agent at the deliverystation
            elif self.is_in_D_station(agent) and agent.state == Agent_State._Shipping:
                agent.deliver_order()
                for j in range(len(self.order_stats)):
                            if agent.order.id_code == self.order_stats[j].id_code:
                                self.order_stats[j].timestep_end = timestep

                self.map[agent.currentPosition[0], agent.currentPosition[1]] = f"D/A{agentId}"

            # check if agent is at the meeting point 
            # if both paired agents are there then --> agent 1 goes back to starting point and agent 2 goes to delivery station 

            # Check if the Agent at the starting point and DONE with the job
            elif self.is_in_S_station(agent) and agent.state == Agent_State._Done:
                agent.go_idle()
                self.map[agent.currentPosition[0], agent.currentPosition[1]] = f"D/A{agentId}"


            # Check if there are collision with agent X TODO what if many agent are colliding in the same pos ?
            elif self.check_collision(agent):
                agentX_pos = agent.currentPosition
                agentX = self.get_agents_by_postion(agentX_pos)[-1]
                self.map[agent.currentPosition[0], agent.currentPosition[1]] = f"A{agentId}/A{agentX.agentId}"
                # TODO to check what to do if collide (normaly agent --> order (to revisite))
                agent.order.state = Order_State._Interrupted
                agent.update_agent_state()
                agentX.order.state = Order_State._Interrupted
                agentX.update_agent_state()


            # check if there is a collision with obstacles TODO what to do
            elif self.check_collision_with_obs(agent):
                self.map[agent.currentPosition[0], agent.currentPosition[1]] = f"x/A{agentId}"
                agent.order.state = Order_State._Interrupted
                agent.update_agent_state()


            # Normal routine
            else:
                self.map[agent.currentPosition[0], agent.currentPosition[1]] = 0
                if agent.state != 0:
                    agent.makesMove(timestep)
                self.map[agent.currentPosition[0], agent.currentPosition[1]] = f"A{agentId}"
                agent.update_agent_state()

            # Save History to  output dict
            self.save_stepHistory()

        # if self.rendering:
        #     self.render(timestep)

    # Render stations
    def render_stations(self, agent):
        if self.is_in_P_station(agent):
            self.map[agent.currentPosition[0], agent.currentPosition[1]] = f"P@A{agent.agentId}"
        else:
            for i in range(len(self.pickupStation)):
                P = self.pickupStation[i]
                self.map[P[0], P[1]] = "P"

        if self.is_in_D_station(agent):
            self.map[agent.currentPosition[0], agent.currentPosition[1]] = f"D@A{agent.agentId}"
        else:
            self.map[self.deliveryStation.coordinate[0][0], self.deliveryStation.coordinate[0][1]] = "D"

    def save_stepHistory(self):
        data = {}
        for agentId, agent in self.Agents.items():
            data[agentId] = agent.getStepsHistory()
        self.output["schedule"] = data

    def is_in_D_station(self, agent):
        return (agent.currentPosition[0] == agent.deliveryStation.coordinate[0][0]) and \
               (agent.currentPosition[1] == agent.deliveryStation.coordinate[0][1])

    def is_in_P_station(self, agent):
        a = False
        for i in range(len(self.pickupStation)):
            P = self.pickupStation[i]
            a = a or (agent.currentPosition[0] == P[0] and \
               agent.currentPosition[1] == P[1])
        return (a)


    def is_in_S_station(self, agent):
        return (agent.currentPosition[0] == agent.startingPosition[0]) and \
               (agent.currentPosition[1] == agent.startingPosition[1])

    def get_agents_by_postion(self, position):
        tmp_dict = []
        for agentId, agentX in self.Agents.items():
            if (position[0] == agentX.currentPosition[0]) and (position[1] == agentX.currentPosition[1]):
                tmp_dict.append(agentX)
        return tmp_dict

    def get_agent_by_id(self, agentId):
        return self.Agents[agentId]

    # TODO Collison with obs need to be a zone in the grid not one single pt
    def check_collision_with_obs(self, agent):
        for obs in self.obstacles:
            if (obs[0] == agent.currentPosition[0]) and (obs[1] == agent.currentPosition[1]):
                return True
            else:
                return False

    # TODO Collison with other agent need to be a zone in the grid not one single pt
    def check_collision(self, agent):
        tmp = False
        for agentId, agentX in self.Agents.items():
            if agent.agentId != agentId:
                if (agent.currentPosition[0] == agentX.currentPosition[0]) and \
                        (agent.currentPosition[1] == agentX.currentPosition[1]):
                    tmp = True
                    return tmp
            else:
                return tmp

    # Update env state according to agent state
    def update_env_state(self):
        def _check_agent(agent):
            #return (agent.state == Agent_State._Done) or (agent.state == Agent_State._Out_of_Order)
            return (agent.state == Agent_State._Out_of_Order)

        self._done = [_check_agent(v) for v in self.Agents.values()]

    def rest(self, agent):
        pass

    def render(self, timestep):
        print(f"++++++++++++++Map+++++++++++++++++")
        print(f"timestep:{timestep}")
        print(self.map)
        for _, agent in self.Agents.items():
            # self.render_sations(agent)
            print(f"agent:{agent.agentId} , state:{agent.state.name};")



def read_config_file(config_file):
    with open(config_file, 'r') as input_file:
        try:
            params = yaml.load(input_file, Loader=yaml.FullLoader)
            # print(map)
        except yaml.YAMLError as exc:
            print(exc)
    return params


def write_output_file(output_file, output):
    with open(output_file, 'w') as output_yaml:
        yaml.safe_dump(output, output_yaml)


if __name__ == "__main__":
    input_file = "./input.yaml"
    env = WareHouse_Env(input_config_file=input_file)
    timestep = 0
    while True:
        env.render(timestep)
        env.step(timestep)

        timestep += 1
        print(env._done)
        if timestep > 1000 or all(env._done):

            break

    #print(len(env.order_stats))
    for j in range(len(env.order_stats)):
        E = env.order_stats[j]
        print("Order;", E.id_code, ";agent", E.agent_assigned, ";pickup;", E.pickupStation, ";d_required;", round(E.distance, 1), "; t_begin:", E.timestep_begin, "; t_pick:", E.timestep_pick, "; t_end:",  E.timestep_end, ";d_performed:", (E.timestep_end - E.timestep_pick), ";loss:", round((E.timestep_end - E.timestep_pick - E.distance), 2))

        # print("Order", E.id_code, " agent", E.agent_assigned)
        # print("pickup: ", E.pickupStation, "d_required: ", round(E.distance, 1))
        # print("quantity:", E.requested_quantities, " t_begin:", E.timestep_begin)
        # print("t_pick:", E.timestep_pick, " t_end: ",  E.timestep_end)
        # print("d_performed:", (E.timestep_end - E.timestep_pick))
        # print("loss: ", round((E.timestep_end - E.timestep_pick - E.distance), 2))

    write_output_file("./output.yaml", env.output)
