from binance.client import Client
import sys
import numpy as np
import Logger

class DataManager(object):
    """
    The datamanager class is used as a container to store the incomming kline data and normalize it.
    """
    def __init__(self,client : Client,symbol : str,klineinterval):
        Logger.Log('Creating DataManager')
        self.client = client
        self.candles = []
        raw_data = get_binance_data(binance_client=client,symbol=symbol,klineinterval=klineinterval)
        self.raw_data = raw_data
        Logger.Log('Stored price data of %i klines '%(len(raw_data)))
        for i in range(1,len(raw_data)):
            self+=float(raw_data[i])/float(raw_data[i-1])-1
    def __add__(self, other):
        candle = Candle(data=other,id=len(self.candles))
        self.candles.append(candle)
        return self
    def get_data(self):
        return sorted(self.candles,key=lambda x: self.candles[self.candles.index(x)].id)
    def reconstruct_raw_data(self,price_change_list:list):
        raw_data = []
        for i in range(len(price_change_list)):
            raw_data.append(float(self.raw_data[i])*(float(price_change_list[i])+1))
        return raw_data


def get_binance_data(binance_client,symbol,klineinterval):
    Logger.Log('Getting data from binance servers')
    try:
        return np.array(binance_client.get_historical_klines(symbol, klineinterval, '28 Januari, 2020', '31 Januari, 2020'))[:,1]
    except:
        Logger.Log('FATAL ERROR: could not get klines from binance server')

class Candle(object):
    def __init__(self,data,id = None):
        self.id = id
        self.data = data
    def __str__(self):
        return "Candle id: %i, price: %f"%(self.id,self.data)
    def __float__(self):
        return float(self.data)
    def __abs__(self):
        return abs(self.__float__())
