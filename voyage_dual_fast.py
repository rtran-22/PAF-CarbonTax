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

    def phi(self, product_quantities, product_list, lmbda):
        sum = 0
        #print(self.name)
        #print("product_list")
        #print(product_list)
        #print("product_q")
        #print(product_quantities)
        for i in range(0, len(product_list)):
            sum += product_quantities[i]*(product_list[i].price + lmbda*product_list[i].carb)
        return sum
    
    def min_phi(self, product_list, lmbda):
        x = cp.Variable(len(product_list))
        #print(x)
        constraints = [x >= 0]
        constraints.append(lmbda >= 0)
        constraints.append(self.u(x) >= self.u_satisfait)

        def f(m):
            return self.phi(m, product_list, lmbda=lmbda)
        
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        #print(x.value)
        return (x.value, f(x.value))

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

    """
    def carbon_total(self, x):
        c_tot = 0
        for i in range(0, len(self.agent_list)):
            j = 0
            for xi in x[i]:
                c_tot += self.product_list[j].carb*xi
                j += 1
        return c_tot
    """

    def D(self, lmbd, C):
        sum = 0
        l = []
        for j in range(0, len(self.agent_list)):
            x, y = self.agent_list[j].min_phi(self.product_list, lmbd)
            sum = sum + y
            l.append(x)
        return (sum - lmbd*C), l
    
    def fAux(self, x0, x1, N, C):
        x = [x0 + (x1-x0) * i / N for i in range(0,N+1)]
        y_tmp = -10000000
        for i in range(0, len(x)):
            y, x_list = self.D(x[i], C)
            if (y_tmp - y) >= 0:
                return x[i-1], x[i]
            else:
                y_tmp = y
        return x[N-1], x[N-1]

    def Dmax_fast(self, C, x0, x1, N1, N2):
        for i in range(0, N2):
            x0, x1 = self.fAux(x0, x1, N1, C)
            if abs((x1-x0)) < 0.0000001:
                return (x0 + x1)/2
        return (x0 + x1)/2
    
    def presentation_resultat(self, c_list, maxL = 500, N = 100): 
        for c in c_list:
            print("===========================================\n")
            ldbd = self.Dmax_fast(c, 0, maxL, N, 150)
            y, x = self.D(ldbd, c)
            print("")
            print("LAMBDA = " + str(round(ldbd*1000, 10)) + "e/t ; C = " + str(c) + "kg ; total carbone : " + str(self.carbon_total(x)) + "kg") 
            for i in range(0, len(x)):
                #print(self.agent_list[i].name + "> expenses : " + str(round(self.total_price(x[i]))) + " ; budget : " + str(round(self.agent_list[i].budget)))
                print(self.agent_list[i].name)

                for j in range(0, len(x[i])):
                    print(self.product_list[j].name + " : " + str(round(abs(x[i][j]), 1)))
                print("")
            print("")
        
    def lmbda(self, Cmin, Cmax, N_pas):
        c = []
        lbda_l = []
        for i in range(0, N_pas):
            print(i)
            ci = Cmin + ((Cmax - Cmin)/N_pas) * i
            c.append(ci)
            ldbd = self.Dmax_fast(ci, 0, 500, 30, 100)
            lbda_l.append(ldbd)

        plt.plot(c, lbda_l)
        plt.grid()
        plt.title("lambda en fonction de C")
        plt.xlabel("C (kg)")
        plt.ylabel("lambda ($/kg)")
        plt.show()


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
ens.presentation_resultat([10000])

#ens.lmbda(6000, 7000, 75)
