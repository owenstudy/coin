from bterapi import common
from bterapi import keyhandler

from bterapi.trade import TradeAPI,OrderItem

#定义调用的客户端类，KEY和secrect在内部处理完成
class Client:
    def __init__(self, access_key=None, secret_key=None, account_id=None):
        keyinfo = keyhandler.KeyHandler('apikey')
        self.tradeapi = TradeAPI(keyinfo.keys[0], keyinfo)

    #提交定单，只需要传入参数就直接执行
    #('doge_cny','sell',0.03,1000)
    def submitOrder(self,pair, trade_type, rate, amount, connection=None, update_delay=None, error_handler=None):
        #下订单
        neworder=self.tradeapi.placeOrder(pair,trade_type,rate,amount)
        print(neworder)
        return neworder
    #得到某个COIN或者全部的余额信息
    #pair e.g. doge_cny
    def getMyBalance(self,coin=None):
        bal = self.tradeapi.getFunds()
        #coin, curr = pair.split("_")
        #print(bal[coin]['available'])
        if coin:
            coinbal=bal[coin]['available']
        else:
            coinbal=bal
        return coinbal

    #得到某个order的状态
    def getOrderStatus(self,orderid):
        return self.tradeapi.getOrderStatus(orderid)
    #取消定单
    def cancelOrder(self,orderid):
        return self.tradeapi.cancelOrder(orderid)

if __name__=='__main__':
    bterclient=Client()
    #获取帐户余额
    bal=bterclient.getMyBalance('cny')
    #print(bal)

