import math
import Logger
import numpy as np
import numpy.random as random
import wandb

class Neuron(object):
    def __init__(self,weights,bias=0,neuron_id = None,layer_id = None):
        #just data holder for neuron information
        self.weights = np.array(weights)
        self.bias = bias
        self.layer_id = layer_id
        self.neuron_id = neuron_id
        Logger.Log('Neuron initiated with id '+str(self.neuron_id)+' in layer '+str(self.layer_id))
class Layer(object):
    def __init__(self,N_neurons,L_Layers_N_neuron,layer_id=None):
        self.layer_id = layer_id
        if layer_id!=0:
            self.neurons = [Neuron(neuron_id = i,layer_id=layer_id,weights=[0 for x in range(L_Layers_N_neuron[self.layer_id-1])]) for i in range(N_neurons)]
        else:
            self.neurons = [Neuron(neuron_id=i, layer_id=layer_id, weights=None)for i in range(N_neurons)]
    def weight_matrix(self):
        return np.array([[w for w in neuron.weights] for neuron in self.neurons])
    def bias_matrix(self):
        biaslist = np.array([[neuron.bias for neuron in self.neurons]])
        _,M = biaslist.shape
        return biaslist.reshape((M,1))
class Model(object):
    def create_structure(self):
        self.layers = [Layer(L_Layers_N_neuron=self.network_config,N_neurons=self.network_config[i],layer_id=i) for i in range(len(self.network_config))]
    def activation_function(self,value):
        return (np.tanh(value))
    def predict(self,inputs):
        inputs = [float(i) for i in inputs]
        if len(inputs) != len(self.layers[0].neurons):
            Logger.Log('Input size is different from input layer size')
            return None
        values = np.array([inputs])
        _,M = values.shape
        values = np.reshape(values,(M,1))
        for l in range(1,len(self.layers)):
            inputs = values.copy()
            weights = self.layers[l].weight_matrix()
            biases = self.layers[l].bias_matrix()
            outputs = self.activation_function((weights@values)+biases)
            values = outputs.copy()
        return values
    def __str__(self):
        for l in range(0,len(self.layers)):
            for n in range(len(self.layers[l].neurons)):
                Logger.Log('Neuron '+str(self.layers[l].neurons[n].neuron_id)+' in layer: '+str(self.layers[l].neurons[n].layer_id)+ ' has weights and bias'+str(self.layers[l].neurons[n].weights)+' bias: ' +str(self.layers[l].neurons[n].bias))
        return 'MODEL PRINT RESULT'
    def assign_start_weights(self):
        for l in self.layers[1:]:
            for n in l.neurons:
                n.weights = random.ranf(len(n.weights)).tolist()
        Logger.Log('Assigned random weights')
    def load(self,filename='network.model',load_offset = 2):
        """
        Load a neural network by filename and return the structure and the maxfitness
        """
        Logger.Log('Loading %s'%(filename))
        file = open(filename,'r')
        lines = file.readlines()
        structure = lines[0].strip('\n').split('/')
        structure = [int(x) for x in structure]
        self.network_config = structure
        self.create_structure()
        Logger.Log(structure)
        for l in range(load_offset,len(lines)):
            line = lines[l]
            line = line.strip('\n')
            data = line.split('/')
            Logger.Log('Loading in model line: '+str(data))
            layer = int(data[0])
            neuron = int(data[1])
            weightstext = data[2][1:-2]
            weights = [float(x) for x in weightstext.split(',')]
            bias = float(data[3])
            self.layers[int(data[0])].neurons[int(data[1])].weights = weights
            self.layers[int(data[0])].neurons[int(data[1])].bias = float(data[3])
        file.close()
        return structure,float(lines[1])
    def save(self,filename='network.model',fitness = 0):
        Logger.Log('saving file')
        file = open(filename,'w')
        structure = ''
        for l in self.layers:
            structure+=str(len(l.neurons))+'/'
        structure = structure[:len(structure)-1]
        file.write(structure+'\n')
        file.write(str(fitness)+'\n')
        for l in self.layers[1:]:
            for n in l.neurons:
                weights = '['
                for x in n.weights:
                    weights+=str(x)+','
                weights = weights[0:-2]
                weights+=']'
                file.write(str(n.layer_id)+'/'+str(n.neuron_id)+'/'+str(weights)+'/'+str(n.bias)+'\n')
        file.close()
        Logger.Log(filename+' created')


