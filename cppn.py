import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import constants as c

import math

import numpy as np

from scipy.ndimage import label

class CPPN: 

    def __init__(self):

        self.inputLayer   = np.zeros(c.cppnInputs,dtype='f')

        self.IHWeights    = np.random.uniform( c.cppnInitialMinWeight , c.cppnInitialMaxWeight , [c.cppnInputs,c.cppnHiddens] )

        self.hiddenLayer1 = np.zeros(c.cppnHiddens,dtype='f')

        self.activeLayer1 = {}

        for h in range(c.cppnHiddens):

            activationFunctionType = np.random.randint(c.numCPPNActivationFunctions)

            self.activeLayer1[h] = c.cppnActivationFunctions[activationFunctionType] 

        self.HHWeights    = np.random.uniform( c.cppnInitialMinWeight , c.cppnInitialMaxWeight , [c.cppnHiddens,c.cppnHiddens] )

        self.hiddenLayer2 = np.zeros(c.cppnHiddens,dtype='f')

        self.activeLayer2 = {}

        for h in range(c.cppnHiddens):

            activationFunctionType = np.random.randint(c.numCPPNActivationFunctions)

            self.activeLayer2[h] = c.cppnActivationFunctions[activationFunctionType]

        self.HOWeights    = np.random.uniform( c.cppnInitialMinWeight , c.cppnInitialMaxWeight , [c.cppnHiddens,c.cppnOutputs] )

        self.outputLayer  = np.zeros(c.cppnOutputs,dtype='f')

    def Mutate(self):

        if np.random.randint(2) == 0:

            self.Mutate_A_Weight()
        else:
            self.Mutate_An_Activation_Function()

    def Paint_At_Resolution(self,robot,resolution):

        cols,rows,sheets = robot.shape

        for x in range(cols):
            xScaled = self.Scale_Using_Resolution(x,resolution)
            for y in range(rows):
                yScaled = self.Scale_Using_Resolution(y,resolution)
                for z in range(sheets):
                    zScaled = self.Scale_Using_Resolution(z,resolution)
                    vals = self.Evaluate_At(xScaled,yScaled,zScaled)

                    if vals[0] > 0:
                        robot[x,y,z] = 1
                    else:
                        robot[x,y,z] = 0

        labelledRobot , numComponents = self.Extract_Largest_Component(robot)

        return numComponents

    def Show_At_Resolution(self,resolution):

        robot = np.zeros([resolution,resolution,resolution],dtype='f')

        self.Paint_At_Resolution(robot,resolution)

        facecolors = np.where(robot==2, 'salmon', 'lightgreen')

        fig = plt.figure()

        ax = fig.gca(projection='3d')

        ax.voxels(robot, facecolors=facecolors , edgecolors = 'k')

        plt.show()

# ---------------- Private methods -----------

    def Extract_Largest_Component(self,robot):

        labelledRobot, num_labels = label(robot,structure=[[[0,0,0],[0,1,0],[0,0,0]],[[0,1,0],[1,1,1],[0,1,0]],[[0,0,0],[0,1,0],[0,0,0]]])

        return labelledRobot, np.amax(labelledRobot)

    def Get_Action_From_Outputs(self,outputs):

        possibleActions = outputs[ 0 : c.numEdgeChangeActions ]

        action = np.argmax( possibleActions )

        return action 

    def Get_DeltaX_From_Outputs(self,outputs):

        # return outputs[c.numEdgeChangeActions]

        minusOneToOne = outputs[c.numEdgeChangeActions]

        minusDeltaXToDeltaX = minusOneToOne * c.vectorFieldXDeltaMax

        return minusDeltaXToDeltaX 

    def Get_DeltaY_From_Outputs(self,outputs):

        # return outputs[c.numEdgeChangeActions+1]

        minusOneToOne = outputs[c.numEdgeChangeActions+1]

        minusDeltaYToDeltaY = minusOneToOne * c.vectorFieldYDeltaMax

        return minusDeltaYToDeltaY

    def Evaluate_At(self,x,y,z):

        self.inputLayer[0] = x

        self.inputLayer[1] = y

        self.inputLayer[2] = z

        self.inputLayer[3] = 1 # Bias

        self.hiddenLayer1 = np.dot( self.inputLayer   , self.IHWeights )

        for h in range(c.cppnHiddens):

            self.hiddenLayer1[h] = self.activeLayer1[h]( self.hiddenLayer1[h] )


        self.hiddenLayer2 = np.dot( self.hiddenLayer1 , self.HHWeights )

        for h in range(c.cppnHiddens):

            self.hiddenLayer2[h] = self.activeLayer2[h]( self.hiddenLayer2[h] )


        self.outputLayer  = np.tanh( np.dot( self.hiddenLayer2 , self.HOWeights ) )


        return self.outputLayer 

    def Gaussian(self,x):

        return np.exp( -x**2 / 2.0 )

    def Mutate_A_Weight(self):

        mutateLayer = np.random.randint(3)

        if mutateLayer == 0:

            self.Mutate_A_Weight_In(self.IHWeights)

        elif mutateLayer == 1:

            self.Mutate_A_Weight_In(self.HHWeights)

        else:
            self.Mutate_A_Weight_In(self.HOWeights)

    def Mutate_A_Weight_In(self,W):

        cols, rows = W.shape

        col = np.random.randint(cols)
        row = np.random.randint(rows)

        W[col,row] = np.random.normal( loc = W[col,row] , scale = np.abs(W[col,row]) )

    def Mutate_An_Activation_Function(self):

        mutateLayer = np.random.randint(2)

        if mutateLayer == 0:

            self.Mutate_An_Activation_Function_In(self.activeLayer1)

        elif mutateLayer == 1:

            self.Mutate_An_Activation_Function_In(self.activeLayer2)

    def Mutate_An_Activation_Function_In(self,activeLayer):

        h = np.random.randint(c.cppnHiddens)

        activationFunctionType = np.random.randint(c.numCPPNActivationFunctions)

        activeLayer[h] = c.cppnActivationFunctions[activationFunctionType]

    def Scale_Using_Resolution(self,OldValue,resolution):

        OldMin = 0
        OldMax = resolution - 1

        NewMin = -1.0
        NewMax = +1.0

        OldRange = (OldMax - OldMin)  
        NewRange = (NewMax - NewMin)  
        NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin

        return NewValue
