#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'

import time
import pricemanage,ordermanage
import common

'''研究市场的深度及价格趋势'''

class MarketResearch(object):
    #对市场进行研究，初始化市场名称
    def __init__(self,market):
        self.__market=market
        #交易市场，用来执行查询及提交订单的处理
        self.__order_market=ordermanage.OrderManage(market)
        #市场研究的coin list
        self.__coin_list=['ltc','doge','btc']

    def test_get_market_depth(self):
        self.__get_market_depth('doge')
    #得到某个COIN的市场深度价格列表
    def __get_market_depth(self,coin_code):
        market_depth=self.__order_market.getMarketDepth(coin_code+'_cny')
        price_date=market_depth.date
        sell_list=market_depth.sell
        buy_list=market_depth.buy

        pass

    #得到市场一段时间内的价格趋势
    def __get_price_trend(self,coin_code):
        pass


if __name__=='__main__':
    market_depth=MarketResearch('btc38')
    market_depth.test_get_market_depth()
