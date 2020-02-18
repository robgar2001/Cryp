from binance.client import Client
import Order
import Wallet
import Logger
import Strategy
import time
import sys
import AI.Model as Model
import Run
import datetime
import numpy as np
class main(object):
    def __init__(self):
        Logger.Log('Starting trading bot')
        Logger.Log('Retrieving client connection to binance api')
        attempt = 1
        while(True):
            try:
                Logger.Log('Establishing connection, attempt %i'%(attempt))
                client = Client(api_key='',api_secret='')
                break
            except:
                Logger.Log('Binance api connection attempt %i failed'%(attempt))
                attempt+=1
                time.sleep(1)
        Logger.Log('Connection succesfull')
        """
        train 2:[pair] 3:[structuur or filename or none]
        create [filename] [structuur]
        run [pair] [filename]
        simulate [pair] [filename]
        predict [pair] [filename]
        """
        #de userinterface wordt gecheckt
        if sys.argv[1] == 'train':
            strategy = Strategy.Strategy(symbol=sys.argv[2],binance_client=client,filename=sys.argv[3])
        elif sys.argv[1] == 'create':
            config = [int(sys.argv[i]) for i in range(3,len(sys.argv))]
            model = Model.Model()
            Logger.Log("Creating network with model config as first layer:"+str(config[0]))
            model.network_config = config
            model.create_structure()
            model.assign_start_weights()
            model.save(filename=sys.argv[2])
        elif sys.argv[1] == 'run':
            pass
        elif sys.argv[1] == 'simulate':
            pass
        elif sys.argv[1] == 'predict':
            pair = sys.argv[2]
            model_filename = sys.argv[3]
            model = Model.Model()
            model.load(filename=model_filename)
            #correctional of 2 is needed
            from_dt = datetime.datetime.now() - datetime.timedelta(minutes=(model.network_config[0]+3)*30)
            Logger.Log(str(from_dt)+" till "+str(datetime.datetime.now()))
            data = np.array(client.get_historical_klines(pair,interval=Client.KLINE_INTERVAL_30MINUTE,start_str=from_dt.ctime()))[:,1].astype(float)
            data = [data[i]-data[i-1] for i in range(1,len(data))]
            Logger.Log("Model input size: "+str(model.network_config[0])+" / data size: "+str(data.shape[0]))
            print(data.astype(float))
            Logger.Log(model.predict(inputs=data.astype(float)))
        else:
            print('Action not specified')


#start the program
start = main()
