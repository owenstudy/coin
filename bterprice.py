#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json,time
import urlaccess
import hashlib


# COIN的价格类，传入CODE得到常用的价格
class CoinPrice:
    # 初始化coin ，并获取对应的数据  coincode=>ltc, btc
    def __init__(self, coincode):
        self.__coincode = coincode
        # URL: http://data.bter.com/api/1/ticker/[CURR_A]_[CURR_B]
        #{"result":"true","last":19949.98,"high":20000.01,"low":19500,"avg":19789.28,"sell":19948.8,"buy":19775.78,"vol_btc":152.8845,"vol_cny":3025473.61,"rate_change_percentage":"1.42"}
        base_url = 'http://data.bter.com/api/1/ticker/'
        url_cny = base_url + coincode + '_cny'
        url_btc = base_url + coincode + '_btc'
        self.__url_cny = url_cny
        self.__url_btc = url_btc
        # 获取价格的JSONObject数据
        pricedata_cny = urlaccess.geturldata(url_cny)
        # cny价格的信息
        self.sell_cny = float(pricedata_cny.sell)
        self.buy_cny = float(pricedata_cny.buy)
        self.last_cny = float(pricedata_cny.last)
        self.avg_cny = float(pricedata_cny.avg)
        time.sleep(1)
        if coincode != 'btc':
            # btc price
            pricedata_btc = urlaccess.geturldata(url_btc)
            self.sell_btc = float(pricedata_btc.sell)
            self.buy_btc = float(pricedata_btc.buy)
            self.last_btc = float(pricedata_btc.last)
            self.avg_btc = float(pricedata_btc.avg)


#比较coin的BTC价格和CNY价格的差异
def findcoindiff(coincode):
    btcprice=CoinPrice('btc')
    #当前币种的价格
    coinprice=CoinPrice(coincode)
    #RMB基准金额
    standardamt=1000
    #人民币买入，以BTC价格卖出，再卖出BTC的价格差异
    buy_coin_units=standardamt/coinprice.sell_cny
    buy_btc_units=buy_coin_units*coinprice.buy_btc
    buy_cny_amt=buy_btc_units*btcprice.buy_cny
    #周转后的金额差异，为正说明是收入金额，为负说明是赔付金额，目前还没有 考虑手续费
    diffamt_cny1=buy_cny_amt-standardamt
    print('方法1：%d'%diffamt_cny1)

    # BTC价格买入，以CNY价格卖出，再买入BTC的价格差异
    #以btc为基础进行相反操作，操作的基础单位在这个变量说明
    standardbtc=1000/btcprice.buy_cny
    buy_coin_units=standardbtc/coinprice.sell_btc
    buy_cny_amt=buy_coin_units*coinprice.buy_cny
    buy_btc_units=buy_cny_amt/btcprice.buy_cny
    diffamt_cny2=(buy_btc_units-standardbtc)*btcprice.buy_cny
    print('方法2：%d'%diffamt_cny2)
    if diffamt_cny1>diffamt_cny2:
        print('方法1: Good!')
        return diffamt_cny1
    else:
        print('方法2: Good!')
        return diffamt_cny2


#取得SHA512加密字符
def getSHA512(secret):
    h=hashlib.sha512()
    h.update(secret)
    return h.digest()
#test
if __name__=='__main__':
    secret=getSHA512('ab'.encode('utf8'))
    print(secret)
    #print('ltc diff: %d'%findcoindiff('ltc'))

    #"""
    coincode='btc'
    coinprice = CoinPrice(coincode)
    if coincode=='btc':
        print('CNY:%f' % (coinprice.sell_cny))
    else:
        print('CNY:%f,BTC:%f'%(coinprice.sell_cny,coinprice.sell_btc))
    #"""