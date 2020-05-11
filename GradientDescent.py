import threading
from AI import Model
import copy
import Logger
import time
import numpy as np
#multithreading based gradiend descent over a dataset

class GradientDescent():
    #initialize the gradient descent process
    def __init__(self,model: Model.Model,interval_size:int,data):
        self.model = model
        #for every neuron and weight the model needs a gradient to be determint
        self.partial_gradient_threads = []
        self.gradientDic = {}
        self.data = data
        self.interval_size = interval_size
    def start(self):
        print(self.model)
        self.fitness1 = self.fitness(self.model)
        Logger.Log('STARTING FITNESS IS: '+str(self.fitness1))
        for l in range(1,len(self.model.layers)):
            for n in range(len(self.model.layers[l].neurons)):
                for w in range(len(self.model.layers[l].neurons[n].weights)):
                    self.partial_gradient_threads.append(threading.Thread(target=self.partial_derivative_of_neuron,kwargs={'neuron':self.model.layers[l].neurons[n],'model':copy.deepcopy(self.model),'result_dic':self.gradientDic,'weight_id':w}))
                    self.partial_gradient_threads[-1].start()
        Logger.Log('Waiting for threads to join')
        thread_results = {}
        print(self.partial_gradient_threads)
        for thread in self.partial_gradient_threads:
            thread.join()
        Logger.Log('Threads finished executing')
        print(self.gradientDic)

    def run_over_data(self, data, interval_size, model):
        afwijkingen = []
        for i in range(len(data) - interval_size-1):
            #carefull with slicing of data, when slicing the last given element is not taken with it in the slice
            #checked, the right information is fed to the network
            afwijkingen.append(abs(abs(model.predict(inputs=data[i:i + interval_size]))-abs(data[i+interval_size])))
        return afwijkingen

    def fitness(self,model):
        #determine the fitness
        return -((np.sum(self.run_over_data(data=self.data,interval_size=self.interval_size,model=model)) + 1) ** 2)

    def partial_derivative_of_neuron(self,result_dic: dict,model: Model.Model,neuron: Model.Neuron,weight_id:int,sense=0.0001):
        #calculate the data
        #gradient = d_fitness/d_sense
        #neuron is copied, so we do not permantly apply changes to network
        #this function is heavely multithreaded
        Logger.Log(threading.current_thread().getName()+' '+str(neuron)+' weight_id: '+str(weight_id))
        fitness1 = self.fitness1
        model.layers[neuron.layer_id].neurons[neuron.neuron_id].weights[weight_id] += sense
        fitness2 = self.fitness(model)
        gradient = (fitness2-fitness1)/sense
        result_dic.__setitem__((neuron.layer_id,neuron.neuron_id),gradient)
        return 0
