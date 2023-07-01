import math

import cvxpy as cp
import matplotlib.pyplot as plt
import numpy as np
import random
import time


class industry:
    def __init__(self, name, benef, carb):
        self.name = name
        self.benef = benef
        # benef est maintenant un vecteur (les bénéfices d'une industrie dépendent de chaque région)
        # [pi,1 ... pi,6]
        self.carb = carb
        # carb est maintenant un vecteur (même chose)
        # [ci,1 ... ci,6]


class region:
    def __init__(self, name, u, population, id):  # u fonction d'utilité de la région
        self.u = u
        self.population = population
        self.name = name
        self.id = id  # je suis la region numero id... (dans les listes)
        # en gros, plutot que d'utiliser self.carb etc (creation d'une info redondante ?) on prend
        # self.carb= carb #carb pour chaque industrie DANS CETTE REGION
        # self.benef= benef #même chose

    def C(self):
        COP = 2
        COP *= self.population
        return COP

    def phi(self, x_list, industry_list, lmbda):
        benef_tot_region = 0
        for i in range(0, len(industry_list)):
            benef_tot_region += x_list[i] * industry_list[i].benef[self.id] - lmbda * industry_list[i].carb[self.id] * \
                                x_list[i]  # j'ai change en - lmbda, peut etre une erreur de moi
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
        constraints.append(x[0] + x[1] + x[2] == 1)
        constraints.append(x[0] >= 0.03)
        constraints.append(x[1] >= 0.05)

        # constraints.append(x[2]>=0.1)

        def f(m):
            return self.phi(m, industry_list, lmbda)

        objective = cp.Maximize(f(x))
        prob = cp.Problem(objective, constraints)
        prob.solve()
        # plt.bar([1,2,3],x.value)
        # plt.xlabel("Percentage")
        # plt.title(self.name)
        # plt.show()
        #print(x.value) #HEREEEEEEEE
        return (x.value, f(x.value))


class commu:
    def __init__(self, region_list, industry_list):
        self.region_list = region_list
        self.industry_list = industry_list

    # ajout spécifique pour calculer C
    def C(self):
        COP = 2  # on met C en tonnes ou en kg?
        s = 0
        for i in range(0, len(self.region_list)):
            s += self.region_list[i].population
        COP *= s
        return COP
        # petit pb quand on prend les resultats de la cop... souvent juste pas tenable...

    # calcul des sommes, on crée un vecteur de coefficient x[région]@benef[region] pour chaque secteur d'activité

    def D(self, ldbd, C):  # dépend des régions qui chacune a sa u (utility function)
        sum = 0
        l = []
        for j in range(0, len(self.region_list)):
            x, y = self.region_list[j].max_phi(self.industry_list, ldbd)
            sum = sum + y
            l.append(x)

        #print(l)
        return (sum + ldbd * C), l
    def fAux(self, x0, x1, N, C):
        x = [x0 + (x1 - x0) * i / N for i in range(0, N + 1)]
        y_tmp = -10000000
        for i in range(0, len(x)):
            y, x_list = self.D(x[i], C)
            if (y_tmp - y) >= 0:
                return x[i - 1], x[i]
            else:
                y_tmp = y
        return x[N - 1], x[N - 1]

    def Dmax_fast(self, C, x0, x1, N1, N2):
        for i in range(0, N2):
            x0, x1 = self.fAux(x0, x1, N1, C)
            if abs((x1 - x0)) < 0.0000001:
                return (x0 + x1) / 2
        return (x0 + x1) / 2

    def presentation_resultat(self, c_list, maxL=500, N=100):
        for c in c_list:
            print("===========================================\n")
            ldbd = self.Dmax_fast(c, 0, maxL, N, 150)
            y, x = self.D(ldbd, c)
            print("")
            print("LAMBDA = " + str(round(ldbd * 1000, 10)) + "e/t ; C = " + str(c) + "kg ; total carbone : " + str(
                self.carbon_total(x)) + "kg")
            for i in range(0, len(x)):
                # print(self.agent_list[i].name + "> expenses : " + str(round(self.total_price(x[i]))) + " ; budget : " + str(round(self.agent_list[i].budget)))
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
            ci = Cmin + ((Cmax - Cmin) / N_pas) * i
            c.append(ci)
            ldbd = self.Dmax_fast(ci, 0, 500, 30, 100)
            lbda_l.append(ldbd)

        plt.plot(c, lbda_l)
        plt.grid()
        plt.title("lambda en fonction de C")
        plt.xlabel("C (kg)")
        plt.ylabel("lambda ($/kg)")
        plt.show()

    def C_evolution(self):
        for r in range(0,len(self.region_list)):
            print("===========================================\n")
            region=self.region_list[r]
            print("C demandé par la région " + self.region_list[r].name + " : " + str(region.C()))
            c_val = [self.C() * i for i in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 1,2, 3, 4, 5, 6, 7, 8, 9, 10]]
            l = [[0 for j in range(len(c_val))] for i in range(len(self.industry_list))]

            for k in range (0,len(c_val)):
                ldbd = self.Dmax_fast(c_val[k], 0, 500, 30, 100) #on trouve le meilleur lambda pour chaque C
                print("lambda = " + str(ldbd))
                print("C = " + str(c_val[k]))
                y, x = self.D(ldbd, c_val[k])   #on trouve les investissements pour chaque secteur
                for i in range(0, len(self.industry_list)): #on les stocke dans une liste
                    l[i][k] = x[r][i]

            print("Affichage...")
            #print(self.D(lmbda, self.C())[1])

            for i in range(0, len(self.industry_list)):
                #print(self.industry_list[industry_i].name)
                plt.plot([(c) for c in c_val],
                         [(l[i][k]) for k in range(0, len(c_val))],
                         label=self.industry_list[i].name)
                plt.legend()

            plt.xlabel("C = Multiples de la taxe carbone recommandée pour la région " + self.region_list[r].name)
            plt.ylabel("Parts d'investissements dans le secteur (C)")
            plt.title("Parts d'investissements dans les secteurs en fonction de C")
            plt.show()


