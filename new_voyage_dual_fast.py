import cvxpy as cp
import matplotlib.pyplot as plt
import random 
import time
import math

class product:
    def __init__(self, name, price, carb):
        self.name = name
        self.price = price
        self.carb = carb

class agent:
    def __init__(self,name, u_satisfsait, r_list, xt_list, t_list):
        self.name = name
        self.r_list = r_list
        self.xt_list = xt_list
        self.t_list = t_list
        self.u_satisfait = u_satisfsait

    def copy(self):
        return agent(self.name, self.u_satisfait, self.r_list, self.xt_list, self.t_list)
    

    def u(self, xi_list):
        return self.utility_function(self.r_list, self.xt_list, self.t_list, xi_list)

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
        sum = 0
        for k in range(0, len(product_list)):
            sum+=x[k]

        constraints.append(sum == 1)
        def f(m):
            return self.phi(m, product_list, lmbda=lmbda)
        
        objective = cp.Minimize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        #print(x.value)
        return (x.value, f(x.value))
    
    def simple_utility_function(self, x_t, t, x): #x_t[i] est la quantité à laquelle une augmentation de dx sera tho fois moins utile que la premiere
        return (x_t + (x)*(1/(t*t) - 1)) ** (1/2) -(x_t)**(1/2)
    
    def p(self, r):
        return 1/r
    
    def utility_function(self, ranking, x_t_list, tho_list, x): #ranking[i] < ranking[j] => on prefere i à j. 
        sum = 0
        i = 0
        for xi in x:
            sum +=  self.p(ranking[i])* (self.simple_utility_function(x_t_list[i], tho_list[i], xi))
            i+=1
        return sum / self.n0(ranking, x_t_list, tho_list)
    
    def n0(self, ranking, x_t_list, tho_list): #ranking[i] < ranking[j] => on prefere i à j. 
        sum = 0
        i = 0
        for xi in x_t_list:
            sum += self.p(ranking[i])*(self.simple_utility_function(x_t_list[i], tho_list[i], 1))
            i+=1
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
        for k in range(0, len(self.product_list)):
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
        def f(x):
            sum = 0
            for i in range(0, len(self.agent_list)):
                for j in range(0, len(self.product_list)):
                    sum += x[i][j]*self.product_list[j].price
            print(sum)

        for c in c_list:
            print("===========================================\n")
            ldbd = self.Dmax_fast(c, 0, maxL, N, 150)
            y, x = self.D(ldbd, c)
            print("")
            print("LAMBDA = " + str(round(ldbd*1000, 10)) + "e/t ; C = " + str(c) + "kg ; total carbone : " + str(self.carbon_total(x)) + "kg") 
            f(x)
            for i in range(0, len(x)):
                #print(self.agent_list[i].name + "> expenses : " + str(round(self.total_price(x[i]))) + " ; budget : " + str(round(self.agent_list[i].budget)))
                print(self.agent_list[i].name)
                for j in range(0, len(x[i])):
                    print(self.product_list[j].name + " : " + str(round(x[i][j], 2)))
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
    
    def C_infini(self):
        INFINI = 1000000000000000000000000000
        ldbd = self.Dmax_fast(INFINI, 0, 500, 100, 20)
        y, x = self.D(ldbd, INFINI)
        return self.carbon_total(x)


