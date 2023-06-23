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

    def phi(self, lmbd, product_list, product_quantities):
        sum = 0
        for i in range(0, len(product_list)):
            sum += product_quantities[i]*(product_list[i].price + lmbd*product_list[i].carb)
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

    def total_price(self, product_quantities_list): 
        pql = product_quantities_list
        tot_price = 0
        for k in range(0, len(product_list)):
            tot_price += self.product_list[k].price * pql[k]
        return tot_price
    

    def function(self, C, lbda, x):
        sum = 0
        for i in range(0, len(self.agent_list)):
            sum += self.agent_list[i].phi(lbda, self.product_list, x[i]) 
        return sum - lbda*C
    
    #on fait le calcul du max sur lmbda 
    def max_lmbda(self, C, x, lmbda_max, N_point = 100):
        x_max = 0
        y_max = -1000000000000000000
        for i in range(0, N_point):
            y = self.function(C, lmbda_max * (i/N_point), x)
            if y_max <= y:
                print(lmbda_max * (i/N_point))
                y_max = y
                x_max = lmbda_max * (i/N_point)
        return x_max, y_max
    
    def min_max_lambd(self, C, lmbda_max):
        x = cp.Variable((len(self.agent_list), len(self.product_list)))
        
        constraints = [x >= 0]
        for i in range(0, len(self.agent_list)):
            constraints.append(self.agent_list[i].u(x) >= 1)
        
        def f(m):
            return self.max_lmbda(C = C,x=m, lmbda_max = lmbda_max)
        
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        return x.value, f(x.value)
    
    #on fait le calcul du min...
    def min_x(self, C, lmbda):
        x = cp.Variable((len(self.agent_list), len(self.product_list)))
        
        constraints = [x >= 0]
        for i in range(0, len(self.agent_list)):
            constraints.append(self.agent_list[i].u(x) >= 1)
        
        def f(m):
            return self.function(C,lmbda, x=m)
        
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        return x.value, f(x.value)
    
    
    def max_min(self, C,lmda_min, lmda_max, N_p):
        x_max = 0
        y_max = -1000000000000000000
        for i in range(0, N_p):
            x, y = self.min_x(C, (lmda_max-lmda_min) * (i/N_p) + lmda_min)
            if y_max <= y:
                print((lmda_max-lmda_min) * (i/N_p) + lmda_min)
                y_max = y
                x_max = (lmda_max-lmda_min) * (i/N_p) + lmda_min
        return x_max, y_max


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

def simple_utility_function(x_t, tho, x): #x_t[i] est la quantité à laquelle une augmentation de dx sera tho fois moins utile que la premiere
    return (x_t + (x)*(1/(tho*tho) - 1)) ** (1/2) -(x_t)**(1/2)

def p(r):
    return 1/r

def utility_function2(ranking, x_t_list, tho_list, x): #ranking[i] < ranking[j] => on prefere i à j. 
    sum2 = 0
    i = 0
    for xi in x:
        sum2 +=  p(ranking[i])* (simple_utility_function(x_t_list[i], tho_list[i], xi))
        i+=1
    return sum2 / n0(ranking, x_t_list, tho_list)

def n0(ranking, x_t_list, tho_list): #ranking[i] < ranking[j] => on prefere i à j. 
    sum2 = 0
    i = 0
    for xi in x_t_list:
        sum2 +=  p(ranking[i])*(simple_utility_function(x_t_list[i], tho_list[i], 1))
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

#pour tho = 0.5
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
x, y = ens.min_max_lambd(100000000, 500)
x, y = ens.max_min(10000,0, 500, 100)
print(x)
