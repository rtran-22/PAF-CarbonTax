import cvxpy as cp
from functools import partial
import math
import pandas as pd
import matplotlib.pyplot as plt

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
    def __init__(self, agent_list, product_list):
        self.agent_list = agent_list
        self.product_list = product_list
    
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
        print(x.value)
        return f(x.value)
    
    #Lagrange Multiplier
    def tot_emission(self, x):
        sum = 0
        for i in range(0, len(self.agent_list)):
            for j in range(0, len(self.product_list)): 
                sum += x[i][j] * self.product_list[j].carb
        return sum
    
    def lmbdak(self, lmbda_old, k, gam, C, x_old):
        carb_emission = self.tot_emission(x_old)
        return max(0, lmbda_old + gam(k)*(carb_emission - C))
    
    def xk(self, lmbda, k, C):
        #on veut argmin de D(x, lmbda_old)...
        x = cp.Variable((len(self.agent_list), len(self.agent_list[0].product_l)))
        constraints = [x >= 0]
        #on ajoute les contraintes
        for i in range(0, len(self.agent_list)):
            constraints.append((self.agent_list[i].u(x[i]) >= 1))
            constraints.append(x[i][0] + x[i][1] + x[i][2] + x[i][3] + x[i][4] + x[i][5] == 1)
        
        def f(m):
            sum = 0
            for i in range(0, len(self.agent_list)):
                for j in range(0, len(self.product_list)): 
                    sum += m[i][j] * self.product_list[j].price
            return sum + self.tot_emission(m)*lmbda - lmbda*C
        
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        return x.value
    
    def distance(self, x, y):
        sum = 0
        for i in range(0, len(x)):
            for j in range(0, len(x[0])):
                sum += abs(x[i][j] - y[i][j])
        return sum
    
    def lagrange_multilplier_m(self, gam, C, eps_lmbd = 0.0000001, eps_x = 0.000001):
        #on prend lmbda0 = 0
        
        
        lmbda1 = - C * gam(1)
        
        
        lmbda_old = lmbda1
        x_old = [[0 for i in range(0, len(self.product_list))] for j in range(0, len(self.agent_list))]

        k = 1

        b = True
        while b:
            x_new = self.xk(lmbda_old, k, C)
            lmbda_new = self.lmbdak(lmbda_old, k, gam, C, x_new)
        

            #c1 = (abs(lmbda_old-lmbda_new) <= eps_lmbd)
            c2 = (self.distance(x_new, x_old) <= eps_x)
            print(self.distance(x_new, x_old))

            if c2:
                b = False
                print(lmbda_new)
                print(x_new)
                return lmbda_old
            
            #print(lmbda_new)
            x_old = x_new.copy()
            lmbda_old = lmbda_new
            #print(lmbda_old)
            k = k+1

        print(lmbda_old)
        print(x_old)
        return lmbda_old


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

ens = commu([agent1, agent2, agent3], prod_l)

def maxfoncf(C, maxl, minl, N_val):
    print(C)
    x = [minl + (maxl - minl)*i/N_val for i in range(0, N_val-1)]
    x_max = 0
    y_max = -10000
    y = [ens.D(C, g) for g in x]
    for i in range(0, len(y)):
        if y_max < y[i]:
            y_max = y[i]
            x_max = x[i]
    print(ens.D(C, x_max))
    return x_max


def gam(x):
    return 1/(x+10)**2

#print("\n\n\nLambda : " + str(maxfoncf(100, 0, 5, 100)))

ens.lagrange_multilplier_m(gam, 100, 0.00001, 0.00001)
#C = [x for x in range(40, 70)]
#plt.plot(C, [max(c, 50, 0, 40) for c in C])
#plt.show()
