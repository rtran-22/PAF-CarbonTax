import cvxpy as cp
import matplotlib.pyplot as plt
import numpy as np

class industry:
    def __init__(self, name, benef, carb):
        self.name = name
        self.benef = benef
        #benef est maintenant un vecteur (les bénéfices d'une industrie dépendent de chaque région)
        # [pi,1 ... pi,6]
        self.carb = carb 
        #carb est maintenant un vecteur (même chose)
        # [ci,1 ... ci,6]

class region:
    def __init__(self, name, u, population, id): #u fonction d'utilité de la région
        self.u = u
        self.population = population
        self.name = name
        self.id = id #je suis la region numero id... (dans les listes)
        #en gros, plutot que d'utiliser self.carb etc (creation d'une info redondante ?) on prend 
        #self.carb= carb #carb pour chaque industrie DANS CETTE REGION
        #self.benef= benef #même chose

    def phi(self, x_list, industry_list, lmbda):
        benef_tot_region = 0
        for i in range(0, len(industry_list)):
            benef_tot_region += x_list[i]*industry_list[i].benef[self.id] - lmbda*industry_list[i].carb[self.id]*x_list[i]   # j'ai change en - lmbda, peut etre une erreur de moi
        return benef_tot_region
    
    def max_phi(self, industry_list, lmbda):
        x = cp.Variable(len(industry_list))
        constraints = [x >= 0]
        """
        def u(x):
            sum = 0
            for xi in x:
                sum += ((xi + 1)**(1/2) - 1)*10000
            return sum
        """
        
        constraints.append(self.u(x) >= 1)
        constraints.append(x[0]+x[1]+x[2] == 1)
        constraints.append(x[0]>=0.05)
        constraints.append(x[1]>=0.05)
        #constraints.append(x[2]>=0.1)

        def f(m):
            return self.phi(m, industry_list, lmbda)
        
        objective = cp.Maximize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        print(x.value)
        return (x.value, f(x.value))
    
class commu:
    def __init__(self, region_list, industry_list):
        self.region_list = region_list
        self.industry_list = industry_list

    #ajout spécifique pour calculer C
    def C(self):
        COP=2 #on met C en tonnes ou en kg?
        s=0
        for i in range(0, len(self.region_list)):
            s+=self.region_list[i].population
        COP*=s
        return COP 
        #petit pb quand on prend les resultats de la cop... souvent juste pas tenable...


#calcul des sommes, on crée un vecteur de coefficient x[région]@benef[region] pour chaque secteur d'activité
    
    def D(self, ldbd,C): #dépend des régions qui chacune a sa u (utility function)
        sum = 0
        l = []
        for j in range(0, len(self.region_list)):
            x, y = self.region_list[j].max_phi(self.industry_list, ldbd)
            sum = sum + y
            l.append(x)
        return (sum + ldbd*C), l


def simple_utility_function(x_t, t, x): #x_t[i] est la quantité à laquelle une augmentation de dx sera tho fois moins utile que la premiere
    return (x_t + x*(1/(t*t) - 1)) ** (1/2) - x_t**(1/2) #x_t moment où t'en as marre de consommer

#j'ai juste modifie un peu pour voir

def utility_function(ranking, x_t_list, tho_list, x):  # ranking[i] < ranking[j] => on prefere i à j.
    sum = 0
    i = 0
    for xi in x:
        sum += (0.4*ranking[i]) * simple_utility_function(x_t_list[i], tho_list[i], xi)
        i += 1
    return sum

def u(x):
    return utility_function([3,2,1], [1,1,1], [0.5, 0.5, 0.5], x)



ridf = [1, 2, 2.44]  # j'adore les services
ra = [1, 3, 4]
rp = [2,1,2.4]
rb = [4,1,0.07] # j'adore l'agriculture
rpdl = [3,7,0.05]
rc = [2,2,2.2]
# pour tho = 0.5

x_tidf = [1, 1, 1]  # en gros, commence à moins aimer ger, swi et jap au bout de 5 voyages, le reste des le 1er
x_ta = [1, 5, 1]
x_tp = [1, 1, 1]
x_tb = [1, 1, 1]
x_tpdl = [1, 1, 1]
x_tc = [1, 1, 1]


def uidf(x):
    t = 0.5
    print(utility_function(ridf, x_tidf, [t, t, t, t, t, t],x))
    return utility_function(ridf, x_tidf, [t, t, t, t, t, t],x) 

def uauvergne(x):
    t = 0.5
    return utility_function(ra, x_ta, [t, t, t, t, t, t], x)

def uprovence(x):
    t = 0.5
    return utility_function(rp, x_tp, [t, t, t, t, t, t], x)

def ubretagne(x):
    t = 0.5
    return utility_function(rb, x_tb, [t, t, t, t, t, t], x)

def upaysdelaloire(x):
    t = 0.5
    return utility_function(rpdl, x_tpdl, [t, t, t, t, t, t], x)

def ucorse(x):
    t = 0.5
    return utility_function(rc, x_tc, [t, t, t, t, t, t], x)
print(u([0,0,0]))
N = 10000000

iledefrance = region("Ile de France", uidf, 12300000/N, 0)
auvergne = region("Auvergne", uauvergne, 8200000/N, 1)
provence = region("Provence", uprovence, 5160000/N,2)
bretagne = region("Bretagne", ubretagne, 3400000/N, 3)
paysdeloire = region("Pays de la Loire",upaysdelaloire ,3900000/N,4)
corse = region("Corse", ucorse, 351000/N,5)


agriculture = industry("Agriculture", [6730953600/N,4487302400/N,2823717120/N,1860588800/N,2134204800/N,192078432/N], [16929110.55/N,11286073.7/N,7101968.329/N,4679591.535/N,5367766.76/N,483099.0084/N])
industrie = industry("Industrie", [1.08495E+11/N,72329705560/N,45514790328/N,29990365720/N,34400713620/N,3096064226/N], [23979872.72/N,23979872.72/N,15089773.57/N,9942874.057/N,11405061.42/N,1026455.528/N])
services = industry("Services", [2.99359e+11/N,1.99573e+11/N,1.25585e+11/N,82749686880/N,94918758480/N,8542688263/N], [10834630.75/N,7223087.169/N,4545259.731/N,2994938.582/N,3435370.727/N,309183.3654/N])

industry_list = [agriculture, industrie, services]
region_list = [iledefrance, auvergne , provence , bretagne , paysdeloire , corse]

ens = commu(region_list, industry_list)
ens.D(0,10000000)
