#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'

'''不同市场的共享coin，这个列表的才具有可操作性'''


class SharedMarketCoin(object):
    def __init__(self,market_base,market_vs,coin_code_base,coin_code_vs=None):
        self.market_base=market_base
        self.market_vs=market_vs
        self.coin_code_base=coin_code_base
        #默认是两个市场的代码是相同的
        if coin_code_vs==None:
            self.coin_code_vs=coin_code_base
        else:
            self.coin_code_vs=coin_code_vs
    def __str__(self):
        return 'BaseMarket:%s,VSMarket:%s,CoinNameBase:%s,CoinNameVS:%s'\
              %(self.market_base,self.market_vs,self.coin_code_base,self.coin_code_vs)
