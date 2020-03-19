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


class Strategy(object):
    def __init__(self,wallet=None,binance_client = None,symbol=None,filename = 'network.model'):
        wandb.init(project="cryp")
        self.symbol = symbol
        self.binance_client = binance_client
        self.filename = filename
        self.model = Model.Model()
        structure,fitness = self.model.load(filename=filename)
        self.model_interval = structure[0]
        Logger.Log('Interval that is fed to network has length: ' + str(self.model_interval))
        data = self.get_data(binance_client=binance_client)
        network_data = np.array(data)[:,1]
        network_data = [float(data) for data in network_data]
        network_da = [float(float(network_data[i])/float(network_data[i-1]))-1 for i in range(1,len(network_data))]
        network_da = np.array(network_da)
        self.train(network_da)
        #remove everything under this and the pandas package dependency if you want to run on raspberry pi
        df = pd.DataFrame({
            'real_price':network_da[self.model_interval:-1],
            'predicted_price':self.prediction_results(data=network_da,interval_size=self.model_interval)
        })
        ax = plt.gca()
        df.plot(kind='line', y='real_price', ax=ax)
        df.plot(kind='line', y='predicted_price', color='red', ax=ax)
        plt.show()

    def train(self,data,accuracy = 0.000001):
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
            if maxdir<=0 and maxdir_type!='None':
                if maxdir_sub == True:
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

    def run_over_data(self,data,interval_size,model):
        afwijkingen = []
        for i in range(len(data) - interval_size-1):
            afwijkingen.append(abs(abs(model.predict(inputs=data[i:i + interval_size]))-abs(data[i+interval_size+1])))
        return afwijkingen
    def get_data(self,binance_client = None,klineinterval = Client.KLINE_INTERVAL_30MINUTE,datetime_start = None,datetime_end = None):
        data = binance_client.get_historical_klines(self.symbol,klineinterval,'28 Januari, 2020','31 Januari, 2020')
        #data = binance_client.get_historical_klines(self.wallet.symbol,klineinterval,'25 Januari, 2020',datetime.datetime.now().ctime())

        return data
    def prediction_results(self,data,interval_size):
        voorspellingen = []
        for i in range(len(data) - interval_size-1):
            voorspellingen.append(self.model.predict(inputs=data[i:i + interval_size]).tolist()[0][0])
        return voorspellingen
    def init_strategy(self):
        Logger.Log('Starting algorithm')
        Logger.Log('Placing buy order')


