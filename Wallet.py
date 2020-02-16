import Logger
class DigitalWallet(object):
    def __init__(self,BaseCoin1bal=0,coin2bal=0,BaseCoin1Name = 'coin1',coin2Name = 'coin2',orderBook={},fee=0.0001):
        self.BaseCoin1bal = BaseCoin1bal
        self.coin2bal = coin2bal
        self.BaseCoin1Name = BaseCoin1Name
        self.coin2Name = coin2Name
        self.orderBook = orderBook
        self.fee = fee
        self.trades_made = 0
        self.symbol = coin2Name+BaseCoin1Name
        self.coin1start = BaseCoin1bal
        self.coin2start = coin2bal
        Logger.Log('Init DigitalWallet [%s:%f][%s:%f] %s/%s' % (self.coin2Name, self.coin2bal, self.BaseCoin1Name, self.BaseCoin1bal, self.coin2Name, self.BaseCoin1Name))
    def reset(self):
        self.trades_made = 0
        self.BaseCoin1bal = self.coin1start
        self.coin2bal = self.coin2start
        #Logger.Log('Wallet was reset')
    def __str__(self):
        return '[%s:%f][%s:%f] %s/%s'%(self.coin2Name,self.coin2bal,self.BaseCoin1Name,self.BaseCoin1bal,self.coin2Name,self.BaseCoin1Name)
    def Profit(self):
        final_balance_1 = self.BaseCoin1bal
        if self.coin2bal != 0:
            last_order_id = max(list(self.orderBook.keys()))
            price = self.orderBook[last_order_id][2]
            final_balance_1 += (self.coin2bal*float(price))
        Logger.Log('Current usdt worth balance: '+str(final_balance_1)+' / starting balance: '+str(self.coin1start))
        return (final_balance_1/self.coin1start)-1
    def Buy(self,quantity=None,price=None):
        if quantity and price:
            Logger.Log('Buying in wallet '+str(quantity)+' at '+str(price))
            self.BaseCoin1bal -= quantity
            self.coin2bal += (quantity/float(price))*(1-self.fee)
            self.orderBook[self.trades_made] = ('buy',quantity,price)
            self.trades_made+=1
    def Sell(self,quantity = None,price = None):
        if quantity and price:
            Logger.Log('Selling in wallet '+str(quantity)+' at '+str(price))
            self.coin2bal-=quantity
            self.BaseCoin1bal += (quantity*float(price))*(1-self.fee)
            self.orderBook[self.trades_made] = ('sell',quantity,price)
            self.trades_made+=1