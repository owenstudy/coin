#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''价格获取'''
__author__='Owen_Study/owen_study@126.com'

import urlaccess

'''价格管理类'''
class PriceManage(object):
    #传入市场名称和coin则获取对应的价格信息
    def __init__(self,market,coincode):
        self.__market=market
        self.__coincode=coincode
    '''返回价格明细'''
    def get_coin_price(self):
        pass

    '''返回bter市场的价格'''
    def __get_bter_price(self):
        base_url = 'http://data.bter.com/api/1/ticker/'
        url_cny = base_url + self.__coincode + '_cny'
        url_btc = base_url + self.__coincode + '_btc'
        # 获取价格的JSONObject数据
        pricedata_cny = urlaccess.geturldata(url_cny)
        # cny价格的信息
        sell_cny = float(pricedata_cny.sell)
        buy_cny = float(pricedata_cny.buy)
        last_cny = float(pricedata_cny.last)
        self.coin_price=CoinPrice(self.__coincode,buy_cny,sell_cny)
    '''返回btc38市场的价格'''


class CoinPrice(object):
    '''定义初始化价格属性'''
    def __init__(self,coin_code,buy_cny,sell_cny,**kwargs):
        self.coin_code=coin_code
        self.buy_cny=buy_cny
        self.sell_cny=sell_cny
        self.last_cny=kwargs.get('last_cny',None)
        self.buy_btc=kwargs.get('buy_btc',None)
        self.sell_btc = kwargs.get('sell_btc', None)
        self.last_btc = kwargs.get('last_btc', None)
        #print('coin:%s,buy_cny:%f,sell_cny:%f' % (self.coin_code, self.buy_cny, self.sell_cny))

    def __str__(self):
        print('coin:%s,buy_cny:%f,sell_cny:%f'%(self.coin_code,self.buy_cny,self.sell_cny))

#test
if __name__=='__main__':
    pricemanage=PriceManage('bter','doge')
    pricemanage.__get_bter_price()

    coinprice=CoinPrice(coin_code='doge',buy_cny=222,sell_cny=3333,buy_btc=2323)
    print('code:%s,buy_cny:%f,buy_btc%f'%(coinprice.coin_code,coinprice.buy_cny,coinprice.buy_btc))
