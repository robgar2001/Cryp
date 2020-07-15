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

import argparse

class main(object):
    def __init__(self):
        Logger.Log('Starting trading bot')
        self.client = None
        #parsen van argumenten
        parser = argparse.ArgumentParser()
        parser.add_argument('task')
        parser.add_argument('-filename',type=str)

        traingroup = parser.add_argument_group('train')
        traingroup.add_argument('-trade_symbol')
        traingroup.add_argument('-learning_rate')
        traingroup.add_argument('-start_date')
        traingroup.add_argument('-end_date')

        creategroup = parser.add_argument_group('create_file')
        creategroup.add_argument('-structure',help='neural network structure for example: 32/9/1')
        creategroup.add_argument('-indicators',type=str)


        predictgroup = parser.add_argument_group('predict')



        args = parser.parse_args()
        print(args)


        #de userinterface wordt gecheckt
        if args.task == 'train':
            self.client = self.connect_to_binance_api()
            learning_rate = 0.001
            if args.learning_rate:
                learning_rate=float(args.learning_rate)
            strategy = Strategy.Strategy(symbol=args.trade_symbol,binance_client=self.client,filename=args.filename,learning_rate=learning_rate,start_date=args.start_date,end_date=args.end_date)
        elif args.task == 'create_file':
            #from 4th index we have the config of the network
            config = [int(i) for i in args.structure.split('/')]
            model = Model.Model()
            Logger.Log("Creating network with model config as first layer:"+str(config[0])+' amount of indicators:'+str(len(args.indicators)))
            config[0]*=len(args.indicators)
            model.network_config = config
            model.create_structure()
            model.assign_start_weights()
            #second argument is the filename
            model.save(filename=args.filename,indicators=args.indicators)
        elif args.task == 'run':
            pass
        elif args.task == 'simulate':
            pass
        elif args.task == 'predict':
            self.client = self.connect_to_binance_api()
            pair = sys.argv[2]
            model_filename = sys.argv[3]
            model = Model.Model()
            model.load(filename=model_filename)
            #correctional of 2 is needed
            from_dt = datetime.datetime.now() - datetime.timedelta(minutes=(model.network_config[0]+3)*30)
            Logger.Log(str(from_dt)+" till "+str(datetime.datetime.now()))
            data = np.array(self.client.get_historical_klines(pair,interval=Client.KLINE_INTERVAL_30MINUTE,start_str=from_dt.ctime()))[:,1].astype(float)
            datan = np.array([data[i]/data[i-1]-1 for i in range(1,len(data))])
            Logger.Log("Model input size: "+str(model.network_config[0])+" / data size: "+str(data.shape[0]))
            prediction = model.predict(inputs=datan.astype(float))[0]
            Logger.Log("Next candle change price predicted to be in percentage: "+str(prediction*100)+' or in base currency: '+str((prediction+1)*data[-1]))
        else:
            print('Action not specified')
    def connect_to_binance_api(self):
        Logger.Log('Retrieving client connection to binance api')
        attempt = 1
        while (True):
            try:
                Logger.Log('Establishing connection, attempt %i' % (attempt))
                client = Client(api_key='', api_secret='')
                break
            except:
                Logger.Log('Binance api connection attempt %i failed' % (attempt))
                attempt += 1
                time.sleep(1)
        Logger.Log('Connection succesfull')
        return client

#start the program
start = main()
