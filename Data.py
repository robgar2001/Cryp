from binance.client import Client
import sys
import numpy as np
import Logger

class DataManager(object):
    """
    The datamanager class is used as a container to store the incomming kline data and normalize it.
    """
    def __init__(self,client : Client,symbol : str,klineinterval,start_date,end_date):
        Logger.Log('Creating DataManager')
        self.client = client
        self.candles = []
        data = get_binance_data(binance_client=client,symbol=symbol,klineinterval=klineinterval,start_date=start_date,end_date=end_date)
        raw_data = data[:,4]
        self.raw_data = raw_data
        Logger.Log('Stored price data of %i klines '%(len(raw_data)))
        for i in range(1,len(raw_data)):
            #normalizing the date
            self+=(float(raw_data[i])/float(raw_data[i-1])-1,data[i])
    def __add__(self, other):
        candle = Candle(data=other[0],id=len(self.candles))
        indicator_data = other[1]
        #add other candle data to the candle
        """
                1499040000000,      // Open time
                "0.01634790",       // Open
                "0.80000000",       // High
                "0.01575800",       // Low
                "0.01577100",       // Close
                "148976.11427815",  // Volume
                1499644799999,      // Close time
                "2434.19055334",    // Quote asset volume
                308,                // Number of trades
                "1756.87402397",    // Taker buy base asset volume
                "28.46694368",      // Taker buy quote asset volume
                "17928899.62484339" // Ignore
                """
        indicator_key_list = [None,'open','high','low',None,'volume',None,'quote_asset_volume','number_of_trades','taker_buy_base_asset_volume','taker_buy_quote_asset_volume',None]
        for i in range(1,len(indicator_data)):
            if indicator_key_list[i]!=None:
                candle.indicators[indicator_key_list[i]] = indicator_data[i]
        print(candle.indicators)
        self.candles.append(candle)
        return self
    def get_data(self):
        return sorted(self.candles,key=lambda x: self.candles[self.candles.index(x)].id)

    def reconstruct_raw_data(self,price_change_list:list):
        #reconstruct from price change list an actual price list
        raw_data = []
        for i in range(len(price_change_list)):
            raw_data.append(float(self.raw_data[i])*(float(price_change_list[i])+1))
        return raw_data


def get_binance_data(binance_client,symbol,klineinterval,start_date,end_date):
    Logger.Log('Getting data from binance servers')
    try:
        return np.array(binance_client.get_historical_klines(symbol, klineinterval, start_date,end_date))
    except:
        Logger.Log('FATAL ERROR: could not get klines from binance server')

class Candle(object):
    def __init__(self,data,id = None):
        self.id = id
        self.data = data
        #indicators are non price data related and belong with the candle but are not real price data
        #data must be added in other way to input layer
        self.indicators = {}

    def __str__(self):
        return "Candle id: %i, price: %f"%(self.id,self.data)
    def __float__(self):
        return float(self.data)
    def __abs__(self):
        return abs(self.__float__())
    def __get_indicators__(self):
        return self.indicators
