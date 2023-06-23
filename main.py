import cvxpy as cp
import matplotlib.pyplot as plt
import numpy as np

class industry:
    def __init__(self, name, benef, carb):
        self.name = name
        self.benef = benef #benef est maintenant un vecteur (les bénéfices d'une industrie dépendent de chaque région)
        # [pi,1 ... pi,6]
        self.carb = carb #carb est maintenant un vecteur
        # [ci,1 ... ci,6]


class region:
    def __init__(self, name, u, population): #u fonction d'utilité de la région
        self.u = u
        self.population = population
        self.name = name



class commu:
    def __init__(self, region_list, industry_list):
        self.region_list = region_list
        self.industry_list = industry_list

#changement calcul: est-ce que c'est pareil de sommer sur les i que sur les a ?
    def carbon_total(self, x):
        c_tot = 0
        for i in range(0, len(self.industry_list)):
            carb=np.array(self.industry_list.carb) #on crée le vecteur correspondant (ligne)
            matx=(np.array(x)).T #x vecteur colonne
            c_tot += np.dot(carb,matx)
        return c_tot

    # changement calcul
    def total_benef(self, product_quantities_list):
        pql = product_quantities_list
        tot_benef = 0
        for k in range(0, len(self.region_list)):
            tot_benef += self.industry_list[k].benef * pql[k]
        return tot_benef

    #ajout spécifique pour calculer C
    def C(self):
        COP=2 #on met C en tonnes ou en kg?
        for i in range(0, len(self.region_list)):
            COP*=self.region_list[i].population

    def function(self, lbda, x):
        sum = 0
        for i in range(0, len(self.region_list)):
            sum += (-1) * self.region_list[i].u(x[i]) + lbda * (self.carbon_total(x) - self.C)
        return sum

    def D(self, ldbd):
        x = cp.Variable((len(self.region_list), len(self.industry_list)))
        constraints = [x >= 0]
        #for i in range(0, len(self.region_list)):
        #    constraints.append((#compléter))

        def f(m):
            return self.function(lbda=ldbd, x=m)

        objective = cp.Maximize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        return x.value, f(x.value)

#??
    def Dmax(self,min_lmbd, max_lmbd, N_val):
        x = [min_lmbd + (max_lmbd - min_lmbd) * i / N_val for i in range(0, N_val - 1)]
        x_max = 0
        y_max = -100000000000000000000000
        tmp = 0
        for i in range(0, len(x)):
            ## tmp uniquement la pour l'affichage
            if (True) & (tmp != round(i * 100 / len(x))):
                tmp = round(i * 100 / len(x))
                print(str(tmp / 100) + "%")
            x_val, y = ens.D(x[i], self.C)
            if y_max <= y:
                print(x[i])
                y_max = y
                x_max = x[i]
        return x_max, y_max


    def fAux(self, x0, x1, N, C):  # ????
        x = [x0 + (x1 - x0) * i / N for i in range(0, N + 1)]
        y_tmp = -10000000
        for i in range(0, len(x)):
            x_val, y = ens.D(x[i], C)
            if (y_tmp - y) >= 0:
                return x[i - 1], x[i]
            else:
                y_tmp = y
        return x[N - 1], x[N - 1]

    def Dmax_fast(self, x0, x1, N1, N2):
        for i in range(0, N2):
            x0, x1 = self.fAux(x0, x1, N1, self.C)
            if abs((x1 - x0)) < 0.00001:
                return (x0 + x1) / 2
        return (x0 + x1) / 2

    def presentation_resultat(self, maxL=10, N=1000 * 2):  # plus de paramètre puisqu'on a fixé C
            print("===========================================\n")
            ldbd = self.Dmax_fast(0, maxL, N, 400)
            x, y = self.D(ldbd)
            print("")
            print("LAMBDA = " + str(ldbd) + "; C = " + str(self.C) + "kg ; total carbone : " + str(
                self.carbon_total(x)) + "kg")
            for i in range(0, len(x)):
                print(self.region_list[i].name + "> expenses : " + str(
                    round(self.total_benef(x[i]))) + " ; budget : " + str(round(self.region_list[i].budget)))
                for j in range(0, len(x[i])):
                    print(self.industry_list[j].name + " : " + str(round(x[i][j], 1)))
                print("")
            print("")


def simple_utility_function(x_t, tho, x): #x_t[i] est la quantité à laquelle une augmentation de dx sera tho fois moins utile que la premiere
    return x_t*(1 + (x/x_t)*(1/(tho*tho) - 1)) ** (1/2)

def utility_function(ranking, x_t_list, tho_list, x):  # ranking[i] < ranking[j] => on prefere i à j.
    sum2 = 0.0
    i = 0
    for xi in x:
        sum2 += (1 / ranking[i]) * simple_utility_function(x_t_list[i], tho_list[i], xi)
        i += 1
    return sum2


ridf = [0.03, 2, 8]  # j'adore les services
ra = [0.2, 2, 7] 
rp = [2,1,7]
rb = [7,3,0.5] # j'adore l'agriculture
rpdl = [3,7,0.5]
rc = [0.2,2,8]
# pour tho = 0.5

x_tidf = [1, 1, 5]  # en gros, commence à moins aimer ger, swi et jap au bout de 5 voyages, le reste des le 1er
x_ta = [3, 3, 3]
x_tp = [3, 1, 2]
x_tb = [5, 2, 1]
x_tpdl = [3, 1, 3]
x_tc = [1, 1, 1]

def uidf(x):
    t = 0.5
    return utility_function(ridf, x_tidf, [t, t, t, t, t, t], x)

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

#il faudrait potentiellement ajouter des caractéristiques à nos régions

iledefrance = region("Ile de France", uidf, 12300000) 
auvergne = region("Auvergne", uauvergne, 8200000)
provence = region("Provence", uprovence,5160000)
bretagne = region("Bretagne", ubretagne,3400000)
paysdeloire = region("Pays de la Loire",upaysdelaloire,3900000)
corse = region("Corse", ucorse,351000)


agriculture = industry("Agriculture", [6730953600,4487302400,2823717120,1860588800,2134204800,192078432], [16929110.55,11286073.7,7101968.329,4679591.535,5367766.76,483099.0084])
industrie = industry("Industrie", [72329705560,72329705560,45514790328,29990365720,34400713620,3096064226], [23979872.72,23979872.72,15089773.57,9942874.057,11405061.42,1026455.528])
services = industry("Services", [2.99359e+11,1.99573e+11,1.25585e+11,82749686880,94918758480,8542688263], [10834630.75,7223087.169,4545259.731,2994938.582,3435370.727,309183.3654])


industry_list = [agriculture, industrie, services]

ens = commu([iledefrance, auvergne, provence, bretagne, paysdeloire, corse], industry_list=industry_list)

# on a pas besoin de changer la valeur de C pour le moment. on pourra ajuster après si par ex on pense ne pas respecter
#la cop, qu'elle est trop ambitieuse etc..

ens.presentation_resultat()