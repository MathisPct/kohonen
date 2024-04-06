# coding: utf8
# !/usr/bin/env python
# ------------------------------------------------------------------------
# Carte de Kohonen
# Écrit par Mathieu Lefort
#
# Distribué sous licence BSD.
# ------------------------------------------------------------------------
# Implémentation de l'algorithme des cartes auto-organisatrices de Kohonen
# ------------------------------------------------------------------------
# Pour que les divisions soient toutes réelles (pas de division entière)
from __future__ import division

import math
import os

# Librairie de calcul matriciel
import numpy
# Librairie d'affichage
import matplotlib.pyplot as plt


class Neuron:
    ''' Classe représentant un neurone '''

    def __init__(self, w, posx, posy):
        '''
    @summary: Création d'un neurone
    @param w: poids du neurone
    @type w: numpy array
    @param posx: position en x du neurone dans la carte
    @type posx: int
    @param posy: position en y du neurone dans la carte
    @type posy: int
    '''
        # Initialisation des poids
        self.weights = w.flatten()
        # Initialisation de la position
        self.posx = posx
        self.posy = posy
        # Initialisation de la sortie du neurone
        self.y = 0.

    def compute(self, x):
        '''
    @summary: Affecte à y la valeur de sortie du neurone (ici on choisit la distance entre son poids et l'entrée, i.e. une fonction d'aggrégation identité)
    @param x: entrée du neurone
    @type x: numpy array
    '''
        self.y = numpy.linalg.norm(x - self.weights)

    def learn(self, eta, sigma, posxbmu, posybmu, x):
        '''
    @summary: Modifie les poids selon la règle de Kohonen
    @param eta: taux d'apprentissage
    @type eta: float
    @param sigma: largeur du voisinage
    @type sigma: float
    @param posxbmu: position en x du neurone gagnant (i.e. celui dont le poids est le plus proche de l'entrée)
    @type posxbmu: int
    @param posybmu: position en y du neurone gagnant (i.e. celui dont le poids est le plus proche de l'entrée)
    @type posybmu: int
    @param x: entrée du neurone
    @type x: numpy array
    '''
        # self.weights[:] += eta * math.exp(

        self.weights[:] += eta * math.exp(-((abs(self.posx - posxbmu) + abs(self.posy - posybmu)) ** 2) / (2 * sigma * sigma)) * (x - self.weights)


