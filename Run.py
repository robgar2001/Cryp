import AI.Model
import sys
from binance.client import Client
import datetime
import numpy as np
import threading
import Logger
class Run(object):
    def __init__(self,client, model_path='network.model',wallet = None):
        self.model_path = model_path
        self.client = client
        self.model = AI.Model.Model()
        self.structure,_ = self.model.load(filename=model_path)
        self.wallet = wallet
    def update(self):
        Logger.Log('Update called')
        price,data = self.next_prediction()
        Logger.Log('Next price is predicted to be: '+str(price))
        if self.wallet.BaseCoin1bal>0 and price>0:
            self.wallet.Buy(quantity=self.wallet.BaseCoin1bal,price=data[-1])
        if self.wallet.coin2bal>0 and price<0:
            self.wallet.Sell(quantity=self.wallet.coin2bal,price=data[-1])
        self.wallet.Profit()
        return True
    def start_digital_run(self):
        while True:
            t = threading.Timer(30*60, self.update)
            t.start()
            t.join()
    def get_data(self):
        d = datetime.datetime.now()-datetime.timedelta(minutes=(self.structuur[0]+3)*30)
        return np.array(self.client.get_historical_klines('BNBUSDT',Client.KLINE_INTERVAL_30MINUTE,d.ctime(),datetime.datetime.now().ctime()))[:,1]
    def next_prediction(self):
        data = self.get_data()
        data = data.astype(float)
        networkdata = np.zeros(len(data)-1)
        for i in range(1,len(data)):
            networkdata[i-1] = (data[i]/data[i-1]-1)
        price = self.model.predict(inputs=networkdata)[0]
        return float(price),data