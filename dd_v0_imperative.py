import cvxpy as cp 
from functools import partial 
import math 
import matplotlib.pyplot as plt 


FRANCE = [150, 1]
JAPON = [1200, 700]

nb_agents = 2
nb_produits = 2

l1 = [1, 0.1, 0.5, 0.1]
l2 = [0.5, 0.1, 0.5, 0.1]

#Utility 

def u(xa, alpha_a, beta_a):
    sum = 0
    for i in range(len(xa)):
        sum += alpha_a[i]*(xa[i]+beta_a[i])
    return sum

def D(C, lmbd):

    x = cp.Variables((nb_agents, nb_produits))

    constraints = [x >= 0]
    constraints.append(FRANCE[0]*x[0][0] + JAPON[0]*x[0][1])
    constraints.append(FRANCE[0]*x[1][0] + JAPON[0]*x[1][1])
    constraints.append(x[0][0] + x[0][1] >= 1)
    constraints.append(x[1][0] + x[1][1] >= 1)

    def f(m):
        