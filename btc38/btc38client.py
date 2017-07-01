
import btc38.client
import urlaccess
import json,time
import openorderlist

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
        #return format b'[succ|123423]
        order2=order[0].decode('utf8').split('|')
        #避免直接成交没有 返回订单的情况
        #orderstatus = order2[0]
        if order2[0]=='succ':
            orderstatus='success'
        else:
            orderstatus='fail'
        if len(order2)>=2:
            orderid=order2[1]
        else:
            if orderstatus=='success':
                #虚拟一个订单号,直接成功的订单，没有 返回定单号则给一个虚拟的订单号
                orderid = 1111111
            else:
                orderid = -1111111

        neworder={'order_id':orderid,'status':orderstatus}
        #转换成对象以方便 统一访问
        neworder2=urlaccess.JSONObject(neworder)
        return neworder2
    #得到某个COIN或者全部的余额信息
    #pair e.g. doge_cny
    def getMyBalance(self,coin=None):
        try:
            bal=self.btc38clt.getMyBalance()
            if coin:
                coinbal=float(bal[coin+'_balance'])
            else:
                coinbal=bal
            #print(bal)
            pass
        except Exception as e:
            print(str(e))
            print('检查IP地址是不是加入了白名单！')
        return coinbal
    #取消定单,btc38传送时需要 放一个coin code否则为报错
    def cancelOrder(self,orderid,coin_code=None):
        try:
            order_status=None
            cancel=self.btc38clt.cancelOrder(coin_code,'cny',orderid)
            cancelstatus=cancel[0].decode('utf8')
            if cancelstatus=='succ':
                order_status='success'
            else:
                order_status = 'fail'
        except Exception as e:
            print(str(e))
            print('订单取消失败@btc38')
            order_status='fail'
        finally:
            return order_status

    # 得到open order list
    def getOpenOrderList(self, coin_code_pair):
        coin_code=coin_code_pair.split('_')[0]
        order_list = self.btc38clt.getOrderList(coin_code)
        open_order_list = []
        for order in order_list:
            if order.get('type')=='1':
                trans_type='buy'
            else:
                trans_type='sell'
            open_order_item = openorderlist.OpenOrderItem(order.get('id'), 'btc38', coin_code_pair, trans_type, \
                                                          float(order.get('price')), float(order.get('amount')), order.get('time'))
            open_order_list.append(open_order_item)
        return open_order_list
        pass

    #取得订单状态
    def getOrderStatus(self,orderid,coin_code=None):
        #
        try:
            time.sleep(1)
            data=self.btc38clt.getOrderList(coin_code)
            #orderstatus=b'[{"order_id":"123", "order_type":"1", "order_coinname":"BTC", "order_amount":"23.232323", "order_price":"0.2929"}, {"order_id":"123", "order_type":"1", "order_coinname":"LTC","order_amount":"23.232323", "order_price":"0.2929"}]'
            #TODO 需要找出指定订单的状态
            orderresult=None
            order_status=None
            for order in data:
                #查找到有订单则说明没有 成交，是open状态，其它为closed，cancel也认为是closed
                if int(order.get('id'))==int(orderid):
                    orderresult={'order_id':orderid,'order_status':'open'}
                    break
            if not orderresult:
                orderresult = {'order_id': orderid, 'order_status': 'closed'}
            orderresultobj=urlaccess.JSONObject(orderresult)
            order_status=orderresultobj.order_status
        except Exception as e:
            #如果订单状态返回出错，则返回一个默认值
            print('获取订单状态出错')
            print(str(e))
            order_status='open'
        finally:
            return order_status

if __name__=='__main__':
    client = Client()
    #submit=client.submitOrder('doge_cny','sell',0.03,100)
    #print(submit.order_id)
    #clt = client.getOrderStatus(367892140)
    #print(clt)
    """
        #test open order list
        open_order_list=client.getOpenOrderList('doge_cny')
        for order in open_order_list:
            print('order_id:%s,trans_type:%s,trans_unit:%f'%(order.order_id,order.trans_type,float(order.trans_unit)))
    """


    btc38clt=Client()
    """
    bal=btc38clt.getMyBalance('doge')
    print(bal)
    neworder=btc38clt.submitOrder('doge_cny','sell',0.03,2000)
    print(neworder)
    bal=btc38clt.getMyBalance('doge')
    print(bal)
    cancel=btc38clt.cancelOrder(367711369)
    print(cancel)
"""
    bal=btc38clt.getMyBalance('doge')
    print(bal)

