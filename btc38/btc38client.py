
import btc38.client
import urlaccess
import json
import ast

'''统一接口'''
#test api transaction
key='47ae44f72c3a93dd33e6177142189071'
secret='f68d9ca86eb175d93d4f992642197b1c7ba555b0e9bb747d989f91ccc3cdeed1'
accountid=43237


class Client():
    def __init__(self):
        self.btc38clt = btc38.client.Client(key, secret, accountid)
        pass

    #提交定单，只需要传入参数就直接执行
    #('doge_cny','sell',0.03,1000)
    def submitOrder(self,pair, trade_type, rate, amount, connection=None, update_delay=None, error_handler=None):
        #btc38Client.submitOrder(2, 'cny', 0.03, 1000, 'doge')
        if trade_type=='sell':
            transtype=2
        else:
            transtype=1
        coin,curr=pair.split('_')
        order=self.btc38clt.submitOrder(transtype,curr,rate,round(amount,2),coin)
        order2=order[0].decode('utf8').split('|')
        orderstatus=order2[0]
        orderid=order2[1]
        neworder={'order_id':orderid,'status':orderstatus}
        #转换成对象以方便 统一访问
        neworder2=urlaccess.JSONObject(neworder)
        return neworder2
    #得到某个COIN或者全部的余额信息
    #pair e.g. doge_cny
    def getMyBalance(self,coin=None):
        bal=self.btc38clt.getMyBalance()
        if coin:
            coinbal=float(bal[coin+'_balance'])
        else:
            coinbal=bal
        #print(bal)
        pass
        return coinbal
    #取消定单
    def cancelOrder(self,orderid):
        cancel=self.btc38clt.cancelOrder('cny',orderid)
        return cancel
    #取得订单状态
    def getOrderStatus(self,orderid):
        #TODO, need test
        orderstatus=self.btc38clt.getOrderList()
        #orderstatus=b'[{"order_id":"123", "order_type":"1", "order_coinname":"BTC", "order_amount":"23.232323", "order_price":"0.2929"}, {"order_id":"123", "order_type":"1", "order_coinname":"LTC","order_amount":"23.232323", "order_price":"0.2929"}]'
        orderstatus2=orderstatus.decode('utf8')
        orderstatusobj=ast.literal_eval(orderstatus2)
        #TODO 需要找出指定订单的状态
        orderresult=None
        for order in orderstatusobj:

            #查找到有订单则说明没有 成交，是open状态，其它为closed，cancel也认为是closed
            if int(order['order_id'])==orderid:
                orderresult={'order_id':orderid,'order_status':'open'}
                break
        if not orderresult:
            orderresult = {'order_id': orderid, 'order_status': 'closed'}
        orderresultobj=urlaccess.JSONObject(orderresult)
        return orderresultobj

if __name__=='__main__':
    client = Client()
    clt = client.getOrderStatus(123)
    print(clt.order_status)

"""
    btc38clt=Client()
    bal=btc38clt.getMyBalance('doge')
    print(bal)
    neworder=btc38clt.submitOrder('doge_cny','sell',0.03,2000)
    print(neworder)
    bal=btc38clt.getMyBalance('doge')
    print(bal)
    cancel=btc38clt.cancelOrder(367711369)
    print(cancel)
    bal=btc38clt.getMyBalance('doge')
    print(bal)
"""

