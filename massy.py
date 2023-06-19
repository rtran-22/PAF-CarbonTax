import cvxpy as cp
from functools import partial
import math
import pandas as pd

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

    def le_min(self, C, lmbd):
        print("...")
        x = cp.Variable((len(self.agent_list), len(self.agent_list[0].product_l)))
        constraints = [x >= 0]
        #on ajoute les contraintes
        print("on ajoute les contraintes")
        for i in range(0, len(self.agent_list)):
            print(i)
            constraints.append((self.agent_list[i].u(x[i]) >= 1))
            constraints.append(x[i][0] + x[i][1] + x[i][2] + x[i][3] + x[i][4] + x[i][5] == 1)
        
        def f(m):
            return self.fonc_i(lmbd=lmbd, C=C, product_q_ai=m)
        
        print("objective...")
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()

        print(x.value)

#un exemple

l1 = [1.62, 0.1, 1.2, 1, 0.5, 1, 0.2, 1, 0.2, 1, 0.2, 1]
l2 =  [1.62, 0.1, 0.6, 1, 1.2, 1, 0.4, 1, 0.2, 1, 0.2, 1]
l3 =  [1.62, 0.1, 0.4, 1, 0.6, 1, 0.1, 1, 0.1, 1, 0.1, 1]

def u(l, x):
    s_tmp = 0
    for k in range(0, 6):
        s_tmp += x[k]
    
    return  l[0]*(x[0] + x[1] + l[1])**(0.5) + l[2]*(x[2] + l[3])**(0.5) + l[4]*(2*x[3] + x[4] + l[5])**(0.5) + l[6]*(x[5] + l[7])**(0.5) + l[8]*(x[6] + l[9])**(0.5) - (l[0]*(l[1])**(0.5) + l[2]*(l[3])**(0.5) + l[4]*(l[5])**(0.5) + l[6]*(l[7])**(0.5) + l[8]*(l[9])**(0.5))


elec_car = product(77, 37)
petrol_car = product(50, 92)
bus = product(35, 32)
e_bike = product(15, 8)
bike = product(3, 2)
foot = product(0,0)
choc = product(2,1)

prod_l = [elec_car, petrol_car, bus, e_bike, bike, foot, choc]

agent1 = agent(partial(u, l1), prod_l)
agent2 = agent(partial(u, l2), prod_l)
agent3 = agent(partial(u, l3), prod_l)

ens = commu([agent1, agent2, agent3])

ens.le_min(100000, 0) #pas de limite, pas de taxe
ens.le_min(100, 100) 
