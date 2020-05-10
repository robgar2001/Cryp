import Logger
from binance.client import Client
import numpy as np
from AI import Model
import Wallet
import pandas as pd
import matplotlib.pyplot as plt
import wandb
import datetime
import copy
import sys
import Data

import GradientDescent


class Strategy(object):
    def __init__(self,symbol: str,binance_client : Client ,filename = 'network.model'):
        wandb.init(project="cryp")
        self.symbol = symbol
        self.binance_client = binance_client
        self.filename = filename
        self.model = Model.Model()
        structure,fitness = self.model.load(filename=filename)
        self.model_interval = structure[0]
        Logger.Log('Interval that is fed to network has length: ' + str(self.model_interval))
        #call datamanager for data
        self.datamanager = Data.DataManager(client=binance_client,symbol=symbol,klineinterval=Client.KLINE_INTERVAL_30MINUTE)
        data = self.datamanager.get_data()
        for x in data:
            print(float(x))
        gd = GradientDescent.GradientDescent(self.model)
        gd.start()
        # self.train(data=data)
        # real_price = [x.data for x in data[self.model_interval:-1]]
        # real_prediction_results = [x.data for x in self.prediction_results(data=data, interval_size=self.model_interval)]
        #
        # df = pd.DataFrame({
        #     'real_price': real_price,
        #     'predicted_price': real_prediction_results
        # })
        # ax = plt.gca()
        # df.plot(kind='line', y='real_price', ax=ax)
        # df.plot(kind='line', y='predicted_price', color='red', ax=ax)
        # plt.show()

    def train(self,data,accuracy = 0.0001):
        def eval(model):
            fitness = self.fitness(self.run_over_data(data=data, model=model,interval_size=self.model_interval))
            return fitness
        fitness = eval(self.model)
        Logger.Log('Starting fitness of network is: %f'%(fitness))

        maxdir = 0
        maxdir_tup = None
        maxdir_sub = False
        maxdir_type = 'None'
        min_fitness = fitness
        while fitness==min_fitness:
            for l in range(1,len(self.model.layers)):
                for n in range(len(self.model.layers[l].neurons)):
                    #check if bias update meight be smartest dicision
                    model_list_bias = [copy.deepcopy(self.model) for _ in range(2)]
                    model_list_bias[0].layers[l].neurons[n].bias+=accuracy
                    model_list_bias[1].layers[l].neurons[n].bias-=accuracy
                    dir_list_bias = [fitness - eval(model) for model in model_list_bias]
                    if(min(dir_list_bias)<maxdir):
                        if(dir_list_bias.index(min(dir_list_bias))==0):
                            maxdir_sub=False
                        else:
                            maxdir_sub=True
                        maxdir = min(dir_list_bias)
                        maxdir_tup = (l,n)
                        maxdir_type = 'bias'

                    for w in range(len(self.model.layers[l-1].neurons)):
                        model_list = [copy.deepcopy(self.model) for _ in range(2)]
                        model_list[0].layers[l].neurons[n].weights[w] += accuracy
                        model_list[1].layers[l].neurons[n].weights[w] -=accuracy
                        dir_list = [fitness-eval(model) for model in model_list]
                        if(min(dir_list)<maxdir):
                            if(dir_list.index(min(dir_list))) == 0:
                                maxdir_sub = False
                            else:
                                maxdir_sub = True
                            maxdir = min(dir_list)
                            maxdir_tup = (l,n,w)
                            maxdir_type = 'weight'
            if maxdir <= 0 and maxdir_type != 'None':
                if maxdir_sub:
                    if maxdir_type == 'weight':
                        Logger.Log('Subtracting form weight')
                        self.model.layers[maxdir_tup[0]].neurons[maxdir_tup[1]].weights[maxdir_tup[2]] -=accuracy
                    else:
                        Logger.Log('Subtracting from bias')
                        self.model.layers[maxdir_tup[0]].neurons[maxdir_tup[1]].bias-=accuracy
                else:
                    if maxdir_type == 'weight':
                        Logger.Log('Adding to weight')
                        self.model.layers[maxdir_tup[0]].neurons[maxdir_tup[1]].weights[maxdir_tup[2]] +=accuracy
                    else:
                        Logger.Log('Adding to bias')
                        self.model.layers[maxdir_tup[0]].neurons[maxdir_tup[1]].bias+=accuracy
            fitness = eval(self.model)
            if fitness>min_fitness:
                min_fitness = fitness
            Logger.Log(str(maxdir)+' '+str(fitness)+' '+maxdir_type)
            self.model.save(filename=self.filename,fitness=fitness)
        return

    def fitness(self,afwijkingen):
        #plus 1 door convergentie wanneer de afwijkingen kleiner is dan 0
        #Logger.Log(-((np.sum(afwijkingen)+1)**2))
        return -((np.sum(afwijkingen)+1)**2)

    def run_over_data(self, data, interval_size, model):
        afwijkingen = []
        for i in range(len(data) - interval_size-1):
            #carefull with slicing of data, when slicing the last given element is not taken with it in the slice
            #checked, the right information is fed to the network
            afwijkingen.append(abs(abs(model.predict(inputs=data[i:i + interval_size]))-abs(data[i+interval_size])))
        print(afwijkingen)
        return afwijkingen
    def prediction_results(self, data, interval_size):
        voorspellingen = []
        for i in range(len(data) - interval_size-1):
            #id's must be matched
            voorspellingen.append(PredictionResult(id=i+interval_size,data=self.model.predict(inputs=data[i:i + interval_size]).tolist()[0][0]))
        return voorspellingen

class PredictionResult(Data.Candle):
    def __init__(self,id,data):
        super().__init__(id=id,data=data)