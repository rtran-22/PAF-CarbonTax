import cvxpy as cp
import matplotlib.pyplot as plt
from math import exp 
import numpy.linalg


class product:
    def __init__(self, name, price, carb):
        self.name = name
        self.price = price
        self.carb = carb

class agent:
    def __init__(self,name, u, budget):
        self.u = u
        self.budget = budget
        self.name = name

class commu:
    def __init__(self, agent_list, product_list):
        self.agent_list = agent_list
        self.product_list = product_list
    
    def carbon_total(self, x):
        c_tot = 0
        for i in range(0, len(self.agent_list)):
            j = 0
            for xi in x[i]:
                c_tot += self.product_list[j].carb*xi
                j += 1
        return c_tot
    
    def total_price(self, product_quantities_list): 
        pql = product_quantities_list
        tot_price = 0
        for k in range(0, len(product_list)):
            tot_price += self.product_list[k].price * pql[k]
        
        return tot_price

    def function(self, C, lbda, x):
        sum = 0
        for i in range(0, len(self.agent_list)):
            sum += (-1) * self.agent_list[i].u(x[i]) + lbda*(self.carbon_total(x) - C)
        return sum
    
    def Dk(self, lbd, C):
        x = cp.Variable((len(self.agent_list), len(self.product_list)))
        constraints = [x >= 0]
        for i in range(0, len(self.agent_list)):
            constraints.append((self.total_price(x[i]) <= self.agent_list[i].budget))

        def f(m):
            return self.function(C = C, lbda=lbd, x=m)
        
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
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
        print(sum)
        return sum 

    
    def lag_multiplier(self, gam, C, lbd_old = 100, eps_x = 0.00001, eps_lbd = 1e-5):
        x_old = self.Dk(lbd_old, C)
        b = True
        k = 0
        while b:
            lbd_new = self.lbd_aux(lbd_old, x_old, k, gam, C)
            x_new = self.Dk(lbd_new, C)
            print(numpy.linalg.norm(x_new-x_old))
            if (numpy.linalg.norm(x_new-x_old) <= 1e-8):
                b = False
            lbd_old = lbd_new 
            x_old = x_new
            k += 1
        print("finito")
        print(lbd_new, x_new)
        return lbd_new, x_new
    

    def presentation_resultat(self, c_list, maxL = 10, N = 1000*2): 
        for c in c_list:
            print("===========================================\n")
            ldbd = self.Dmax_fast(c, 0, maxL, N, 400)
            x, y = self.D(ldbd, c)
            print("")
            print("LAMBDA = " + str(ldbd) + "; C = " + str(c) + "kg ; total carbone : " + str(self.carbon_total(x)) + "kg") 
            for i in range(0, len(x)):
                print(self.agent_list[i].name + "> expenses : " + str(round(self.total_price(x[i]))) + " ; budget : " + str(round(self.agent_list[i].budget)))
                for j in range(0, len(x[i])):
                    print(self.product_list[j].name + " : " + str(round(x[i][j], 1)))
                print("")
            print("")



def simple_utility_function(x_t, tho, x): #x_t[i] est la quantité à laquelle une augmentation de dx sera tho fois moins utile que la premiere
    return x_t*(1 + (x/x_t)*(1/(tho*tho) - 1)) ** (1/2)

def utility_function2(ranking, x_t_list, tho_list, x): #ranking[i] < ranking[j] => on prefere i à j. 
    sum2 = 0.0
    i = 0
    for xi in x:
        sum2 +=  (1/ranking[i]) * simple_utility_function(x_t_list[i], tho_list[i], xi)
        i+=1
    return sum2

def gam(k):
    return 1/(k+100)

france = product("france", 1995,887)
us = product("us",3737,5963)
germany = product("germany", 1957,1954)
canada = product("canada", 3618,5580)
switzerland = product("switzerland", 3462,961)
japan = product("japan", 4594, 5822)

product_list = [france, us, germany, canada, switzerland, japan]


r1 = [1, 6, 2, 5, 3, 4] #j'adore l'europe
r2 = [6, 1, 5, 2, 4, 3] #j'adore les us, canada...

#pour tho = 0.5

x_t1 = [1, 1, 5, 1, 5, 5] #en gros, commence à moins aimer ger, swi et jap au bout de 5 voyages, le reste des le 1er
x_t2 = [3, 3, 3, 3, 3, 3]

def u1(x):
    t = 0.5
    return utility_function2(r1, x_t1, [t,t,t,t,t,t], x)

def u2(x):    
    t = 0.5
    return utility_function2(r2, x_t2, [t,t,t,t,t,t], x)

agent_europe = agent("M. Europe", u1, 15000) #moins riche
agent_us = agent("Mme. US", u2, 100000) #riche

ens = commu([agent_europe, agent_us], product_list=product_list)

ens.lag_multiplier(gam, 10000)