class generateur:
    def __init__(self, agent_type_list, N_agent_list):
        self.agent_type_list = agent_type_list
        self.N_agent_list = N_agent_list
        self.product_list = []
        self.agent_list = []
        self.ens = 0
    
    def lancement(self):
        for i in range(len(self.agent_type_list)):
            for j in range(0, self.N_agent_list[i]):
                self.agent_list.append(self.agent_type_list[i].copy())
        file = open("expo", "r")
        data = file.read()
        l = data.split("\n")
        for ls in l:
            ligne = ls.split(";")
            self.product_list.append(product(ligne[0], float(ligne[1]), float(ligne[2])))
        self.ens = commu(agent_list=self.agent_list, product_list=self.product_list)
        print("===============================\n")
        print("conso de carbone pour cet ensemble : " + str(round(self.ens.C_infini()/1000, 2)) + "t")
    
    
    def lancement_random(self, N):
        file = open("expo", "r")
        data = file.read()
        l = data.split("\n")
        for ls in l:
            ligne = ls.split(";")
            self.product_list.append(product(ligne[0], float(ligne[1]), float(ligne[2])))
        
        self.generate_random_agent(N)
        self.ens = commu(agent_list=self.agent_list, product_list=self.product_list)
        print("===============================\n")
        print("conso de carbone pour cet ensemble : " + str(round(self.ens.C_infini()/1000, 2)) + "t")
    
    def random_agent(self):
        r =  [1 for i in range(0, len(self.product_list))]
        x_t = [1 for i in range(0, len(self.product_list))]
        t = [0.5 for i in range(0, len(self.product_list))]
        for i in range(0, len(self.product_list)):
            n = random.randint(1, len(self.product_list)+1)
            while (n in r):
                n = random.randint(1, len(self.product_list)+1)
            r[i] = n
            if (n == len(self.product_list)):
                x_t[i] = len(self.product_list)

        r = [(x-1) for x in r]
        self.agent_list.append(agent("Random " + str(random.randint(100000,999999)), 0.2, r, x_t, t))

    def affichage_dLmbda(self, C_list, x0, x1):
        N = 10
        x_l = [x0 + (x1-x0) * i/N for i in range(0, N+1)]
        
        for c in C_list:
            y_l = []
            for ldbd in x_l:
                y, x = self.ens.D(ldbd, c)
                y_l.append(y)
            print(x)
            print(y_l)
            plt.plot(x_l, y_l)
            
        plt.show()

    def Cinfini(self):
        return self.ens.C_infini()
    
    def stat_bar_dest(self, C_limite):
        lmbda = self.ens.Dmax_fast(C_limite, 0, 500, 100, 30)
        y, x = self.ens.D(lmbda, C_limite)
        sum = [0 for k in range(0, len(self.product_list))]
        for k in range(0, len(self.product_list)):
            for i in range(0, len(self.agent_list)):
                sum[k] += x[i][k]

        plt.bar([x.name for x in self.product_list], sum)
        plt.show()
    
    def C_evolution(self, c_val):
        l = [[0 for j in range(len(c_val))] for i in range(len(self.product_list))]
        tmp = time.time()
        for m in range(0,len(c_val)):
            lmbda = self.ens.Dmax_fast(c_val[m], 0, 500, 100, 30)
            y, x = self.ens.D(lmbda, c_val[m])
            for k in range(0, len(self.product_list)):
                for i in range(0, len(self.agent_list)):
                    l[k][m] += x[i][k]
            print("Il reste " + str(round((len(c_val)-1-m)*(time.time() - tmp))/60) + " minutes")
            tmp = time.time()

        for pays_i in range(0, len(self.product_list)):
            plt.plot(c_val,[l[pays_i][i] for i in range(0, len(c_val))])
        plt.show()
    

    def C_evolution_normalisee(self, c_val):
        l = [[0 for j in range(len(c_val))] for i in range(len(self.product_list))]
        tmp = time.time()

        for m in range(0,len(c_val)):
            lmbda = self.ens.Dmax_fast(c_val[m], 0, 500, 100, 30)
            y, x = self.ens.D(lmbda, c_val[m])
            for k in range(0, len(self.product_list)):
                for i in range(0, len(self.agent_list)):
                    l[k][m] += x[i][k]
            print("étape : " + str(m) + "\ntemps de la derniere étape : "+  str(time.time() - tmp) + "s\nIl reste " + str(round(((len(c_val)+1-m)*(time.time() - tmp)/60),1)) + " minutes")
            tmp = time.time()
        
        print("Affichage...")
        for pays_i in range(0, len(self.product_list)):
            print(self.product_list[pays_i].name)
            plt.plot([(c / c_val[0]) for c in c_val],[l[pays_i][i]/l[pays_i][0] for i in range(0, len(c_val))], label = self.product_list[pays_i].name)
            plt.legend()
        plt.xlabel("C/C_infini")
        plt.ylabel("Nombre_de_voyages(C)/Nombre_de_voyages(C = C_infini)")
        plt.title("Nombre de voyages en fonction de la limite fixée pour le groupe")
        plt.show()
    
    def C_evolution_normalisee_ln(self, c_val):
        l = [[0 for j in range(len(c_val))] for i in range(len(self.product_list))]
        tmp = time.time()

        for m in range(0,len(c_val)):
            lmbda = self.ens.Dmax_fast(c_val[m], 0, 500, 100, 30)
            y, x = self.ens.D(lmbda, c_val[m])
            for k in range(0, len(self.product_list)):
                for i in range(0, len(self.agent_list)):
                    l[k][m] += x[i][k]
            print("étape : " + str(m) + "\ntemps de la derniere étape : "+  str(round(time.time() - tmp)) + "s\nIl reste " + str(round(((len(c_val)+1-m)*(time.time() - tmp)/60),1)) + " minutes")
            tmp = time.time()
        
        print("Affichage...")
        for pays_i in range(0, len(self.product_list)):
            print(self.product_list[pays_i].name)
            plt.plot([(c / c_val[0]) for c in c_val],[math.log(l[pays_i][i]/l[pays_i][0]) for i in range(0, len(c_val))], label = self.product_list[pays_i].name)
            plt.legend()
        plt.xlabel("C/C_infini")
        plt.ylabel("ln(Nombre_de_voyages(C)/Nombre_de_voyages(C = C_infini))")
        plt.title("Nombre de voyages en fonction de la limite fixée pour le groupe")
        plt.show()


    def generate_random_agent(self, N):
        for k in range(0, N):
            self.random_agent()
        for a in self.agent_list:
            print(a.name)

