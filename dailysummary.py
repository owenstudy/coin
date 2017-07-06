#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'

import ordermanage,common

'''模块注释说明: 每日资金总结'''

class DailySummary(object):
    def __init__(self,market_list):
        self.__market_list=market_list

    ''' 获取当前的余额'''
    def get_balance(self):
        for market in self.__market_list:
            order_market=ordermanage.OrderManage(market)
            market_bal=order_market.getMyBalance()

    '''输出余额到文件'''
    def output_summary(self,filename):
        file=open(filename,'a')
        #每个市场的明细
        file_detail=open(filename.split('.')[0]+'_detail.'+filename.split('.')[1],'a')
        all_market_bal={}
        all_coin_list=[]
        for market in self.__market_list:
            order_market=ordermanage.OrderManage(market)
            market_bal=order_market.getMyBalance()
            all_market_bal[market]=market_bal
            all_coin_list=all_coin_list+list(market_bal.keys())
        # 所有市场的COIN列表
        all_coin_list=list(set(all_coin_list))
        all_output={}
        all_coin_bal={}

        # 按币种循环生成各个市场的帐户的情况
        for coin in all_coin_list:
            all_coin_bal[coin]=[]
            for market in self.__market_list:
                if coin in all_market_bal[market].keys():
                    coin_bal=all_market_bal[market][coin]['available']
                    coin_bal_lock=all_market_bal[market][coin]['locked']
                    coin_total_bal = round(coin_bal + coin_bal_lock,4)
                    all_coin_bal[coin].append({'market':market,'available':coin_total_bal})
                else:
                    all_coin_bal[coin].append({'market':market,'available':0})
        # 按币种输出
        all_coin_list.sort()
        for coin in all_coin_list:
            need_output=False
            all_market_values=0
            coin_value=all_coin_bal[coin]
            for item in coin_value:
                if float(item['available'])>0:
                    need_output=True
                #市场之间的总和,针对同一币种
                all_market_values=round(all_market_values+item['available'],4)
                pass
            if need_output:
                coin_value = all_coin_bal[coin]
                for item in coin_value:
                    coin_bal=str(round(item['available'],4))
                    market=item['market']
                    all_output[market] = all_output.get(market, '') + '%s|%s|' % (coin.ljust(6), coin_bal.rjust(12))
                all_output['ALL'] = all_output.get('ALL', '') + '%s|%s|' % (coin.ljust(6), str(all_market_values).rjust(12))

        # 输出每个市场的余额
        currtime=common.CommonFunction.get_curr_time()
        for market in self.__market_list:
            output='%s|%s|%s|\n'%(currtime,market.ljust(6),all_output[market])
            file_detail.write(output)
        summary_output='%s|%s|%s|\n'%(currtime,'ALL'.ljust(6),all_output['ALL'])
        file.write(summary_output)
        file.close()
        file_detail.close()
if __name__ == '__main__':
    market_list=['bter','btc38']
    daily_summary=DailySummary(market_list)
    bal=daily_summary.output_summary('daily_summary.log',)
    pass