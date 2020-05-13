import Logger
from binance.client import Client
import numpy as np
from AI import Model
import Wallet
#import pandas as pd
#import matplotlib.pyplot as plt
import wandb
import datetime
import copy
import sys
import Data

import GradientDescent


class Strategy(object):
    def __init__(self,symbol: str,binance_client : Client ,filename = 'network.model',learning_rate = 0.01):
        wandb.init(project="cryp")
        self.learning_rate = learning_rate
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
        self.data = data
        for x in data:
            print(float(x))
        for i in range(1000):
            gd = GradientDescent.GradientDescent(model=self.model,interval_size=self.model_interval,data=data)
            gradient_updates = gd.start()
            self.update_model_from_gradient_dic(gradient_dic=gradient_updates)
            self.model.save(fitness=gd.fitness1)
            # if not (i%100):
            #
            #     real_price = [x.data for x in data[self.model_interval:-1]]
            #     predicted_price_data = self.prediction_run()
            #
            #     df = pd.DataFrame({
            #         'real_price': real_price,
            #         'predicted_price': predicted_price_data
            #     })
            #     ax = plt.gca()
            #     df.plot(kind='line', y='real_price', ax=ax)
            #     df.plot(kind='line', y='predicted_price', color='red', ax=ax)
            #     plt.show()
        # self.train(data=data)

    def update_model_from_gradient_dic(self,gradient_dic: dict):
        for key in gradient_dic.keys():
            layer,neuron,weight = key
            if gradient_dic[key]>0:
                self.model.layers[layer].neurons[neuron].weights[weight]  += -1*self.learning_rate
            else:
                self.model.layers[layer].neurons[neuron].weights[weight] += 1*self.learning_rate
        Logger.Log('Updated all weights based of their gradient dict')
    def prediction_run(self):
        result = []
        for i in range(len(self.data) - self.model_interval - 1):
            result.append(float(self.model.predict(inputs=self.data[i:i + self.model_interval])))
        return result
class PredictionResult(Data.Candle):
    def __init__(self,id,data):
        super().__init__(id=id,data=data)