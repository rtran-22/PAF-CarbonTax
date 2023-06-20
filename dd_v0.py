import cvxpy as cp
from functools import partial
import math
import pandas as pd
import matplotlib.pyplot as plt
from math import log as ln

class product:
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

        

    

#MODELE 

def u(l, x):
    prod = 1
    for i in range(NB_DESTINATIONS):
        prod *= (x[i]+l[2*i+1])**l[2*i]
    return ln(prod)
        

#MODELE NUMERIQUE 

NB_DESTINATIONS = 4

#DESTINATIONS : prix = prix d'un aller-retour

FRANCE = product(150, 1)
JAPON = product(1200, 700)
USA = product(400, 350)
ALLEMAGNE = product(275, 30)

prod_l = [FRANCE, JAPON, USA, ALLEMAGNE]

agent1 = agent(partial(u, l1), prod_l)
agent2 = agent(partial(u, l2), prod_l)
agent3 = agent(partial(u, l3), prod_l)

ens = commu([agent1, agent2, agent3])


l = [g/10 for g in range(0,100)]
#for g in l:
#    print("D(" + str(g/200) +") = "+ str(ens.D(100, g/200)))

plt.plot(l, [ens.D(100, g) for g in l])
plt.plot(l, [ens.D(75, g) for g in l])
plt.plot(l, [ens.D(50, g) for g in l])

plt.show()
