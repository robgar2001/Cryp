from binance.client import Client
import Order
import Wallet
import Logger
import Strategy
import time
import sys
import AI.Model as Model
import Run
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
        """
        #de userinterface wordt gecheckt
        if sys.argv[1] == 'train':
            strategy = Strategy.Strategy(symbol=sys.argv[2],binance_client=client)
        elif sys.argv[1] == 'create':
            config = [int(sys.argv[i]) for i in range(3,len(sys.argv))]
            model = Model.Model()
            Logger.Log("Creating network with model config as first layer:"+str(config[0]))
            model.network_config = config
            model.save(filename=sys.argv[2])
        elif sys.argv[1] == 'run':
            pass
        elif sys.argv[1] == 'simulate':
            pass
        else:
            print('Action not specified')


#start the program
start = main()