class SOM:
    ''' Classe implémentant une carte de Kohonen. '''

    def __init__(self, inputsize, gridsize):
        '''
    @summary: Création du réseau
    @param inputsize: taille de l'entrée
    @type inputsize: tuple
    @param gridsize: taille de la carte
    @type gridsize: tuple
    '''
        # Initialisation de la taille de l'entrée
        self.inputsize = inputsize
        # Initialisation de la taille de la carte
        self.gridsize = gridsize
        # Création de la carte
        # Carte de neurones
        self.map = []
        # Carte des poids
        self.weightsmap = []
        # Carte des activités
        self.activitymap = []
        for posx in range(gridsize[0]):
            mline = []
            wmline = []
            amline = []
            for posy in range(gridsize[1]):
                neuron = Neuron(numpy.random.random(self.inputsize), posx, posy)
                mline.append(neuron)
                wmline.append(neuron.weights)
                amline.append(neuron.y)
            self.map.append(mline)
            self.weightsmap.append(wmline)
            self.activitymap.append(amline)
        self.activitymap = numpy.array(self.activitymap)

    def compute(self, x):
        '''
    @summary: calcule de l'activité des neurones de la carte
    @param x: entrée de la carte (identique pour chaque neurone)
    @type x: numpy array
    '''
        # On demande à chaque neurone de calculer son activité et on met à jour la carte d'activité de la carte
        for posx in range(self.gridsize[0]):
            for posy in range(self.gridsize[1]):
                self.map[posx][posy].compute(x)
                self.activitymap[posx][posy] = self.map[posx][posy].y

    def learn(self, eta, sigma, x):
        '''
    @summary: Modifie les poids de la carte selon la règle de Kohonen
    @param eta: taux d'apprentissage
    @type eta: float
    @param sigma: largeur du voisinage
    @type sigma: float
    @param x: entrée de la carte
    @type x: numpy array
    '''
        # Calcul du neurone vainqueur
        bmux, bmuy = numpy.unravel_index(numpy.argmin(self.activitymap), self.gridsize)
        # Mise à jour des poids de chaque neurone
        for posx in range(self.gridsize[0]):
            for posy in range(self.gridsize[1]):
                self.map[posx][posy].learn(eta, sigma, bmux, bmuy, x)

    def scatter_plot(self, interactive=False):
        '''
    @summary: Affichage du réseau dans l'espace d'entrée (utilisable dans le cas d'entrée à deux dimensions et d'une carte avec une topologie de grille carrée)
    @param interactive: Indique si l'affichage se fait en mode interactif
    @type interactive: boolean
    '''
        # Création de la figure
        if not interactive:
            plt.figure()
        # Récupération des poids
        w = numpy.array(self.weightsmap)
        # Affichage des poids
        plt.scatter(w[:, :, 0].flatten(), w[:, :, 1].flatten(), c='k')
        # Affichage de la grille
        for i in range(w.shape[0]):
            plt.plot(w[i, :, 0], w[i, :, 1], 'k', linewidth=1.)
        for i in range(w.shape[1]):
            plt.plot(w[:, i, 0], w[:, i, 1], 'k', linewidth=1.)
        # Modification des limites de l'affichage
        plt.xlim(-1, 1)
        plt.ylim(-1, 1)
        # Affichage du titre de la figure
        plt.suptitle('Poids dans l\'espace d\'entree')
        # Affichage de la figure
        if not interactive:
            plt.show()

    def scatter_plot_2(self, interactive=False):
        '''
    @summary: Affichage du réseau dans l'espace d'entrée en 2 fois 2d (utilisable dans le cas d'entrée à quatre dimensions et d'une carte avec une topologie de grille carrée)
    @param interactive: Indique si l'affichage se fait en mode interactif
    @type interactive: boolean
    '''
        # Création de la figure
        if not interactive:
            plt.figure(figsize=(10, 5))
        # Affichage des 2 premières dimensions dans le plan
        plt.subplot(1, 2, 1)
        # Récupération des poids
        w = numpy.array(self.weightsmap)
        # Affichage des poids
        plt.scatter(w[:, :, 0].flatten(), w[:, :, 1].flatten(), c='k')
        # Affichage de la grille
        for i in range(w.shape[0]):
            plt.plot(w[i, :, 0], w[i, :, 1], 'k', linewidth=1.)
        for i in range(w.shape[1]):
            plt.plot(w[:, i, 0], w[:, i, 1], 'k', linewidth=1.)
        # Affichage des 2 dernières dimensions dans le plan
        plt.subplot(1, 2, 2)
        # Récupération des poids
        w = numpy.array(self.weightsmap)
        # Affichage des poids
        plt.scatter(w[:, :, 2].flatten(), w[:, :, 3].flatten(), c='k')
        # Affichage de la grille
        for i in range(w.shape[0]):
            plt.plot(w[i, :, 2], w[i, :, 3], 'k', linewidth=1.)
        for i in range(w.shape[1]):
            plt.plot(w[:, i, 2], w[:, i, 3], 'k', linewidth=1.)
        # Affichage du titre de la figure
        plt.suptitle('Poids dans l\'espace d\'entree')
        # Affichage de la figure
        if not interactive:
            plt.show()

    def plot(self):
        '''
    @summary: Affichage des poids du réseau (matrice des poids)
    '''
        # Récupération des poids
        w = numpy.array(self.weightsmap)
        # Création de la figure
        f, a = plt.subplots(w.shape[0], w.shape[1])
        # Affichage des poids dans un sous graphique (suivant sa position de la SOM)
        for i in range(w.shape[0]):
            for j in range(w.shape[1]):
                plt.subplot(w.shape[0], w.shape[1], i * w.shape[1] + j + 1)
                im = plt.imshow(w[i, j].reshape(self.inputsize), interpolation='nearest', vmin=numpy.min(w),
                                vmax=numpy.max(w), cmap='binary')
                plt.xticks([])
                plt.yticks([])
        # Affichage de l'échelle
        f.subplots_adjust(right=0.8)
        cbar_ax = f.add_axes([0.85, 0.15, 0.05, 0.7])
        f.colorbar(im, cax=cbar_ax)
        # Affichage du titre de la figure
        plt.suptitle('Poids dans l\'espace de la carte')
        # Affichage de la figure
        plt.show()

    def MSE(self, X):
        '''
    @summary: Calcul de l'erreur de quantification vectorielle moyenne du réseau sur le jeu de données
    @param X: le jeu de données
    @type X: numpy array
    '''
        # On récupère le nombre d'exemples
        nsamples = X.shape[0]
        # Somme des erreurs quadratiques
        s = 0
        # Pour tous les exemples du jeu de test
        for x in X:
            # On calcule la distance à chaque poids de neurone
            self.compute(x.flatten())
            # On rajoute la distance minimale au carré à la somme
            s += numpy.min(self.activitymap) ** 2
        # On renvoie l'erreur de quantification vectorielle moyenne
        return s / nsamples

    def get_map_dispertion(self):
        distanceTotal = 0
        for i in range(0, len(self.map)):
            for j in range(0, len(self.map[i])):
                distanceTotal += self.get_distance_with_neighbor(i, j)

        return distanceTotal

    def get_distance_with_neighbor(self, posx, posy):
        distance = 0
        if (posx != 0):
            #  distance+=abs(self.map[posx-1][posy].posx-self.map[posx][posy].posx)**2+abs(self.map[posx-1][posy].posy-self.map[posx][posy].posy)**2
            distance += abs(self.map[posx - 1][posy].weights[0] - self.map[posx][posy].weights[0]) ** 2 + abs(
                self.map[posx - 1][posy].weights[1] - self.map[posx][posy].weights[1]) ** 2
        elif (posx != len(self.map) - 1):
            #  distance += abs(self.map[posx][posy].posx - self.map[posx+1][posy].posx) ** 2 + abs(self.map[posx][posy].posy - self.map[posx+1][posy].posy)**2
            distance += abs(self.map[posx][posy].weights[0] - self.map[posx + 1][posy].weights[0]) ** 2 + abs(
                self.map[posx][posy].weights[1] - self.map[posx + 1][posy].weights[1]) ** 2

        if (posy != 0):
            #  distance += abs(self.map[posx][posy-1].posx - self.map[posx][posy].posx) ** 2 + abs(self.map[posx][posy-1].posy - self.map[posx][posy].posy)**2
            distance += abs(self.map[posx][posy - 1].weights[0] - self.map[posx][posy].weights[0]) ** 2 + abs(
                self.map[posx][posy - 1].weights[1] - self.map[posx][posy].weights[1]) ** 2

        elif posy != len(self.map[posx]) - 1:
            #  distance += abs(self.map[posx][posy].posx - self.map[posx][posy+1].posx) ** 2 + abs(self.map[posx][posy].posy - self.map[posx][posy+1].posy) ** 2
            distance += abs(self.map[posx][posy].weights[0] - self.map[posx][posy + 1].weights[0]) ** 2 + abs(
                self.map[posx][posy].weights[1] - self.map[posx][posy + 1].weights[1]) ** 2
        return distance
    

    
    def find_hand_position_v1(self, map, motrice_position):
        closest_value=pow(pow(map[0][0].weights[0]-motrice_position[0],2)+pow(map[0][0].weights[1]-motrice_position[1],2),0.5)
        closest_index=(0,0)

        for i in range(len(map)):
            for j in range(len(map[i])):
                if pow(pow((map[i][j].weights[0]-motrice_position[0]),2)+pow((map[i][j].weights[1]-motrice_position[1]),2),0.5)<closest_value:
                    closest_value=pow(pow((map[i][j].weights[0]-motrice_position[0]),2)+pow((map[i][j].weights[1]-motrice_position[1]),2),0.5)
                    closest_index=(i,j)

        return ((map[closest_index[0]][closest_index[1]].weights[0],map[closest_index[0]][closest_index[1]].weights[1]),(map[closest_index[0]][closest_index[1]].weights[2],map[closest_index[0]][closest_index[1]].weights[3]))



    def find_hand_position_v2(self, map, motrice_position, nb_values):
        closest_values=[]

        for i in range(len(map)):
            for j  in range(len(map[i])):
                if len(closest_values)<nb_values:
                    closest_values.append(((i,j),pow(pow(map[i][j].weights[0]-motrice_position[0],2)+pow(map[i][j].weights[1]-motrice_position[1],2),0.5)))
                    closest_values.sort(key=lambda x: x[1])
                elif pow(pow(map[i][j].weights[0]-motrice_position[0],2)+pow(map[i][j].weights[1]-motrice_position[1],2),0.5)<closest_values[nb_values-1][1]:
                    closest_values[nb_values-1]=((i,j),pow(pow(map[i][j].weights[0]-motrice_position[0],2)+pow(map[i][j].weights[1]-motrice_position[1],2),0.5))
                    closest_values.sort(key=lambda x: x[1])

        result_x=0
        result_y=0

        for i in range(nb_values):
            result_x+=map[closest_values[i][0][0]][closest_values[i][0][1]].weights[2]
            result_y+=map[closest_values[i][0][0]][closest_values[i][0][1]].weights[3]

        result_x/=nb_values
        result_y/=nb_values        

        return ([closest_values[i][0] for i in range(nb_values)],(result_x,result_y))
    

    
    def find_hand_position_v3(self, map, motrice_position, nb_values):
        closest_values=[]

        for i in range(len(map)):
            for j  in range(len(map[i])):
                if len(closest_values)<nb_values:
                    closest_values.append(((i,j),pow(pow(map[i][j].weights[0]-motrice_position[0],2)+pow(map[i][j].weights[1]-motrice_position[1],2),0.5)))
                    closest_values.sort(key=lambda x: x[1])
                elif pow(pow(map[i][j].weights[0]-motrice_position[0],2)+pow(map[i][j].weights[1]-motrice_position[1],2),0.5)<closest_values[nb_values-1][1]:
                    closest_values[nb_values-1]=((i,j),pow(pow(map[i][j].weights[0]-motrice_position[0],2)+pow(map[i][j].weights[1]-motrice_position[1],2),0.5))
                    closest_values.sort(key=lambda x: x[1])


        total_distance=sum(closest_values[i][1] for i in range(nb_values))
    
        result_x=0
        result_y=0

        for i in range(nb_values):
            dist=(1-(closest_values[i][1]/total_distance))/(nb_values-1)
            result_x+=map[closest_values[i][0][0]][closest_values[i][0][1]].weights[2]*dist
            result_y+=map[closest_values[i][0][0]][closest_values[i][0][1]].weights[3]*dist

        return ([closest_values[i][0] for i in range(nb_values)],(result_x,result_y))
    

    
    def mouvement_v1(self,map, from_pos,to_pos,nb_steps):
        hand_steps=[]
        for index in range(nb_steps-1):
            x=(from_pos[0]+(index/(nb_steps-1))*(to_pos[0]-from_pos[0]))
            y=(from_pos[1]+(index/(nb_steps-1))*(to_pos[1]-from_pos[1]))
            pos_hand=self.find_hand_position_v1(map,(x,y))
            hand_steps.append((pos_hand[0],pos_hand[1]))


        pos_hand=self.find_hand_position_v1(map,(to_pos[0],to_pos[1]))
        hand_steps.append((pos_hand[0],pos_hand[1]))
        
        return hand_steps
    
    def mouvement_v2(self,map, from_pos,to_pos,nb_steps):
        hand_steps=[]
        for index in range(nb_steps-1):
            x=(from_pos[0]+(index/(nb_steps-1))*(to_pos[0]-from_pos[0]))
            y=(from_pos[1]+(index/(nb_steps-1))*(to_pos[1]-from_pos[1]))
            pos_hand=self.find_hand_position_v2(map,(x,y),4)
            hand_steps.append((pos_hand[0],pos_hand[1]))


        pos_hand=self.find_hand_position_v2(map,(to_pos[0],to_pos[1]),3)
        hand_steps.append((pos_hand[0],pos_hand[1]))
        
        return hand_steps
    
    def mouvement_v3(self,map, from_pos,to_pos,nb_steps):
        hand_steps=[]
        for index in range(nb_steps-1):
            x=(from_pos[0]+(index/(nb_steps-1))*(to_pos[0]-from_pos[0]))
            y=(from_pos[1]+(index/(nb_steps-1))*(to_pos[1]-from_pos[1]))
            pos_hand=self.find_hand_position_v3(map,(x,y),4)
            hand_steps.append((pos_hand[0],pos_hand[1]))


        pos_hand=self.find_hand_position_v3(map,(to_pos[0],to_pos[1]),3)
        hand_steps.append((pos_hand[0],pos_hand[1]))
        
        return hand_steps


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # os.curdir
    for fichier in os.listdir("./generatedImage"):
        os.remove("./generatedImage/" + fichier)

    # Création d'un réseau avec une entrée (2,1) et une carte (10,10)
    # TODO mettre à jour la taille des données d'entrée pour les données robotiques
    network = SOM((2, 2), (10, 10))
    # PARAMÈTRES DU RÉSEAU
    # Taux d'apprentissage
    ETA = 0.1 # Par défaut à 0.05
    # Largeur du voisinage
    SIGMA = 0.9 # Par défaut à 1.4
    # Nombre de pas de temps d'apprentissage
    N = 30000 # Par défaut à 30000
    # Affichage interactif de l'évolution du réseau
    # TODO à mettre à faux pour que les simulations aillent plus vite
    VERBOSE = True
    # Nombre de pas de temps avant rafraissichement de l'affichage
    NAFFICHAGE = 1000 # Par défaut à 1000
    # DONNÉES D'APPRENTISSAGE
    # Nombre de données à générer pour les ensembles 1, 2 et 3
    # TODO décommenter les données souhaitées
    nsamples = 1200 # Par défaut à 1200

    # Ensemble de données 1
    # samples = numpy.random.random((nsamples, 2, 1)) * 2 - 1

    # Ensemble de données 2
    # samples1 = -numpy.random.random((nsamples//3,2,1))
    # samples2 = numpy.random.random((nsamples//3,2,1))
    # samples2[:,0,:] -= 1
    # samples3 = numpy.random.random((nsamples//3,2,1))
    # samples3[:,1,:] -= 1
    # samples = numpy.concatenate((samples1,samples2,samples3))

    # Ensemble de données 3
    # samples1 = numpy.random.random((nsamples//2,2,1))
    # samples1[:,0,:] -= 1
    # samples2 = numpy.random.random((nsamples//2,2,1))
    # samples2[:,1,:] -= 1
    # samples = numpy.concatenate((samples1,samples2))

    # Ensemble de données 4
    # samples1 = numpy.random.random((nsamples//4,2,1))
    # samples1[:,0] -= 1
    # samples1[:,1] *= 2
    # samples1[:,1] -= 1
    # samples2 = numpy.random.random((nsamples//4*1,2,1))
    # samples2[:,1] *= 2
    # samples2[:,1] -= 1
    # samples = numpy.concatenate((samples1,samples2))

    # Ensemble de données 5
    # samples1 = numpy.random.random((nsamples//8,2,1))
    # samples1[:,0] -= 1
    # samples1[:,1] *= 2
    # samples1[:,1] -= 1
    # samples2 = numpy.random.random((nsamples//8*7,2,1))
    # samples2[:,1] *= 2
    # samples2[:,1] -= 1
    # samples = numpy.concatenate((samples1,samples2))

    # Ensemble de données 6
    # samples1 = numpy.random.random((nsamples//4,2,1))*2-1
    # samples2 = numpy.random.random((nsamples//4*3,2,1))
    # samples = numpy.concatenate((samples1,samples2))

    # Ensemble de données robotiques
    samples = numpy.random.random((nsamples,4,1))
    samples[:,0:2,:] *= numpy.pi
    l1 = 0.7
    l2 = 0.3
    samples[:,2,:] = l1*numpy.cos(samples[:,0,:])+l2*numpy.cos(samples[:,0,:]+samples[:,1,:])
    samples[:,3,:] = l1*numpy.sin(samples[:,0,:])+l2*numpy.sin(samples[:,0,:]+samples[:,1,:])

    motrice_test_position=(numpy.random.rand()*2.5+0.5,numpy.random.rand()*2.5+0.5)
    print(f"Position motrice: {motrice_test_position[0]}:{motrice_test_position[1]}")

    ideal=(l1*numpy.cos(motrice_test_position[0])+l2*numpy.cos(motrice_test_position[0]+motrice_test_position[1]),l1*numpy.sin(motrice_test_position[0])+l2*numpy.sin(motrice_test_position[0]+motrice_test_position[1]))
    # print(f"Position idéale: {ideal[0]}:{ideal[1]}")
    # print()


    # Affichage des données (pour les ensembles 1, 2 et 3)
    # plt.figure()
    # plt.scatter(samples[:, 0, 0], samples[:, 1, 0])
    # plt.xlim(-1, 1)
    # plt.ylim(-1, 1)
    # plt.suptitle('Donnees apprentissage')
    # plt.show()


    # SIMULATION
    # Affichage des poids du réseau
    network.plot()
    # Initialisation de l'affichage interactif
    if VERBOSE:
        # Création d'une figure
        plt.figure(figsize=(10, 5))
        # Mode interactif
        plt.ion()
        # Affichage de la figure
        plt.show()
    # Boucle d'apprentissage
    for i in range(N + 1):
        # Choix d'un exemple aléatoire pour l'entrée courante
        index = numpy.random.randint(nsamples)
        x = samples[index].flatten()
        # Calcul de l'activité du réseau
        network.compute(x)
        # Modification des poids du réseau
        network.learn(ETA, SIGMA, x)
        # Mise à jour de l'affichage
        if VERBOSE and i % NAFFICHAGE == 0:
            # Effacement du contenu de la figure
            plt.clf()
            # Remplissage de la figure
            # TODO à remplacer par scatter_plot_2 pour les données robotiques
            network.scatter_plot_2(True)
            # Affichage du contenu de la figure
            plt.pause(0.00001)
            plt.draw()
            plt.savefig("generatedImage/" + str(i) + ".png")
    # Fin de l'affichage interactif
    if VERBOSE:
    
        # Désactivation du mode interactif
        result=network.find_hand_position_v1(network.map, motrice_test_position)

        plt.subplot(1, 2, 1)
        plt.scatter(samples[:,0,0].flatten(),samples[:,1,0].flatten(),c='lightgray',s=10)
        plt.scatter(motrice_test_position[0],motrice_test_position[1],c='green')
        plt.scatter(result[0][0],result[0][1],c='red')
        plt.subplot(1, 2, 2)
        plt.scatter(samples[:,2,0].flatten(),samples[:,3,0].flatten(),c='lightgray',s=10)
        plt.scatter(ideal[0],ideal[1],c='green')
        plt.scatter(result[1][0],result[1][1],c='red')
        plt.suptitle('Réultat avec la méthode v1')
        plt.savefig("generatedImage/figure1.png")
        plt.draw()
        plt.pause(2)

        
        result2=network.find_hand_position_v2(network.map, motrice_test_position,4)

        plt.clf()
        network.scatter_plot_2(True)
        plt.subplot(1, 2, 1)
        plt.scatter(samples[:,0,0].flatten(),samples[:,1,0].flatten(),c='lightgray',s=10)
        plt.scatter(motrice_test_position[0],motrice_test_position[1],c='green')
        for i in range(4):
            plt.scatter(network.map[result2[0][i][0]][result2[0][i][1]].weights[0],network.map[result2[0][i][0]][result2[0][i][1]].weights[1],c='red')
        plt.subplot(1, 2, 2)
        plt.scatter(samples[:,2,0].flatten(),samples[:,3,0].flatten(),c='lightgray',s=10)
        plt.scatter(ideal[0],ideal[1],c='green')
        plt.scatter(result2[1][0],result2[1][1],c='red')
        plt.suptitle('Réultat avec la méthode v2')
        plt.savefig("generatedImage/figure2.png")
        plt.draw()
        plt.pause(2)


        result3=network.find_hand_position_v3(network.map, motrice_test_position,4)

        plt.clf()
        network.scatter_plot_2(True)
        plt.subplot(1, 2, 1)
        plt.scatter(samples[:,0,0].flatten(),samples[:,1,0].flatten(),c='lightgray',s=10)
        plt.scatter(motrice_test_position[0],motrice_test_position[1],c='green')
        for i in range(4):
            plt.scatter(network.map[result3[0][i][0]][result3[0][i][1]].weights[0],network.map[result3[0][i][0]][result3[0][i][1]].weights[1],c='red')
        plt.subplot(1, 2, 2)
        plt.scatter(samples[:,2,0].flatten(),samples[:,3,0].flatten(),c='lightgray',s=10)
        plt.scatter(ideal[0],ideal[1],c='green')
        plt.scatter(result3[1][0],result3[1][1],c='red')
        plt.suptitle('Réultat avec la méthode v3')
        plt.savefig("generatedImage/figure3.png")
        plt.draw()
        plt.pause(2)

        
        plt.clf()
        network.scatter_plot_2(True)
        plt.subplot(1, 2, 1)
        plt.scatter(samples[:,0,0].flatten(),samples[:,1,0].flatten(),c='lightgray',s=10)
        plt.scatter(motrice_test_position[0],motrice_test_position[1],c='green')
        plt.subplot(1, 2, 2)
        plt.scatter(samples[:,2,0].flatten(),samples[:,3,0].flatten(),c='lightgray',s=10)
        plt.scatter(ideal[0],ideal[1],c='green')
        plt.scatter(result[1][0],result[1][1],c='red')
        plt.scatter(result2[1][0],result2[1][1],c='blue')
        plt.scatter(result3[1][0],result3[1][1],c='gold')
        plt.suptitle('Réultat avec les différents méthodes')
        plt.savefig("generatedImage/figure4.png")
        plt.draw()
        plt.pause(2)


        #pos1=(numpy.random.rand()*2.5+0.5,numpy.random.rand()*2.5+0.5)
        #pos2=(numpy.random.rand()*2.5+0.5,numpy.random.rand()*2.5+0.5)
        pos1=(1,1)
        pos2=(2.5,2.5)
        result4=network.mouvement_v1(network.map, pos1,pos2,10)

        plt.clf()
        network.scatter_plot_2(True)
        plt.subplot(1, 2, 1)
        plt.scatter(samples[:,0,0].flatten(),samples[:,1,0].flatten(),c='lightgray',s=10)
        plt.plot((pos1[0],pos2[0]),(pos1[1],pos2[1]),c='red')
        plt.subplot(1, 2, 2)
        plt.scatter(samples[:,2,0].flatten(),samples[:,3,0].flatten(),c='lightgray',s=10)
        plt.plot([point[1][0] for point in result4],[point[1][1] for point in result4],c="red")
        plt.suptitle('Réultat avec la méthode v1')
        plt.savefig("generatedImage/figure5.png")
        plt.draw()
        plt.pause(2)


        result5=network.mouvement_v2(network.map, pos1,pos2,10)

        plt.clf()
        network.scatter_plot_2(True)
        plt.subplot(1, 2, 1)
        plt.scatter(samples[:,0,0].flatten(),samples[:,1,0].flatten(),c='lightgray',s=10)
        plt.plot((pos1[0],pos2[0]),(pos1[1],pos2[1]),c='red')
        plt.subplot(1, 2, 2)
        plt.scatter(samples[:,2,0].flatten(),samples[:,3,0].flatten(),c='lightgray',s=10)
        plt.plot([point[1][0] for point in result5],[point[1][1] for point in result5],c="red")
        plt.suptitle('Réultat avec la méthode v2')
        plt.savefig("generatedImage/figure6.png")
        plt.draw()
        plt.pause(2)
        
        
        result6=network.mouvement_v3(network.map, pos1,pos2,10)

        plt.clf()
        network.scatter_plot_2(True)
        plt.subplot(1, 2, 1)
        plt.scatter(samples[:,0,0].flatten(),samples[:,1,0].flatten(),c='lightgray',s=10)
        plt.plot((pos1[0],pos2[0]),(pos1[1],pos2[1]),c='red')
        plt.subplot(1, 2, 2)
        plt.scatter(samples[:,2,0].flatten(),samples[:,3,0].flatten(),c='lightgray',s=10)
        plt.plot([point[1][0] for point in result6],[point[1][1] for point in result6],c="red")
        plt.suptitle('Réultat avec la méthode v3')
        plt.savefig("generatedImage/figure7.png")
        plt.draw()
        plt.pause(2)

        plt.clf()
        network.scatter_plot_2(True)
        plt.subplot(1, 2, 1)
        plt.scatter(samples[:,0,0].flatten(),samples[:,1,0].flatten(),c='lightgray',s=10)
        plt.plot((pos1[0],pos2[0]),(pos1[1],pos2[1]),c='red')
        plt.subplot(1, 2, 2)
        plt.scatter(samples[:,2,0].flatten(),samples[:,3,0].flatten(),c='lightgray',s=10)
        plt.plot([point[1][0] for point in result4],[point[1][1] for point in result4],c="red")
        plt.plot([point[1][0] for point in result5],[point[1][1] for point in result5],c="blue")
        plt.plot([point[1][0] for point in result6],[point[1][1] for point in result6],c="gold")
        plt.suptitle('Réultat avec toutes les méthodes')
        plt.savefig("generatedImage/figure8.png")
        plt.draw()
        plt.pause(2)


        # Désactivation du mode interactif
        plt.ioff()
    # Affichage des poids du réseau
    network.plot()



    # print(f"Position idéale: {ideal[0]}:{ideal[1]}")
    

    # print(f"Position calculé: {result[0]}:{result[1]}")
    # print(f"Distance à l'idéal: {abs(ideal[0]-result[0])+abs(ideal[1]-result[1])}")
    # print()

    #
    # print(f"Position calculé 2: {result2[0]}:{result2[1]}")
    # print(f"Distance à l'idéal: {abs(ideal[0]-result2[0])+abs(ideal[1]-result2[1])}")
    # print()

    #result3=network.find_hand_position_v2(network.map, motrice_test_position,3)
    # print(f"Position calculé 3: {result3[0]}:{result3[1]}")
    # print(f"Distance à l'idéal: {abs(ideal[0]-result3[0])+abs(ideal[1]-result3[1])}")
    # print()

    #result4=network.find_hand_position_v3(network.map, motrice_test_position,5)
    # print(f"Position calculé 4: {result4[0]}:{result4[1]}")
    # print(f"Distance à l'idéal: {abs(ideal[0]-result4[0])+abs(ideal[1]-result4[1])}")
    # print()

    #result5=network.find_hand_position_v3(network.map, motrice_test_position,3)
    # print(f"Position calculé 5: {result5[0]}:{result5[1]}")
    # print(f"Distance à l'idéal: {abs(ideal[0]-result5[0])+abs(ideal[1]-result5[1])}")
    # print()

    print(str(pow(pow(ideal[0]-result[1][0],2)+pow(ideal[1]-result[1][1],2),0.5)).replace('.',',').replace('[','').replace(']',''))
    print(str(pow(pow(ideal[0]-result2[1][0],2)+pow(ideal[1]-result2[1][1],2),0.5)).replace('.',',').replace('[','').replace(']',''))
    print(str(pow(pow(ideal[0]-result3[1][0],2)+pow(ideal[1]-result3[1][1],2),0.5)).replace('.',',').replace('[','').replace(']',''))

    # begin=(numpy.random.rand()*numpy.pi,numpy.random.rand()*numpy.pi)
    # end=(numpy.random.rand()*numpy.pi,numpy.random.rand()*numpy.pi)

    # begin=(0,0)
    # end=(3,3)

    # result6=network.mouvement_v1(network.map,begin,end,25)

    # result7=network.mouvement_v2(network.map,begin,end,25)

    # result8=network.mouvement_v3(network.map,begin,end,25)

    # Affichage des données (pour l'ensemble robotique)
    # plt.figure()

    # plt.subplot(1,2,1)
    # plt.scatter(network.map[:,0,0].flatten(),network.map[:,1,0].flatten(),c='lightgray',s=10)
    # plt.scatter(motrice_test_position[0],motrice_test_position[1],c='black')
    # x_values = [point[0] for point in result7]
    # y_values = [point[1] for point in result7]
    # plt.plot(x_values,y_values,c='black')

    # plt.subplot(1,2,2)
    # plt.scatter(network.map[:,2,0].flatten(),network.map[:,3,0].flatten(),c='lightgray',s=10)

    # plt.scatter(result[0],result[1],c='blue')
    # plt.scatter(result3[0],result3[1],c='green')
    # plt.scatter(result5[0],result5[1],c='red')

    # x_values = [point[2] for point in result6]
    # y_values = [point[3] for point in result6]
    # plt.plot(x_values,y_values,c='blue')

    # x_values = [point[2] for point in result7]
    # y_values = [point[3] for point in result7]
    # plt.plot(x_values,y_values,c='green')

    # x_values = [point[2] for point in result8]
    # y_values = [point[3] for point in result8]
    # plt.plot(x_values,y_values,c='red')

    # plt.suptitle('Donnees apprentissage')
    #plt.show()

    # Affichage de l'erreur de quantification vectorielle moyenne après apprentissage
    print("erreur de quantification vectorielle moyenne ", network.MSE(samples))
    print("coef de relachement ", network.get_map_dispertion())