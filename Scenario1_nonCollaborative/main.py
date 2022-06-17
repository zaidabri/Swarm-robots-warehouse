import random
import numpy as np
import tcod #python3 -m pip install --user tcod


'''
This class is used for the navigation part of the single agents. 

It is made of 3 different functions. The agent layer is the primary user of this. 
At each time step from environment.py for each agent the function agent.makesMove is called
which in turn calls the function Pathfinder.solve  

The remaining two functions of this layer are auxiliary functions to the solve function 
'''

class Pathfinder:


    '''
    Pre processing function where the map is represented as of a grid of a summation of 1x1 squares
    for a total dimension of nxn. The dimension of the map is decided in the input file. 

    The inputs are the graph representing the map and the start position of the agent (its current position)

    The goal is to represent the grid with a binary approach: obstacles are represented by 0 and squares where the agent can go by 1 
    
    output: updated graph with new position the dynamic obstacles updated 
    '''
    def prepareGraph(self, graph, start):
        
        for i in range(len(graph)):
            for j in range(len(graph[i])):
                if graph[i][j] == 0 or isinstance(graph[i][j], str) and ("P" in graph[i][j] or "D" in graph[i][j] or "M" in graph[i][j]):
                    if isinstance(graph[i][j], str) and "A" in graph[i][j]:
                        continue
                    graph[i][j] = 1

        x = start[0]
        y = start[1]

        # Add agents to map
        if x - 1 >= 0:
            if isinstance(graph[x-1][y], str) and "A" in graph[x-1][y]:
                graph[x-1][y] = 0
        if x + 1 < len(graph):
            if isinstance(graph[x+1][y], str) and "A" in graph[x+1][y]:
                graph[x-1][y] = 0
        if y - 1 >= 0:
            if isinstance(graph[x][y-1], str) and "A" in graph[x][y-1]:
                graph[x][y-1] = 0
        if y + 1 < len(graph):
            if isinstance(graph[x][y+1], str) and "A" in graph[x][y+1]:
                graph[x][y+1] = 0

     
        #Change not neighbour agents to 1 because they are not obstacles
        # Neighboring agents seen as obstalce so change to 0 
        for i in range(len(graph)):
            for j in range(len(graph[i])):
                if isinstance(graph[i][j], str) and "A" in graph[i][j]:
                    graph[i][j] = 0

        # Change * to 0 for obstacles
        for i in range(len(graph)):
            for j in range(len(graph[i])):
                if graph[i][j] == "*":
                    graph[i][j] = 0



        return graph
    
    
    
    '''
    This function has been specifically designed to allow the agents waiting at a meeting point to make random 1 step long 
    moves around the meeting point. This has been done in order to allow other deliverer agents to reach the meeting point and thus set their state
    to waiting. 
    
    '''
    def randomStep(self, graph, start):
        #print("RANDOMSTEP INPUT", start)
        for i in range(4):
            x = start[0]
            y = start[1]
            j = random.randint(0, 3)
            #print("HERE I AM",j)

            if j == 0:
                x += 1
                if x < len(graph[0]) and graph[x][y] == 1:
                    return x,y
            elif j == 1:
                x -= 1
                if x >= 0 and graph[x][y] == 1:
                    return x,y
            elif j == 2:
                y += 1
                if y < len(graph[0]) and graph[x][y] == 1:
                    return x,y
            elif j == 3:
                y -= 1
                if y >= 0 and graph[x][y] == 1:
                    return x,y
        return start[0], start[1]
    

    '''
    Main function used by each agent at each time-step of the simulation. 

    Input: non-preprocessed graph, start position of the agent, goal position 

    first the preprocessing of the graph is done 
    secondly the library tcod is used to calculate the shortest path using the A* algorithm 
    based on the length of the solution it is checked whether the random step function should be used or if the 
    computed solution can be used by the agent

    output: new position of the agent 
    '''
    def solve(self, agentId, graph, start, end):
        #print("main\\","agentId:",agentId, "start:", start,"end:", end)

        #print(graph)


        self.x = start[0]
        self.y = start[1]
        preparedGraph = self.prepareGraph(graph, start)   # preprocessing
        preparedGraph = graph.astype(dtype=np.int8, order="F")

        #print(preparedGraph)
        tcodGraph = tcod.path.SimpleGraph(cost=preparedGraph,cardinal=1,diagonal=0)  # tcod library for A* path finding 

        pf = tcod.path.Pathfinder(tcodGraph)
        pf.add_root(start)
        pf.resolve()

        solution = pf.path_to(end)

        if len(solution) > 1:
            self.x = np.uint32(solution[1][0]).item()
            self.y = np.uint32(solution[1][1]).item()
            return self.x, self.y
        else:
            x, y = self.randomStep(preparedGraph, start)
            #print("x and y", x, y)
            return x, y
