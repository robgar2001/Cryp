import threading
from AI import Model
import copy
import Logger
import time
#multithreading based gradiend descent over a dataset

class GradientDescent():
    #initialize the gradient descent process
    def __init__(self,model: Model.Model):
        self.model = model
        #for every neuron and weight the model needs a gradient to be determint
        self.partial_gradient_threads = []
        self.gradientDic = {}
    def start(self):
        print(self.model)
        for l in range(1,len(self.model.layers)):
            for n in range(len(self.model.layers[l].neurons)):
                for w in range(len(self.model.layers[l].neurons[n].weights)):
                    self.partial_gradient_threads.append(threading.Thread(target=self.partial_derivative_of_neuron,kwargs={'neuron':self.model.layers[l].neurons[n],'model':copy.deepcopy(self.model),'result_dic':self.gradientDic}))
                    self.partial_gradient_threads[-1].start()
        Logger.Log('Waiting for threads to join')
        thread_results = {}
        print(self.partial_gradient_threads)
        for thread in self.partial_gradient_threads:
            thread.join()
        Logger.Log('Threads finished executing')
        print(self.gradientDic)

    def fitness(self):
        #determine the fitness core
        pass

    def partial_derivative_of_neuron(self,result_dic: dict,model: Model.Model,neuron: Model.Neuron,sense=0.0001):
        #calculate the data
        #gradient = d_fitness/d_sense
        #neuron is copied, so we do not permantly apply changes to network
        Logger.Log(threading.current_thread().getName()+' '+str(neuron))


        result_dic.__setitem__((neuron.layer_id,neuron.neuron_id),0.001)

        return 0