#exemple de r et x_t1

"""
r1 = [1, 6, 2, 5, 3, 4] #j'adore l'europe
r2 = [6, 1, 2, 5, 4, 3] #j'adore les us, canada...
r3 = [1, 1, 1, 1, 1, 1] #je m'en moque
#pour t = 0.5
N = 2 #je m'en lasse pas !
x_t1 = [(N), 1, 1, 1, 1, 1] #en gros, commence à moins aimer ger, swi et jap au bout de 5 voyages, le reste des le 1er
x_t2 = [1, (N), 1, 1, 1, 1]
x_t3 = [N/6, N/6, N/6, N/6, N/6, N/6]
t = 0.5

agent_europe = agent("M. Europe", 0.2, r1, x_t1,  [t,t,t,t,t,t])
agent_us = agent("Mme. US", 0.2, r2, x_t2, [t,t,t,t,t,t])
agent_sp = agent("M. ???", 0.2, r3, x_t3,  [t,t,t,t,t,t])


ens = commu([agent_list=[agent_europe , agent_us ]])
#C_limite_initial = gen.Cinfini()


gen.stat_bar_dest(1*C_limite_initial)
gen.stat_bar_dest(0.98*C_limite_initial)
gen.stat_bar_dest(0.96*C_limite_initial)
gen.stat_bar_dest(0.94*C_limite_initial)
"""

gen = generateur([], [])
gen.lancement_random(20)
C_limite_initial = gen.Cinfini()

gen.stat_bar_dest(100000000)
#gen.affichage_dLmbda([C_limite_initial, C_limite_initial*0.9, C_limite_initial*0.8, C_limite_initial*0.7, C_limite_initial*0.6, C_limite_initial*0.5], 0, 5)

"""
N = 12
x0 = 0.7
x1 = 1
l = [(x0 + (x1-x0)*(i/(N+1)))*C_limite_initial for i in range(0, N)]
l.reverse()
gen.C_evolution_normalisee_ln(l)
"""


