import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 


data1 = [80.58, 128.58, 20.70, 57.96, 43.58, ]
expSc1 = [1, 2, 3, 4, 5]

data2 = [155.32, 205, 100.87, 119.7, 85.99, 66.7]
expSc2 = [6, 7, 8, 9, 10, 11 ]



# map 51x51 

# sc 1   1-3-4-5 

# sc 2 6-8-9-10-11 



x =[0, 1, 2, 3]

y1 = [data1[0], data1[2], data1[3], data1[4]]

y2 = [data2[0], data2[2], data2[3], data2[4]]





plt.plot(x, y1, label = "lambda Sc 1")
plt.scatter(x, y1)
plt.plot(x, y2, label = "lambda Sc 2")
plt.scatter(x, y2)
plt.grid(True)
plt.xlabel('Comparable Experiments [n]')
plt.ylabel('Time-steps [s]')
plt.xticks(np.arange(4), ['1 vs 6', '3 vs 8', '4 vs 9', '5 vs 10']) 
#plt.set_xlim(1, 5)
plt.legend()
plt.show()
plt.close()




## RSD graph 

y3 = [34.148, 3.74, 35.417, 25.790 ] # scenario 1 
y4 = [41.406, 17.631, 30.556, 22.883]

plt.plot(x, y3, label = "RSD Sc 1")
plt.scatter(x, y3)
plt.plot(x, y4, label = "RSD Sc 2")
plt.scatter(x, y4)
plt.grid(True)
plt.xlabel('Comparable Experiments [n]')
plt.ylabel('Time-steps [s]')
plt.xticks(np.arange(4), ['1 vs 6', '3 vs 8', '4 vs 9', '5 vs 10']) 
#plt.set_xlim(1, 5)
plt.legend()



plt.show()
plt.close()


# avg total operated distance 
y5 = [119.86, 59.33, 97.24, 82.86 ] # scenario 1 
y6 = [195.62, 141.17, 160, 126.29] # sc 2

plt.plot(x, y5, label = "Avg total dist Sc 1")
plt.scatter(x, y5)
plt.plot(x, y6, label = "Avg total dist Sc 2")
plt.scatter(x, y6)
plt.grid(True)
plt.xlabel('Comparable Experiments [n]')
plt.ylabel('Time-steps [s]')
plt.xticks(np.arange(4), ['1 vs 6', '3 vs 8', '4 vs 9', '5 vs 10']) 
#plt.set_xlim(1, 5)
plt.legend()



plt.show()
plt.close()



# Simulation time 


y7 = [276, 63, 237, 219] # scenario 1 
y8 = [374, 199, 301, 276]

plt.plot(x, y7, label = "Simulation time Sc 1")
plt.scatter(x, y7)
plt.plot(x, y8, label = "Simulation time Sc 2")
plt.scatter(x, y8)
plt.grid(True)
plt.xlabel('Comparable Experiments [n]')
plt.ylabel('Time-steps [s]')
plt.xticks(np.arange(4), ['1 vs 6', '3 vs 8', '4 vs 9', '5 vs 10']) 
#plt.set_xlim(1, 5)
plt.legend()



plt.show()
plt.close()

