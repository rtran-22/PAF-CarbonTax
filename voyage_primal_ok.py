import cvxpy as cp
import matplotlib.pyplot as plt 


class product:
    def __init__(self, name, price, carb):
        self.name = name
        self.price = price
        self.carb = carb

class agent:
    def __init__(self,name, u, u_satisfsait, budget):
        self.u = u
        self.budget = budget
        self.name = name
        self.quantities = 0
        self.u_satisfait = u_satisfsait

    def phi(self, product_quantities, product_list):
        sum = 0
        for i in range(0, len(product_list)):
            sum += product_list[i].price*product_quantities[i]
        return sum


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


    def min_depenses(self, C):
        x = cp.Variable((len(self.agent_list), len(self.product_list)))
        constraints = [x >= 0]
        constraints.append(self.carbon_total(x) <= C)
        
        for i in range(len(self.agent_list)):
            constraints.append(self.agent_list[i].u(x[i]) >= self.agent_list[i].u_satisfait)

        def f(m):
            sum = 0 
            for i in range(len(self.agent_list)):
                sum += self.agent_list[i].phi(m[i], self.product_list)
            return sum
        
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        print(x.value)
        print(f(x.value))
        return (x.value, f(x.value))
    


def simple_utility_function(x_t, tau, x): #x_t[i] est la quantité à laquelle une augmentation de dx sera tau fois moins utile que la premiere
    return (x_t + (x)*(1/(tau*tau) - 1)) ** (1/2) -(x_t)**(1/2)

def p(r):
    return 1/r

def utility_function2(ranking, x_t_list, tau_list, x): #ranking[i] < ranking[j] => on prefere i à j. 
    sum2 = 0
    i = 0
    for xi in x:
        sum2 +=  p(ranking[i])* (simple_utility_function(x_t_list[i], tau_list[i], xi))
        i+=1
    return sum2 / n0(ranking, x_t_list, tau_list)

def n0(ranking, x_t_list, tau_list): #ranking[i] < ranking[j] => on prefere i à j. 
    sum = 0
    i = 0
    for xi in x_t_list:
        sum +=  p(ranking[i])*(simple_utility_function(x_t_list[i], tau_list[i], 1))
        i+=1
    return sum


france = product("france", 1995,887)
us = product("us",3737,5963)
germany = product("germany", 1957,1954)
canada = product("canada", 3618,5580)
switzerland = product("switzerland", 3462,961)
japan = product("japan", 4594, 5822)

product_list = [france, us, germany, canada, switzerland, japan]

r1 = [1, 6, 2, 5, 3, 4] #j'adore l'europe
r2 = [6, 1, 5, 2, 4, 3] #j'adore les us, canada...
r3 = [1, 1, 1, 1, 1, 1] #je m'en moque

#pour tau = 0.5
N = 2 #je m'en lasse pas !

x_t1 = [(N), 1, 1, 1, 1, 1] #en gros, commence à moins aimer ger, swi et jap au bout de 5 voyages, le reste des le 1er
x_t2 = [1, (N), 1, 1, 1, 1]
x_t3 = [N/6, N/6, N/6, N/6, N/6, N/6]


def u1(x):
    t = 0.5
    return utility_function2(r1, x_t1, [t,t,t,t,t,t], x)

def u2(x):    
    t = 0.5
    return utility_function2(r2, x_t2, [t,t,t,t,t,t], x)

def u3(x):
    t = 0.5
    return utility_function2(r3, x_t3, [t,t,t,t,t,t], x)


agent_europe = agent("M. Europe", u1, 0.6, 10000) #moins riche
agent_us = agent("Mme. US", u2, 0.8, 10000) #met du temps à être satisfait
agent_sp = agent("M. ???", u3, 0.6, 10000) #
ens = commu([agent_europe, agent_us, agent_sp], product_list=product_list)

cop = 3 * 2000
#ens.presentation_resultat([7500, 7600, 7800, 7900, 8000, 8100, 10000])
ens.min_depenses(19000)


#ens.lmbda(6000, 7000, 75)