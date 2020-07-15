import math
import Logger
import numpy as np
import numpy.random as random
import wandb
import json

class Neuron(object):
    def __init__(self,weights,bias=0,neuron_id = None,layer_id = None):
        #just data holder for neuron information
        self.weights = np.array(weights)
        self.bias = bias
        self.layer_id = layer_id
        self.neuron_id = neuron_id
        Logger.Log('Neuron initiated with id '+str(self.neuron_id)+' in layer '+str(self.layer_id))
    def __str__(self):
        return 'Neuron id: %i , layer id: %i'%(self.neuron_id,self.layer_id)
class Layer(object):
    def __init__(self,N_neurons,L_Layers_N_neuron,layer_id=None):
        self.layer_id = layer_id
        if layer_id!=0:
            self.neurons = [Neuron(neuron_id = i,layer_id=layer_id,weights=[0 for x in range(L_Layers_N_neuron[self.layer_id-1])]) for i in range(N_neurons)]
        else:
            self.neurons = [Neuron(neuron_id=i, layer_id=layer_id, weights=0)for i in range(N_neurons)]
    def weight_matrix(self):
        return np.array([[w for w in neuron.weights] for neuron in self.neurons])
    def bias_matrix(self):
        biaslist = np.array([[neuron.bias for neuron in self.neurons]])
        _,M = biaslist.shape
        return biaslist.reshape((M,1))
class Model(object):
    def __get_model_dict__(self):
        try:
            model_dict = {}
            for l in range(1,len(self.layers)):
                for n in self.layers[l].neurons:
                    model_dict['(%i,%i)' % (n.layer_id, n.neuron_id)] = [n.weights, n.bias]
            return model_dict
        except:
            Logger.Log('FAILED to create model dictionairy')
    def create_structure(self):
        self.layers = [Layer(L_Layers_N_neuron=self.network_config,N_neurons=self.network_config[i],layer_id=i) for i in range(len(self.network_config))]
    def activation_function(self,value):
        return (np.tanh(value))
    def predict(self,inputs):
        #only possible when inputs have an id associated with them
        ids = [i.id for i in inputs]
        del ids
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
        model = self.__get_model_dict__()
        return json.dumps(model)
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
        data = json.load(file)
        structure = data['structure'].strip('\n').split('/')
        structure = [int(x) for x in structure]
        self.indicators = data['indicators']
        self.network_config = structure
        self.create_structure()
        model_data = data['model']
        for key in model_data.keys():
            _ = key.replace(')','').replace('(','')
            _ = _.split(',')
            layer = int(_[0])
            neuron = int(_[1])
            self.layers[layer].neurons[neuron].weights = model_data[key][0]
            self.layers[layer].neurons[neuron].bias = model_data[key][1]
        file.close()
        Logger.Log('Loading file completed')
        return structure,data['cost']
    def save(self,filename='network.model',cost = 9999999,indicators=None):
        #must be reworked trough json
        Logger.Log('Saving file to location: %s'%(filename))
        save_dic = {}
        structure = ''
        for l in self.layers:
            structure+=str(len(l.neurons))+'/'
        structure = structure[:len(structure)-1]
        save_dic.__setitem__('structure',structure)
        save_dic['cost'] = cost
        if indicators:
            save_dic['indicators'] = indicators
        else:
            save_dic['indicators'] = self.indicators
        save_dic['model'] = self.__get_model_dict__()

        with open(filename,'w') as file:
            json.dump(save_dic,file,indent=2)
        Logger.Log(filename+' created')


