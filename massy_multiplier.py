import cvxpy as cp
from functools import partial
import math
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
    
    def function(self, C, lbda, x):
        sum = 0
        for j in range(0, len(self.agent_list)):
            for i in range(0, len(self.product_list)):
                sum += x[j][i]*self.product_list[i].price - lbda*x[j][i]*self.product_list[i].carb
        return sum - lbda*C
    
    def carbon_total(self, x):
        c_tot = 0
        for i in range(0, len(self.agent_list)):
            j = 0
            for xi in x[i]:
                c_tot += self.product_list[j].carb*xi
                j += 1
        return c_tot
    
    def D(self, C, lmbd):
        x = cp.Variable((len(self.agent_list), len(self.agent_list[0].product_l)))
        
        constraints = [x >= 0]
        #on ajoute les contraintes
        for i in range(0, len(self.agent_list)):
            constraints.append((self.agent_list[i].u(x[i]) >= 1))
            constraints.append(x[i][0] + x[i][1] + x[i][2] + x[i][3] + x[i][4] + x[i][5] == 1)
        
        def f(m):
            return self.function(lmbd=lmbd, C=C, product_q_ai=m)
        
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
            
        print(x.value)
        return f(x.value)

    def total_price(self, product_quantities_list): 
        pql = product_quantities_list
        tot_price = 0
        for k in range(0, len(self.product_list)):
            tot_price += self.product_list[k].price * pql[k]
        
        return tot_price

    def Dk(self, lbd, C):
        x = cp.Variable((len(self.agent_list), len(self.product_list)))
        constraints = [x >= 0]
        for i in range(0, len(self.agent_list)):
            constraints.append((self.agent_list[i].u(x[i]) >= 1))
            constraints.append(x[i][0] + x[i][1] + x[i][2] + x[i][3] + x[i][4] + x[i][5] == 1)

        def f(m):
            return self.function(C = C, lbda=lbd, x=m)
        
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        print(x.value)
        return x.value
    
    def lbd_aux(self, lbd, x, k, gam, C):
        sum = 0
        for i in range(len(self.agent_list)):
            for j in range(len(self.product_list)):
                sum += x[i][j] * self.product_list[i].carb 
        return max(0, lbd + gam(k)*(sum - C))

    def distance_aux(self, x_new, x_old):
        sum = 0
        for i in range(len(x_new)):
            for j in range(len(x_new[0])):
                sum += abs(x_new[i][j] - x_old[i][j])
        #print(sum)
        return sum 

    def lag_multiplier(self, gam, C, lbd_old = 0, eps_x = 0.0001, eps_lbd = 0.0001):
        x_old = self.Dk(lbd_old, C)
        b = True
        k = 0
        while b:
            lbd_new = self.lbd_aux(lbd_old, x_old, k, gam, C)
            x_new = self.Dk(lbd_new, C)
            if (self.distance_aux(x_new, x_old) < eps_x) and (abs(lbd_new - lbd_old) < eps_lbd):
                b = False
            lbd_old = lbd_new
            x_old = x_new
            print(lbd_new)
            print(k)
            k += 1
        #print("finito")
        #print(lbd_new, x_new)
        print(lbd_new)
        return lbd_new, x_new

        

    

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

def gam(k):
    return 1/(k+1)**2

#for g in l:
#    print("D(" + str(g/200) +") = "+ str(ens.D(100, g/200)))

'''plt.plot(l, [ens.D(100, g) for g in l])
plt.plot(l, [ens.D(75, g) for g in l])
plt.plot(l, [ens.D(50, g) for g in l])

#plt.show()'''

ens.lag_multiplier(gam, 100)