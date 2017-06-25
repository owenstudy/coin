#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''自动检查市场行情并进行交易'''
__author__='Owen_Study/owen_study@126.com'

import logging;logging.basicConfig(level=logging.INFO)
import ordermanage

class TradeRobot:
    '''自动侦测并进行交易，如果有指定盈利比例则按指定的标准进行，否则自动计算'''
    def __init__(self,std_rate=0.02):
        #监测市场列表，目前只支持下面2个市场，如需要增加市场，需要增加对应的市场交易接口
        self.__market_list=['bter','btc38']
        #监控的coin列表，由于交易需要对应的coin做为基础，如果需要对相应的币种进行监控并交易，需要准备一些币种作为种子
        self.__coin_list=['doge']

        pass

    '''开始检测交易'''
    def start(self):
        pass
    '''多市场同时交易'''
    def trans_apply(self,buymarket,coincode,coinamt,buyprice,sellprice):
        pass
    '''市场价格分析'''
    #返回分析结果，哪个市场买入，哪个市场卖出
    def __price_analyze(self):
        pass
    '''把交易过程写入日志'''
    def __log(self):
        pass


