import copy
import constants as c
import matplotlib.pyplot as plt
import numpy as np
import operator

from cppn import CPPN

class AFPO:

    def __init__(self,randomSeed):

        self.randomSeed = randomSeed

        self.resolution = c.robotResolution

        self.currentGeneration = 0

        self.nextAvailableID = 0

        self.genomes = {}

        for populationPosition in range(c.popSize):

            self.genomes[populationPosition] = CPPN(self.nextAvailableID)

            self.nextAvailableID = self.nextAvailableID + 1

    def Evolve(self):

        pass

        # self.Perform_First_Generation(resolution)

        #for self.currentGeneration in range(1,c.numGenerations):
       
        #    self.Perform_One_Generation(resolution)

# -------------------------- Private methods ----------------------

    def Age(self):

        for cppn in self.cppns:

            self.cppns[cppn].Age()

    def Aggressor_Dominates_Defender(self,aggressor,defender):

        return self.cppns[aggressor].Dominates(self.cppns[defender])

    def Choose_Aggressor(self):

        return np.random.randint(c.popSize)

    def Choose_Defender(self,aggressor):

        defender = np.random.randint(c.popSize)

        while defender == aggressor:

            defender = np.random.randint(c.popSize)

        return defender

    def Contract(self):

        while len(self.cppns) > c.popSize:

            aggressorDominatesDefender = False

            while not aggressorDominatesDefender:

                aggressor = self.Choose_Aggressor()

                defender  = self.Choose_Defender(aggressor)

                aggressorDominatesDefender = self.Aggressor_Dominates_Defender(aggressor,defender)

            for cppnToMove in range(defender,len(self.cppns)-1):

                self.cppns[cppnToMove] = self.cppns.pop(cppnToMove+1)

    def Evaluate_CPPNs(self,resolution):

        for cppn in self.cppns:

            robot = np.zeros([resolution,resolution,resolution],dtype='f')

            self.cppns[cppn].Paint_At_Resolution(robot,resolution)

            self.cppns[cppn].Compute_Fitness(robot)

    def Expand(self):

        popSize = len(self.cppns)

        for newCPPN in range( popSize , 2 * popSize - 1 ):

            spawner = self.Choose_Aggressor()

            self.cppns[newCPPN] = copy.deepcopy( self.cppns[spawner] )

            self.cppns[newCPPN].Set_ID(self.nextAvailableID)

            self.nextAvailableID = self.nextAvailableID + 1

            self.cppns[newCPPN].Mutate()

    def Find_Best_CPPN(self):

        CPPNsSortedByFitness = sorted(self.cppns.values(), key=operator.attrgetter('fitness'),reverse=True)

        return CPPNsSortedByFitness[0]

    def Inject(self):

        popSize = len(self.cppns)

        self.cppns[popSize-1] = CPPN(self.nextAvailableID)

        self.nextAvailableID = self.nextAvailableID + 1

    def Perform_First_Generation(self,resolution):

        self.Evaluate_CPPNs(resolution)

        self.Print()

        self.Save_Best()

    def Perform_One_Generation(self,resolution):

        self.Expand()

        self.Age()

        self.Inject()

        self.Evaluate_CPPNs(resolution)

        self.Contract()

        self.Print()

        self.Save_Best()

    def Print(self):

        print('Generation ', end='')

        print(self.currentGeneration, end='')

        print(' of ', end='')

        print(str(c.numGenerations), end='')

        print(': ', end='')

        bestCPPN = self.Find_Best_CPPN()

        print( str( round(bestCPPN.Get_Fitness()) ) + ' \t' , end = '' )

        print( str( round(bestCPPN.Get_Age()) ) )

    def Save_Best(self):

        bestCPPN = self.Find_Best_CPPN()

        bestCPPN.Save(self.randomSeed)

