import Logger
from binance.client import Client
import numpy as np
from AI import Model
import Wallet
import pandas as pd
import matplotlib.pyplot as plt

import datetime
import copy
import sys
import Data

import GradientDescent


class Strategy(object):
    def __init__(self,symbol: str,binance_client : Client ,filename = 'network.model',learning_rate = 0.001,start_date=None,end_date=None):
        self.learning_rate = learning_rate
        self.symbol = symbol
        self.binance_client = binance_client
        self.filename = filename
        self.model = Model.Model()
        structure,fitness = self.model.load(filename=filename)
        self.model_interval = structure[0]
        Logger.Log('Interval that is fed to network has length: ' + str(self.model_interval))
        #call datamanager for data
        self.datamanager = Data.DataManager(client=binance_client,symbol=symbol,klineinterval=Client.KLINE_INTERVAL_30MINUTE,start_date=start_date,end_date=end_date)
        data = self.datamanager.get_data()
        self.data = data
        for i in range(1000):
            gd = GradientDescent.GradientDescent(model=self.model,interval_size=self.model_interval,data=data)
            gradient_updates = gd.start()
            not_finished = self.update_model_from_gradient_dic(gradient_dic=gradient_updates,gradient_descent=gd)
            if not i%1000 or not not_finished:
                real_price = [x.data for x in data[self.model_interval:-1]]
                predicted_price_data = self.prediction_run()

                df = pd.DataFrame({
                    'real_price': real_price,
                    'predicted_price': predicted_price_data
                })
                ax = plt.gca()
                df.plot(kind='line', y='real_price', ax=ax)
                df.plot(kind='line', y='predicted_price', color='red', ax=ax)
                plt.show()
                self.model.save(cost=gd.cost1,filename=filename)
                if not not_finished:
                    exit(0)

        # self.train(data=data)

    def update_model_from_gradient_dic(self,gradient_dic: dict,gradient_descent: GradientDescent.GradientDescent):
        candidate_model_update = copy.deepcopy(self.model)
        #update our network based on the gradients recieved by the gradient descent class
        Logger.Log('Learning-rate: '+str(self.learning_rate))
        for key in gradient_dic.keys():
            #biases must be treated differently
            gradient_treshold = 0.00001
            if abs(gradient_dic[key])>gradient_treshold:
                if key[2]!='bias':
                    layer,neuron,weight = key
                    if gradient_dic[key]>0:
                        candidate_model_update.layers[layer].neurons[neuron].weights[weight]  += -1*self.learning_rate
                    else:
                        candidate_model_update.layers[layer].neurons[neuron].weights[weight] += 1*self.learning_rate
                else:
                    layer,neuron,_ = key
                    if gradient_dic[key]>0:
                        candidate_model_update.layers[layer].neurons[neuron].bias += -1*self.learning_rate
                    else:
                        candidate_model_update.layers[layer].neurons[neuron].bias += self.learning_rate
            else:
                Logger.Log('gradient treshold reached')
        #check if updated model performs better then the current one
        cost2 = gradient_descent.cost(candidate_model_update)
        cost1 = gradient_descent.cost1
        print(cost1,cost2)
        if cost2<=cost1:
            self.model = copy.deepcopy(candidate_model_update)
            del candidate_model_update
            Logger.Log('Update of vars was needed')
            return True
        else:
            Logger.Log('training complete')
            return False


    def prediction_run(self):
        result = []
        for i in range(len(self.data) - self.model_interval - 1):
            result.append(float(self.model.predict(inputs=self.data[i:i + self.model_interval])))
        return result
class PredictionResult(Data.Candle):
    def __init__(self,id,data):
        super().__init__(id=id,data=data)