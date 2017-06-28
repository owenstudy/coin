#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__='Owen_Study/owen_study@126.com'

'''解决两个市场的资金池平衡'''
"""
思路：A，B两个市场如果出现币和现金不均衡的情况，出现不能买出或者进出，刚两个市场进行同步操作以平衡
如：A中货币RMB不足时，通过卖出指定的币种（如DOGE）来产生RMB，同时在市场B同等价格买入DOGE，这样实现A中的现金增加，同时B
中的COIN增加，两者之间的差异就是交易费率
这个交易需要完全完成才行进行下一次的操作，原则上是小额交易，确保两次交易都在短时间内完成，如果没有完成则继续等等直至完成
"""

class ExchAccountBal(object):
    '''对指定的市场和帐户进行平衡'''
    def __init__(self,market_list, coin_list):
        pass

    '''开始平衡处理'''
    def start(self):
        pass

    '''对指定的市场和coin进行平衡处理，返回True/False'''
    def exch_balance(self,market_base, market_vs, coin_code):
        pass

    '''单个交易处理，返回订单id和status'''
    def single_trans(self,market_base,trans_type,coin_code,trans_units,trans_price,curr_type='cny'):
        pass

    '''检查资金池的状态，确定是不是需要均衡，返回True/False'''
    def check_balance_flag(self,market_base, market_vs,coin_code):
        pass

    '''检查同时操作的完成情况，返回True/False'''
    def check_twin_trans(self,order_id_base, order_id_vs):
        pass


