#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__='Owen_Study/owen_study@126.com'

import logging;logging.basicConfig(level=logging.INFO,filename='find_bal_coin.log')
import json,time,common
import pricemanage,urlaccess
'''模块注释说明:查找可用来作为两个市场之间进行均衡交易的COIN，目前主要是找从BTER卖出，BTC38买入的COIN'''

class FindBalCoin(object):
    def __init__(self,market_list):
        self.__market_list=market_list
        # TODO 先手工加入，后面需要写个功能来自动获取可用的列表
        self.__coin_list=self.get_shared_coin_list()
        print(self.__coin_list)

    # 确认价格是不是合适作为balance coin
    def __match_balance(self,price_base, price_vs):
        # 卖出方市场的价格高于买入市场，则适合进行均衡price_vs的RMB，增加卖出市场的RMB
        if price_vs.buy_cny>price_base.sell_cny or abs(price_vs.buy_cny-price_base.sell_cny)/price_vs.buy_cny<0.003:
            return True
        else:
            return False

        pass

    # 获取bter所有的交易对
    def get_all_pairs_bter(self):
        base_url = 'http://data.bter.com/api/1/pairs'
        all_pairs = urlaccess.geturldata(base_url)
        all_coin_list=[]
        for pair in all_pairs:
            if pair.split('_')[1]!='cny':
                continue
            all_coin_list.append(pair.split('_')[0])

        # 返回bter唯一的code list
        return(list(set(all_coin_list)))

    # 获取btc38所有的交易对
    def get_all_pairs_btc38(self):
        base_url='http://api.btc38.com/v1/ticker.php?c=all&mk_type=cny'
        all_pairs = urlaccess.get_content(base_url).decode('utf-8')
        all_paris_list=json.loads(all_pairs)
        all_coin_list=all_paris_list.keys()

        # 返回bter唯一的code list
        return (list(set(all_coin_list)))
    # 获取两个市场COIN列表中共同的COIN
    def get_shared_coin_list(self):
        bter_coin_list=self.get_all_pairs_bter()
        btc38_coin_list=self.get_all_pairs_btc38()
        share_list=list(set(bter_coin_list).intersection(set(btc38_coin_list)))
        veri_share_list=[]
        # 验证是不是能取得价格
        for coin in share_list:
            veri_flag=True

            for market in self.__market_list:
                try:
                    price_base = pricemanage.PriceManage(market, coin).get_coin_price()

                except:
                    veri_flag=False
                    break
                    pass
            # 两个市场同时都能取得价格的才是真正的共享coin
            if veri_flag:
                veri_share_list.append(coin)
        return (veri_share_list)


    # 查找合适的COIN进行市场之间MONEY的平衡
    def find_bal_coin(self):
        #比较多个市场之间的价格
        for market_base in self.__market_list:
            market_vs_list=list(self.__market_list)
            #移除作为base 的市场
            market_vs_list.remove(market_base)
            #对比每一个其它的市场
            for market_vs in market_vs_list:
                #对每个coin进行分析
                for coin in self.__coin_list:
                    #base的市场价格
                    price_base=pricemanage.PriceManage(market_base,coin).get_coin_price()
                    #需要对比的市场价格
                    price_vs=pricemanage.PriceManage(market_vs,coin).get_coin_price()
                    match_bal_flag=self.__match_balance(price_base,price_vs)
                    if match_bal_flag :
                        # 专门找bter的
                        if market_vs=='bter':
                            logging.info('%s:Coin:%s 适合作为%s的均衡Coin，从%s卖出来得到Money，同时从%s买入!'%(common.CommonFunction.get_curr_time(),coin,market_vs,market_vs,market_base))
                            logging.info('买入价格:%f, 卖出价格:%f'%(price_base.sell_cny,price_vs.buy_cny))

if __name__=='__main__':
    market_list=['btc38','bter']
    find_bal=FindBalCoin(market_list)
    #shared_coin_list=find_bal.get_shared_coin_list()
    #print(shared_coin_list)
    while(True):
        try:
            find_bal.find_bal_coin()
            time.sleep(1)
        except:
            pass
    pass