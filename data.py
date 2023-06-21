C_REF = 1000 / 30 #cout de la vie + logement de référence
THO_D = 1 #combien je compte dépenser plus dans le pays (si 1, je vis comme un citoyen normal). On imagine la différence entre des vacances et des études...
THO_C = THO_D #combien je vais dépenser de carbone en plus


class transport:
    def __init__(self, name, emissions, prix):
        self.name = name
        self.emissions = emissions #emission km
        self.prix = prix #prix au km
    
    def emissions_distance(self, d):
        return d*self.emissions
    
    def cout_distance(self, d):
        return d*self.prix
    
    def transport_information(self, N = 500):
        print(self.name + " pour " + str(N) + " km")
        print("emissions > " + str(round(self.emissions_distance(N))) + " kg CO2")
        print("cout > " + str(round(self.cout_distance(N))) + " euros")
        print("\n")

class pays:
    def __init__(self, name, emssion_par_hab, cost_of_living): 
        self.name = name
        self.emissions_par_hab = emssion_par_hab
        self.cost_of_living = cost_of_living
        self.dist = 0
    
    def presentation(self):
        if (self.cost_of_living != []):
            #print("country : " + self.name + ", emissions : " + str(round(self.emissions_par_hab)) + "kg, cost of living + rent : ???")
        
            print("country : " + self.name + ", emissions : " + str(round(self.emissions_par_hab)) + "kg, cost of living + rent : " + str(round(self.cost_of_living_plus_rent_f(), 2)))

    def cost_of_living_plus_rent(self):
        sum = 0
        for i in range(0, len(self.cost_of_living)):
            sum += self.cost_of_living[i]
        return sum / (len(self.cost_of_living))

    def cost_of_living_plus_rent_f(self):
        return self.cost_of_living_plus_rent()/56
    
    def carbo_without_transport(self, time): #temps en jour
        return self.emissions_par_hab * (time / 356) * THO_C
    
    def cost_without_transport(self, time): #temps en jour
        cofpr = self.cost_of_living_plus_rent_f()
        return cofpr * C_REF * time * THO_D
    
    def transport_mode(self):
        if (self.dist < 500):
            car = transport("car", (0.200 + 0.250)/2, (2 * 7)/100)
            return car
        else:
            plane = transport("plane", (0.145+0.285)/2, 0.12)    
            return plane
    
    def carbo(self, time):
        m = self.transport_mode()
        return self.carbo_without_transport(time) + m.emissions_distance(self.dist/1000) * 2
    
    def cost(self, time):
        m = self.transport_mode()
        return self.cost_without_transport(time) + m.cout_distance(self.dist/1000) * 2

    

class data:
    def __init__(self, country_list = []):
        self.country_list = []

    def lecture_co2(self, year):
        country_list = []
        file = open("data/owid-co2-data.csv", "r")
        data = file.read()
        data_liste = data.split("\n")
        for l in data_liste:
            try:
                ls = l.split(",")
                if (ls[1] == str(year)):
                    country_list.append(pays(ls[0], float(ls[16])*1000, []))
            except:
                pass
        self.country_list = country_list
    
    def lecture_cost(self):
        file = open("data/costofliving.csv")
        data = file.read()
        data_liste = data.split("\n")
        for l in data_liste:
            try:
                ls = l.split(",")
                country = ls[2][1:]
                country = country[:4]
                for c in self.country_list:
                    if (c.name.lower()[:4] == country.lower()):
                        c.cost_of_living.append(float(ls[5]))
            except:
                pass

    def get_country_list(self, list):
        l = []
        for country_name in list:
            for country in self.country_list:
                if (country_name.lower() in country.name.lower()):
                    l.append(country)
        return l
    
        
    def data_presentation(self):
        for p in self.country_list:
            p.presentation()


#https://geodesie.ign.fr/contenu/fichiers/Distance_longitude_latitude.pdf

 
from math import sin, cos, acos, pi


def dms2dd(d, m, s):
        #Convertit un angle "degrés minutes secondes" en "degrés décimaux"
        return d + m/60 + s/3600

def dd2dms(dd):
    #Convertit un angle "degrés décimaux" en "degrés minutes secondes"
    d = int(dd)
    x = (dd-d)*60
    m = int(x)
    s = (x-m)*60
    return d, m, s

def deg2rad(dd):
    #Convertit un angle "degrés décimaux" en "radians"
    return dd/180*pi
 
def rad2deg(rd):
    #Convertit un angle "radians" en "degrés décimaux"
    return rd/pi*180
 
def distanceGPS(latA, longA, latB, longB):
    #Retourne la distance en mètres entre les 2 points A et B connus grâce àleurs coordonnées GPS (en radians).
    # Rayon de la terre en mètres (sphère IAG-GRS80)
    RT = 6378137
    # angle en radians entre les 2 points
    S = acos(sin(latA)*sin(latB) + cos(latA)*cos(latB)*cos(abs(longB-longA)))
    # distance entre les 2 points, comptée sur un arc de grand cercle
    return S*RT

class distance:
    #programme pas de moi (enfin pas la base du programme)
    def __init__(self, countryA, countryB):
        self.countryA = countryA
        self.countryB = countryB
    
    def dist(self):
        A1 = 0
        A2 = 0
        B1 = 0
        B2 = 0
        file = open("data/rbjev.txt", "r")
        data = file.read()
        
        ll = data.split("\n")
        for l in ll:
            donnee_l = l.split("\t")
            try:
                if (donnee_l[3][:4].lower() == self.countryA[:4].lower()):
                    A1 = float(donnee_l[1])
                    A2 = float(donnee_l[2])
                if (donnee_l[3][:4].lower() == self.countryB[:4].lower()):
                    B1 = float(donnee_l[1])
                    B2 = float(donnee_l[2])
            except: 
                print("erreur")

    # cooordonnées GPS en radians du 1er point (ici, mairie de Tours)
        latA = deg2rad(A1) # Nord
        longA = deg2rad(A2) # Est
 
    # cooordonnées GPS en radians du 2ème point (ici, mairie de Limoges)
        latB = deg2rad(B1) # Nord
        longB = deg2rad(B2) # Est
 
        dist = distanceGPS(latA, longA, latB, longB)
        return int(dist)


class export:
    def __init__(self, destination_list):
        self.destination_list = destination_list
    
    def export(self,time):
        d = data()
        d.lecture_co2(2017)
        d.lecture_cost()
        #d.data_presentation()
        countries_l = d.get_country_list(self.destination_list)
        for country in countries_l:
            dist = distance("france", country.name)
            country.dist = dist.dist()
        
        file = open("expo", "w+")
        for country in countries_l:
            print(country.name + " > " + " price : " + str(round(country.cost(time))) + " euros, carbon : " + str(round(country.carbo(time))) + " kg")
            file.write(country.name[:5] + ";"+ str(round(country.cost(time))) +";"+ str(round(country.carbo(time)))+ "\n")
        file.close()

expo = export(["france", "united states", "canada", "germany", "hong kong", "japan", "sweden", "Switzerland"])        
expo.export(30*2)

"""
plane = transport("plane", (0.145+0.285)/2, 0.12)    
train = transport("train", 0.010, 0.20) 
elec_car = transport("elec_car", 0.100, 0.03)
car = transport("car", (0.200 + 0.250)/2, (2 * 7)/100)
bus = transport("bus", 0.100, 0.07)
l = [plane, train, elec_car, car, bus]
"""
