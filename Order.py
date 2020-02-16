from binance.client import Client
import Logger
class Buy(object):
    def __init__(self,price = None,BinanceClient = None,DigitalWallet = None):
        self.BinanceClient = BinanceClient
        #als prijs none, dan market order
        self.price = price
        self.DigitalWallet = DigitalWallet
        self.OrderHistory = []
    def placeBuyOrder(self,quantity = 0,market_type = None,price = None):
        """"
            Place a buy order in the order object.
            If the binance_client is set in the Order, it will be a real order.
            Otherwise the order is only digitally simulated.
        """
        if market_type:
            Logger.Log('Placing buy order: ' + self.coinName + '/' + str(quantity))
            if self.BinanceClient:
                order = self.BinanceClient.create_test_order(
                    symbol=self.DigitalWallet.symbol,
                    side=Client.SIDE_BUY,
                    type=market_type,
                    quantity=quantity)
                self.OrderHistory.append(order)
                Logger.Log(order)
                Logger.Log('Real order placed successfull, bought %f %s '%(quantity,self.coinName))
        else:
            Logger.Log('Placing virtual buy order')
            self.DigitalWallet




