#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''自动检查市场行情并进行交易'''
__author__='Owen_Study/owen_study@126.com'

import urlaccess
import json,time
import openorderlist
import btceapi.keyhandler as keyhandler
from btceapi import  TradeAPI


'''统一接口'''
#test api transaction
key='47ae44f72c3a93dd33e6177142189071'
secret='f68d9ca86eb175d93d4f992642197b1c7ba555b0e9bb747d989f91ccc3cdeed1'

#定义调用的客户端类，KEY和secrect在内部处理完成
class Client:
    def __init__(self, access_key=None, secret_key=None, account_id=None):
        keyinfo = keyhandler.KeyHandler('apikey')
        self.tradeapi = TradeAPI(keyinfo.keys[0], keyinfo)
    #得到某个COIN或者全部的余额信息
    #pair e.g. doge_cny
    def getMyBalance(self,coin=None):
        try:
            bal = self.tradeapi.getFunds()
            #coin, curr = pair.split("_")
            #print(bal[coin]['available'])
            coinbal = None
            if coin:
                try:
                    coinbal=bal[coin]['available']
                except:
                    coinbal=None

            else:
                coinbal=bal
        except Exception as e:
            print(str(e))
            print('获取BTER余额异常！')
            pass
        return coinbal
    #得到open order list
    def getOpenOrderList(self,coin_code_pair):
        order_list=self.tradeapi.activeOrders(coin_code_pair)
        open_order_list=[]
        for order in order_list:
            open_order_item = openorderlist.OpenOrderItem(order.order_id,'btce',coin_code_pair,order.type,\
                                                          float(order.rate),float(order.initial_amount),order.date)
            open_order_list.append(open_order_item)
        return open_order_list
        pass