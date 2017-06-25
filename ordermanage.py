
import time
import btc38.btc38client
import bterapi.bterclient

'''统一订单的管理到一个文件中'''

class OrderManage:
    #market, 支持这两个参数 bter, btc38
    def __init__(self,market):
        self.market=market
        #初始化两个市场的接口模块
        if market=='bter':
            self.clientapi=bterapi.bterclient.Client()
        elif market=='btc38':
            self.clientapi=btc38.btc38client.Client()
    #提交定单，只需要传入参数就直接执行
    #('doge_cny','sell',0.03,1000)
    def submitOrder(self,pair, trade_type, rate, amount, connection=None, update_delay=None, error_handler=None):
        return self.clientapi.submitOrder(pair,trade_type,rate,round(amount,2))
    #得到某个COIN或者全部的余额信息
    #pair e.g. doge_cny
    def getMyBalance(self,coin=None):
        return self.clientapi.getMyBalance(coin)
    #取消定单
    def cancelOrder(self,orderid):
        return self.clientapi.cancelOrder(orderid)
    #订单状态
    def getOrderStatus(self,orderid,coin_code=None):
        #time.sleep(1)
        return self.clientapi.getOrderStatus(orderid,coin_code)

#test
if __name__=='__main__':
    bterorder=OrderManage('btc38')
    order=bterorder.submitOrder('doge_cny','sell',0.04,100)
    orderstatus=bterorder.getOrderStatus(order.order_id,'doge')
    print(orderstatus)
    bal=bterorder.getMyBalance('doge')
    print('BTER:%f'%bal)

    btc38order=OrderManage('btc38')
    bal=btc38order.getMyBalance('doge')
    print('BTC38:%f'%bal)



