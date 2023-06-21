import cvxpy as cp
from functools import partial
import math
import matplotlib.pyplot as plt
from math import log as ln

class product:
    def __init__(self, price, carb):
        self.price = price
        self.carb = carb

class agent:
    def __init__(self, u, product_l, coefs, budget):
        self.u = u 
        self.product_l = product_l
        self.coefs = coefs
        self.budget = budget
    
    def fonc(self, lmbd, product_q): #pour chaque agent, on fait le calcul de sa fonction connaissant lambda et la quantité de produit
        sum = 0
        for i in range(0, len(self.product_l)):
            sum += lmbd*product_q[i]*(self.product_l[i].carb) 
        return sum - self.u(product_q)

    def somme_depenses(self, product_q):
        sum = 0
        i = 0
        for p in product_q:
            sum += p*(self.product_l[i].price)
            i += 1
        return sum
        
class commu:
    def __init__(self, agent_list):
        self.agent_list = agent_list
    
    def fonc_i(self, lmbd, C, x_mat):
        sum = 0
        for k in range(0, len(self.agent_list)):
            sum += self.agent_list[k].fonc(lmbd, x_mat[k])
        sum = sum - lmbd*C
        return sum
    

    def D(self, C, lmbd):
        x = cp.Variable((len(self.agent_list), len(self.agent_list[0].product_l)))
        
        constraints = [x >= 0]
        #on ajoute les contraintes
        for i in range(0, len(self.agent_list)):
            constraints.append(self.agent_list[i].somme_depenses(x[i]) <= self.agent_list[i].budget)
            constraints.append(x[i][0] + x[i][1] + x[i][2] + x[i][3] == 1)
        
        def f(m):
            return self.fonc_i(lmbd=lmbd, C=C, x_mat=m)
        
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        
        print(x.value)
        return f(x.value)

        

  

#MODELE 

def u(l, x):
    sum = 0
    for i in range(NB_DESTINATIONS):
        sum += l[2*i]*(x[i]+l[2*i+1])**0.5 - l[2*i]*(l[2*i+1])**0.5
    return sum
        

#MODELE NUMERIQUE 

NB_DESTINATIONS = 4

#DESTINATIONS : prix = prix d'un aller-retour

FRANCE = product(150, 1)
JAPON = product(1200, 700)
USA = product(400, 350)
ALLEMAGNE = product(275, 30)
SUISSE = ...

prod_l = [FRANCE, JAPON, USA, ALLEMAGNE]

l1 = [1.6, 1, 0.3, 0.1, 0.3, 1.5, 1, 0.8] #Veut rester en France et riche 
l2 = [0.8, 1, 1.2, 0.1, 1.6, 0.3, 0.8, 0.8] #Se faire de la thune et riche
l3 = [1, 1, 1, 0.1, 1, 0.3, 1, 0.8] #N'a pas d'argent et osef
agent1 = agent(partial(u, l1), prod_l, l1, 30000)
agent2 = agent(partial(u, l2), prod_l, l2, 30000)
agent3 = agent(partial(u, l3), prod_l, l3, 1500)

ens = commu([agent1, agent2, agent3])
ens.D(10000, 15)

l = [g/10 for g in range(0,100)]
#for g in l:
#    print("D(" + str(g/200) +") = "+ str(ens.D(100, g/200)))

'''plt.plot(l, [ens.D(100, g) for g in l])
plt.plot(l, [ens.D(75, g) for g in l])
plt.plot(l, [ens.D(50, g) for g in l])
'''
plt.show()
