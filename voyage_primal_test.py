import cvxpy as cp
import matplotlib.pyplot as plt
import scipy.optimize as opti

class product:
    def __init__(self, name, price, carb):
        self.name = name
        self.price = price
        self.carb = carb 

class agent:
    def __init__(self, name, u, u_satisfait, budget):
        self.name = name
        self.u = u 
        self.u_satisfait = u_satisfait
        self.budget = budget
        self.quantities = 0 
    
    def somme_agent(self, lmbd, product_lst, product_qts):
        sum = 0
        for i in range(0, len(product_lst)):
            sum += product_qts[i]*(product_lst[i].price + lmbd*product_lst[i].carb)
        return sum

class commu:
    def __init__(self, agent_list, product_list):
        self.agent_list = agent_list
        self.product_list = product_list

    def somme_commu(self, C, x, lmbd):
        sum = 0
        for i in range(0, len(self.agent_list)):
            sum += self.agent_list[i].somme_agent(lmbd, self.product_list, x[i]) 
        return sum - lmbd*C
    
    def max_lmbd(self, C, x):
        #def aux(lmbd):
         #   return (-1)*self.somme_commu(C, x, lmbd)
        lmbd = range(0, 500)
        values = [self.somme_commu(C, x, lmbd[i]) for i in range(500)]
        def dernierIndiceMaximum(liste):
            maxi = liste[0]
            longueur=len(liste)
            indice_max = 0
            for i in range(longueur):
                if liste[i] >= maxi:
                    maxi = liste[i]
                    indice_max = i
            return indice_max
        return dernierIndiceMaximum(values)
        #return opti.minimize(aux, x0 = 50)
    
    def min_max_lmbd(self, C):
        x = cp.Variable((len(self.agent_list), len(self.product_list)))
        
        constraints = [x >= 0]
        for i in range(0, len(self.agent_list)):
            constraints.append(self.agent_list[i].u(x[i]) >= 1)
        
        def f(m):
            return self.max_lmbd(C = C, x=m)
        
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        return x.value, f(x.value)

    def presentation_resultat(self, c_list, maxL = 10, N = 4*1000): 
            for c in c_list:
                print("===========================================\n")
                ldbd = self.Dmax_fast(c, 0, maxL, N, 400)
                x, y = self.D(ldbd, c)
                print(x)
                print("LAMBDA = " + str(ldbd) + "; C = " + str(c) + "kg ; total carbone : " + str(self.carbon_total(x)) + "kg") 
                for i in range(0, len(x)):
                    print(self.agent_list[i].name + "> expenses : " + str(round(self.total_price(x[i]))) + " ; budget : " + str(round(self.agent_list[i].budget)))
                    for j in range(0, len(x[i])):
                        print(self.product_list[j].name + " : " + str(round(x[i][j], 1)))
                    print("")
                print("")

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
    sum2 = 0
    i = 0
    for xi in x_t_list:
        sum2 +=  p(ranking[i])*(simple_utility_function(x_t_list[i], tau_list[i], 1))
        i+=1
    return sum2


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
#ens.presentation_resultat([19000, 1000000])
x, y = ens.min_max_lmbd(100000000)
#x, y = ens.max_min(10000,0, 500, 100)
print(x)
