from agent import Pair, Pair_State, Agent, Agent_State
from AGV import Order, Order_State


'''
FILE USED FOR PROTOTYPING AND DEBUGGING SINGLE FUNCTIONS OF THE CODE 
'''
'''
InitPos = []


x = 0
y = 1 
iD = 3 

pos = [x, y, iD]

InitPos.append(pos)



print(InitPos[0][2])
#print(pos)

'''
# GOAL: TODO create a list of lists and access them 
'''
from agent import Pair, Pair_State
agents = 7 

m = agents / 2 
m = int(m)

pairs = []
for i in range(m): 
    pairs.append(Pair(i))


print(len(pairs))

if pairs[0].getState() == Pair_State._Busy:

    print(pairs[0].getState())
else:
    print("busy boiiii")


for pair in pairs:
    print("this is pair ", pair , "and its Id is ",pair.getId())
'''



