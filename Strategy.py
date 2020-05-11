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
        gd = GradientDescent.GradientDescent(model=self.model,interval_size=self.model_interval,data=data)
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



class PredictionResult(Data.Candle):
    def __init__(self,id,data):
        super().__init__(id=id,data=data)