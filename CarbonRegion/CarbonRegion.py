import cvxpy as cp
from functools import partial
import math
import pandas as pd
import matplotlib.pyplot as plt

class sector:
    def __init__(self, price, carb):
        self.price = price
        self.carb = carb

class agent:
    def __init__(self, u, product_l):
        self.u = u 
        self.product_l = product_l
    
    def fonc(self, lmbd, product_q): #pour chaque agent, on fait le calcul de sa fonction connaissant lambda et la quantité de produit
        sum = 0
        for i in range(0, len(self.product_l)):
            sum += product_q[i]*(self.product_l[i].price + lmbd*self.product_l[i].carb)
        return sum
            
    
class commu:
    def __init__(self, agent_list):
        self.agent_list = agent_list
    
    def fonc_i(self, lmbd, C, product_q_ai):
        sum = 0
        for k in range(0, len(self.agent_list)):
            sum += self.agent_list[k].fonc(lmbd, product_q_ai[k])
        sum = sum - lmbd*C
        return sum

    def D(self, C, lmbd):
        x = cp.Variable((len(self.agent_list), len(self.agent_list[0].product_l)))
        
        constraints = [x >= 0]
        #on ajoute les contraintes
        for i in range(0, len(self.agent_list)):
            constraints.append((self.agent_list[i].u(x[i]) >= 1))
            constraints.append(x[i][0] + x[i][1] + x[i][2] + x[i][3] + x[i][4] + x[i][5] == 1)
        
        def f(m):
            return self.fonc_i(lmbd=lmbd, C=C, product_q_ai=m)
        
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        
        #print(x.value)
        return f(x.value)

        

    

#Cas du gouvernement et des régions : L'objectif pour le gouvernement est de fixer la taxe carbone optimale
#pour des régions qui ont des objectifs économiques et des caractéristiques différentes (pop, secteurs d'activités...)

idf = [1.62, 0.1, 1.2, 1, 0.5, 1, 0.2, 1, 0.2, 1, 0.2, 1]
auvergne =  [1.62, 0.1, 0.6, 1, 1.2, 1, 0.4, 1, 0.2, 1, 0.2, 1]
provence =  [1.62, 0.1, 0.4, 1, 0.6, 1, 0.1, 1, 0.1, 1, 0.1, 1]
bretagne =  [1.62, 0.1, 0.4, 1, 0.6, 1, 0.1, 1, 0.1, 1, 0.1, 1]
paysdelaloire = []
corse = []
def u(l, x):
    s_tmp = 0
    for k in range(0, 6):
        s_tmp += x[k]
    return  l[0]*(x[0] + l[1])**(0.5) + l[2]*(x[2] + l[3])**(0.5) + l[4]*(2*x[3] + x[4] + l[5])**(0.5) + l[6]*(x[5] + l[7])**(0.5) + l[8]*(x[6] + l[9])**(0.5) - (l[0]*(l[1])**(0.5) + l[2]*(l[3])**(0.5) + l[4]*(l[5])**(0.5) + l[6]*(l[7])**(0.5) + l[8]*(l[9])**(0.5))


agricultur = sector(77, 37)
industry = sector(50, 92)
services = sector(35, 32)

sector_l = [agricultur, industry, services]

agent1 = agent(partial(u, idf), sector_l)
agent2 = agent(partial(u, auvergne), sector_l)
agent3 = agent(partial(u, provence), sector_l)
agent4 = agent(partial(u, bretagne), sector_l)
agent5 = agent(partial(u, paysdelaloire), sector_l)
agent6 = agent(partial(u, corse), sector_l)


ens = commu([agent1, agent2, agent3, agent4, agent5, agent6])


l = [g/10 for g in range(0,100)]
#for g in l:
#    print("D(" + str(g/200) +") = "+ str(ens.D(100, g/200)))

plt.plot(l, [ens.D(100, g) for g in l])
plt.plot(l, [ens.D(75, g) for g in l])
plt.plot(l, [ens.D(50, g) for g in l])

plt.show()
