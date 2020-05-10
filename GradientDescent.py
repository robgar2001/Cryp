import threading
from AI import Model
import copy
import Logger
#multithreading based gradiend descent over a dataset

class GradientDescent():
    #initialize the gradient descent process
    def __init__(self,model: Model.Model):
        self.model = model
        #for every neuron and weight the model needs a gradient to be determint
        self.partial_gradient_threads = []
    def start(self):
        print(self.model)
        for l in range(1,len(self.model.layers)):
            for n in range(len(self.model.layers[l].neurons)):
                for w in range(len(self.model.layers[l].neurons[n].weights)):
                    Logger.Log('Opening threads for gradient descent')
                    self.partial_gradient_threads.append(threading.Thread(target=self.partial_dirivative_of_neuron,kwargs={'neuron':self.model.layers[l].neurons[n]}).start())





    def partial_dirivative_of_neuron(self,neuron: Model.Neuron,sense=0.0001):
        #calculate the data
        print('Initatiated tread for partial dirivative')
        print(neuron.weights)
        return 0