def simple_utility_function(x_t, t,
                            x):  # x_t[i] est la quantité à laquelle une augmentation de dx sera tho fois moins utile que la premiere
    return (x_t + x * (1 / (t * t) - 1)) ** (1 / 2) - x_t ** (1 / 2)  # x_t moment où t'en as marre de consommer


# j'ai juste modifie un peu pour voir

def utility_function(ranking, x_t_list, tho_list, x):  # ranking[i] < ranking[j] => on prefere i à j.
    sum = 0
    i = 0
    for xi in x:
        sum += (0.4 * ranking[i]) * simple_utility_function(x_t_list[i], tho_list[i], xi)
        i += 1
    return sum


def u(x):
    return utility_function([3, 2, 1], [1, 1, 1], [0.5, 0.5, 0.5], x)


ridf = [1, 1.8, 2.43]  # j'adore les services
ra = [0.98, 1.96, 2.549]
rp = [2, 1, 2.4]
rb = [4, 1, 0.07]  # j'adore l'agriculture
rpdl = [3, 7, 0.05]
rc = [2, 2, 2.33]
# pour tho = 0.5

x_tidf = [1, 1, 1]  # en gros, commence à moins aimer ger, swi et jap au bout de 5 voyages, le reste des le 1er
x_ta = [1, 100, 0.001]
x_tp = [1, 1, 1]
x_tb = [1, 1, 1]
x_tpdl = [1, 1, 1]
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


#print(u([0, 0, 0]))
M = 10000000

iledefrance = region("Ile de France", uidf, 12300000 / M, 0)
auvergne = region("Auvergne", uauvergne, 8200000 / M, 1)
provence = region("Provence", uprovence, 5160000 / M, 2)
bretagne = region("Bretagne", ubretagne, 3400000 / M, 3)
paysdeloire = region("Pays de la Loire", upaysdelaloire, 3900000 / M, 4)
corse = region("Corse", ucorse, 351000 / M, 5)

agriculture = industry("Agriculture",
                       [6730953600 / M, 4487302400 / M, 2823717120 / M, 1860588800 / M, 2134204800 / M, 192078432 / M],
                       [16929110.55 / M, 11286073.7 / M, 7101968.329 / M, 4679591.535 / M, 5367766.76 / M,
                        483099.0084 / M])
industrie = industry("Industrie", [1.08495E+11 / M, 72329705560 / M, 45514790328 / M, 29990365720 / M, 34400713620 / M,
                                   3096064226 / M],
                     [23979872.72 / M, 23979872.72 / M, 15089773.57 / M, 9942874.057 / M, 11405061.42 / M,
                      1026455.528 / M])
services = industry("Services", [2.99359e+11 / M, 1.99573e+11 / M, 1.25585e+11 / M, 82749686880 / M, 94918758480 / M,
                                 8542688263 / M],
                    [10834630.75 / M, 7223087.169 / M, 4545259.731 / M, 2994938.582 / M, 3435370.727 / M,
                     309183.3654 / M])

industry_list = [agriculture, industrie, services]
region_list = [iledefrance, auvergne, provence, bretagne, paysdeloire, corse]

ens = commu(region_list, industry_list)
#r = ens.D(0, 10000000)

ens.C_evolution()


# ens.Dmax_fast()
"""sectors=["Agriculture","Industry","Services"]
sectorstat=[0,0,0]
for i in range(len(sectors)):
    for j in range(len(ens.region_list)):
        sectorstat[i]+=r[1][j][i]/6
#regions = {'Ile-De-France': r[1][0],'Auvergne': r[1][1],'Provence': r[1][2], 'Bretagne': r[1][3], 'Pays de la Loire' : r[1][4], 'Corse' : r[1][5]}

print(sectorstat)

plt.bar(sectors, sectorstat, color=['green', 'grey', 'blue'])
plt.title('Sectors')

#bottom = np.zeros(3)

#fig, ax = plt.subplots()

 #for region,region_sectors  in regions.items():
 #   p = ax.bar(sectors, region_sectors, 0.6, label=region, bottom=bottom, color=['green', 'grey', 'blue'])
  #  bottom += region_sectors


#bar_container = ax.bar(sectors, r[1][0],color=['green', 'grey', 'blue'])
#ax.bar_label(bar_container)
#ax.set(ylabel='Percentage')

plt.show()"""


