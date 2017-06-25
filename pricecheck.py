#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''检查两个市场之间的价格差异'''

import bterprice
import btc38price
import time
import ordermanage

#成功运行次数
succnum=0

"""
@buymarket   --btc38, bter
@coincode    --e.g. doge, ltc...
@coinamt      --buy coin number
@buyprice    --buy price for this coin
@sellprice   --sell price for this coin
"""
# 对不同的市场进行同时操作，要确保同一个买和卖同时成功才进行下一次的操作
def buysell(buymarket,coincode,coinamt,buyprice,sellprice):
    #交易成功与否的标志，只有同时操作成功才算成功
    transflag=False
    if buymarket=='bter':
        order=ordermanage.OrderManage('bter')
    elif buymarket=='btc38':
        order=ordermanage.OrderManage('btc38')

    buyorder = order.submitOrder(coincode + '_cny', 'buy', buyprice, coinamt)
    orderid=buyorder.order_id
    if orderid:
        #检查order_id是不是成交TODO
        x=order.getOrderStatus(orderid)
        orderstatus=order.getOrderStatus(orderid).status
        if orderstatus=='closed':
            transflag=True
        #没有成交的订单则等20S，超时还没有成交刚取消
        else:
            waitseconds=0
            while (waitseconds<=20):
                time.sleep(1)
                orderstatus = order.getOrderStatus(orderid).status
                if orderstatus=='closed':
                    waitseconds=100    #退出
                    transflag=True
                else:  #没有成效刚继续等待检查
                    waitseconds=waitseconds+1
                #超过时间后则取消该订单，任务取消
                if waitseconds==20:
                    order.cancelOrder(orderid)
        pass


    buyorder = bterorder.submitOrder(coincode + '_cny', 'buy', buyprice, transunit)
    # neworder=btc38Client.submitOrder(2,'cny',0.03,1000,'doge')
    sellorder = btc38order.submitOrder(coincode + '_cny', 'sell', sellprice, transunit)


#比较coin的BTC价格和CNY价格的差异
def findcoindiff(coincode):
    global succnum
    btcprice=bterprice.CoinPrice('btc')
    #当前币种的价格
    coinprice_mark1=bterprice.CoinPrice(coincode)
    coinprice_mark2=btc38price.CoinPrice(coincode)
    #RMB基准金额
    standardamt=200
    #赚钱比例
    standardrate=0.03
    bterorder=ordermanage.OrderManage('bter')
    btc38order=ordermanage.OrderManage('btc38')

    #buyprice = coinprice_mark1.sell_cny
    #sellprice = coinprice_mark2.buy_cny
    #transunit = standardamt / coinprice_mark1.sell_cny

    #earnmoney = coinprice_mark2.buy_cny * (standardamt / coinprice_mark1.sell_cny) - standardamt
    #sellorder = btc38order.submitOrder(coincode + '_cny', 'sell', sellprice, transunit)
    #人民币买入，市场1买入，市场2卖出
    if coinprice_mark1.sell_cny<coinprice_mark2.buy_cny:
        buyprice =coinprice_mark1.sell_cny
        sellprice=coinprice_mark2.buy_cny
        transunit=round(standardamt/coinprice_mark1.sell_cny,2)

        earnmoney=coinprice_mark2.buy_cny*(standardamt/coinprice_mark1.sell_cny)-standardamt
        if earnmoney/standardamt>=standardrate:

            print('可以操作%s：mark1-BTER买入@:%f,mark2-BTC38卖出@:%f'%(coincode,coinprice_mark1.sell_cny,coinprice_mark2.buy_cny))
            print('每%f操作可以赚取：%f'%(standardamt,earnmoney))
            #买入mark1-bter, 卖出mark2-btc38
            buybal=bterorder.getMyBalance('cny')
            sellbal=btc38order.getMyBalance(coincode)
            if buybal>standardamt and sellbal>transunit:
                buyorder=bterorder.submitOrder(coincode+'_cny','buy',buyprice,transunit)
                #neworder=btc38Client.submitOrder(2,'cny',0.03,1000,'doge')
                sellorder=btc38order.submitOrder(coincode+'_cny','sell',sellprice,transunit)
                succnum=succnum+1
                print('Buy  order status@%s:%s'%(bterorder.market,buyorder))
                print('Sell order status@%s:%s'%(btc38order.market,sellorder))
            else:
                print('余额不足!')
    elif coinprice_mark2.sell_cny<coinprice_mark1.buy_cny:
        buyprice =coinprice_mark2.sell_cny
        sellprice=coinprice_mark1.buy_cny
        transunit=round(standardamt/coinprice_mark2.sell_cny,2)
        earnmoney = coinprice_mark1.buy_cny * (standardamt / coinprice_mark2.sell_cny) - standardamt
        if earnmoney/standardamt>=standardrate:
            print('可以操作%s：mark2-BTC38买入@:%f,mark1-BTER卖出@:%f' % (coincode,coinprice_mark2.sell_cny, coinprice_mark1.buy_cny))
            print('每%f操作可以赚取：%f' % (standardamt, earnmoney))
            #买入mark2-btc38, 卖出mark1-bter
            buybal=btc38order.getMyBalance('cny')
            sellbal=bterorder.getMyBalance(coincode)
            if buybal>standardamt and sellbal>transunit:
                buyorder=btc38order.submitOrder(coincode + '_cny', 'buy', buyprice, transunit)
                sellorder=bterorder.submitOrder(coincode + '_cny', 'sell', sellprice, transunit)
                succnum = succnum + 1
                print('Buy  order status@%s:%s' % (btc38order.market, buyorder))
                print('Sell order status@%s:%s' % (bterorder.market, sellorder))


# test
if __name__ == '__main__':

    #coinprice_mark1=bterprice.CoinPrice('xrp')
    #coinprice_mark2=btc38price.CoinPrice('xrp')
    #print('mark1%s,%s'%(coinprice_mark1.buy_cny,coinprice_mark1.sell_cny))
    #print('mark2%s,%s'%(coinprice_mark2.buy_cny,coinprice_mark2.sell_cny))
    buysell('btc38','doge',100,0.01,0.03)
    #循环处理，每15秒做一次检查
    global succnum
    processnum=0
    #coinlist=['xrp']
    coinlist=['doge']
    while (succnum<=1):
        for coin in coinlist:
            try:
                findcoindiff(coin)
                time.sleep(1)
            except:
                pass
                print('%s process error!'%coin)
        processnum=processnum+1
        if processnum%10==0:
            print('已经处理了:%d次'%processnum)
        time.sleep(10)