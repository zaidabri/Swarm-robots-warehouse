

import numpy as np
import tcod #python3 -m pip install --user tcod

# graph = tcod.path.CustomGraph((5, 5))
# cost = np.ones((5, 5), dtype=np.int8)
# CARDINAL = [[0, 1, 0],[1, 0, 1],[0, 1, 0],]
# graph.add_edges(edge_map=CARDINAL, cost=cost)
# pf = tcod.path.Pathfinder(graph)
# pf.add_root((0, 0))
# pf.resolve()
# pf.distance
# print(pf.path_to((3, 3)))

class Pathfinder:

    def prepareGraph(self, graph, start):
        # Change 0, P and D to 1, because 0 are obstacles here
        for i in range(len(graph)):
            for j in range(len(graph[i])):
                if graph[i][j] == 0 or isinstance(graph[i][j], str) and ("P" in graph[i][j] or "D" in graph[i][j]):
                    if isinstance(graph[i][j], str) and "A" in graph[i][j]:
                        continue
                    graph[i][j] = 1

        print("graph1",graph)
        # Change neighbour agents to 0 because they are obstacles


        x = start[0]
        y = start[1]

        print("XY",x,y)

        print(graph[x-1][y])
        #print(graph[x+1][y])
        print(graph[x][y-1])
        #print(graph[x][y+1])


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

        print("graph2",graph)

        # Change not neighbour agents to 1 because they not obstacles
        for i in range(len(graph)):
            for j in range(len(graph[i])):
                if isinstance(graph[i][j], str) and "A" in graph[i][j]:
                    graph[i][j] = 1

        print("graph3",graph)

        # Change * to 0 for obstacles
        for i in range(len(graph)):
            for j in range(len(graph[i])):
                if graph[i][j] == "*":
                    graph[i][j] = 0

        print("graph4",graph)

        return graph

    def getNextMove(self):
        return self.x, self.y

    def solve(self, agentId, graph, start, end):
        print("Before",agentId,graph)
        print("start",start)
        print("end",end)
        graph = self.prepareGraph(graph, start)
        print("After",agentId,graph)
        graph = graph.astype(dtype=np.int8, order="F")
        graph = tcod.path.SimpleGraph(cost=graph,cardinal=1,diagonal=0)
        pf = tcod.path.Pathfinder(graph)
        pf.add_root(start)
        pf.resolve()
        solution = pf.path_to(end)

        if len(solution) > 1:
            self.x = np.uint32(solution[1][0]).item()
            self.y = np.uint32(solution[1][1]).item()
            return True
        else:
            return False
