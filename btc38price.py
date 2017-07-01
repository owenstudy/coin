#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import urlaccess

#BTC38的价格传入CODE得到常用的价格
#http://api.btc38.com/v1/ticker.php?c=btc&mk_type=cny
class CoinPrice:
    # 初始化coin ，并获取对应的数据  coincode=>ltc, btc
    def __init__(self, coincode):
        self.__coincode = coincode
        # http://api.btc38.com/v1/ticker.php?c=btc&mk_type=cny
        base_url = 'http://api.btc38.com/v1/ticker.php?c='
        url_cny = base_url + coincode + '&mk_type_cny'
        url_btc = base_url + coincode + '&mk_type_btc'
        self.__url_cny = url_cny
        self.__url_btc = url_btc
        # 获取价格的JSONObject数据
        pricedata_cny = urlaccess.geturldata(url_cny)
        # cny价格的信息
        #{"ticker":{"high":19855,"low":19429,"last":19818.9,"vol":1778.949921,"buy":19703.2,"sell":19818.9}}
        self.sell_cny = pricedata_cny.ticker.sell
        self.buy_cny = pricedata_cny.ticker.buy
        self.last_cny = pricedata_cny.ticker.last
        self.avg_cny = None
        #time.sleep(1)
        if coincode != 'btc':
            # btc price
            #pricedata_btc = urlaccess.geturldata(url_btc)
            self.sell_btc = None
            self.buy_btc = None
            self.last_btc = None
            self.avg_btc = None


#get帐户余额
def accountbal():
    pass

#getcoin balance
def coinbal(coincode):
    pass
#买入操作,按RMB金额买入
def buycoin(amt):
    pass

#卖出操作，按数量卖出
def sellcoin(unit):
    pass



#test
if __name__=='__main__':
    coincode='ltc'
    coinprice = CoinPrice(coincode)
    print('CNY:%f' % (coinprice.sell_cny))

