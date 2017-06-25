#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''自动检查市场行情并进行交易'''
__author__='Owen_Study/owen_study@126.com'

import logging;logging.basicConfig(level=logging.INFO,filename='translog.log')
import time,os
import ordermanage
import pricemanage

class TradeRobot(object):
    '''自动侦测并进行交易，如果有指定盈利比例则按指定的标准进行，否则自动计算'''
    def __init__(self,std_profit_rate=0.025):
        #监测市场列表，目前只支持下面2个市场，如需要增加市场，需要增加对应的市场交易接口
        self.__market_list=['bter','btc38']
        #监控的coin列表，由于交易需要对应的coin做为基础，如果需要对相应的币种进行监控并交易，需要准备一些币种作为种子
        self.__coin_list=['doge','ltc']
        #盈利操作的起点
        self.__std_profit_rate=std_profit_rate
        #每次投资的金额标准
        self.__std_amount=100
        #Trans log
        self.__translog=TransLog()
        pass

    '''开始检测交易'''
    def start(self):
        processnum = 0
        while (1==1):
            processnum = processnum + 1
            try:
                self.price_analyze()
                #time.sleep(0.5)
                if processnum % 10 == 0:
                    print('已经处理了:%d次' % processnum)
            except Exception as e:
                print(str(e))
                print('%d 次process error!' % processnum)
        pass
    '''多市场同时交易,交易之前已经检查过余额'''
    def __trans_apply(self):
        buy_cny=self.__price_base.sell_cny
        sell_cny=self.__price_vs.buy_cny
        trans_units=round(self.__std_amount/buy_cny,2)
        #bterorder.submitOrder(coincode+'_cny','buy',buyprice,transunit)
        trans_base=self.__order_base.submitOrder(self.__trans_coin_code+'_cny','buy',buy_cny,trans_units)
        orderid=trans_base.order_id
        transflag=False
        if orderid:
            #检查order_id是不是成交TODO
            orderstatus=self.__order_base.getOrderStatus(orderid,self.__trans_coin_code)
            if orderstatus=='closed':
                transflag=True
            #没有成交的订单则等20S，超时还没有成交刚取消
            else:
                waitseconds=0
                while (waitseconds<=20):
                    time.sleep(1)
                    orderstatus = self.__order_base.getOrderStatus(orderid,self.__trans_coin_code)
                    if orderstatus=='closed':
                        waitseconds=100    #退出
                        transflag=True
                    else:  #没有成效刚继续等待检查
                        waitseconds=waitseconds+1
                    #超过时间后则取消该订单，任务取消
                    if waitseconds==20:
                        self.__order_base.cancelOrder(orderid)
            #只有买入成功后才进行卖出操作
            if transflag:
                trans_vs=self.__order_vs.submitOrder(self.__trans_coin_code+'_cny','sell',sell_cny,trans_units)
                sell_order_id=trans_vs.order_id
                sell_order_status=self.__order_vs.getOrderStatus(sell_order_id,self.__trans_coin_code)
                if sell_order_status=='closed':
                    trans_succ_flag=True
                else:
                    pass
                    #todo循环处理，直到成功
                    waitseconds = 0
                    while (waitseconds <= 20):
                        time.sleep(1)
                        orderstatus = self.__order_base.getOrderStatus(orderid, self.__trans_coin_code)
                        if orderstatus == 'closed':
                            waitseconds = 100  # 退出
                            trans_succ_flag = True
                        else:  # 没有成效刚继续等待检查
                            waitseconds = waitseconds + 1
                        # 超过时间后则取消该订单，任务取消
                        if waitseconds == 20:
                            self.__order_base.cancelOrder(orderid)
                            #按市场当前价卖出
                            newtrans_vs = self.__order_vs.submitOrder(self.__trans_coin_code + '_cny', 'sell', sell_cny*0.8,\
                                                                   trans_units)
                            neworder_id=newtrans_vs.order_id
                            neworderstatus = self.__order_base.getOrderStatus(neworder_id, self.__trans_coin_code)
                            if neworderstatus=='closed':
                                trans_succ_flag = True
                            else:
                                self.__order_base.cancelOrder(neworder_id)
                                trans_succ_flag=False

                pass
            pass
        return trans_succ_flag



    '''检查帐户余额是不是满足交易'''
    def __check_account(self):
        #Base余额，买入方余额为现金
        bal_base=self.__order_base.getMyBalance('cny')
        bal_vs=self.__order_vs.getMyBalance(self.__trans_coin_code)
        #预期交易数量
        trans_units=self.__std_amount/self.__price_vs.sell_cny

        #是不是满足交易条件
        if bal_base>self.__std_amount and bal_vs>trans_units:
            return True
        else:
            return False
        pass

    '''市场价格分析'''
    #返回分析结果，哪个市场买入，哪个市场卖出
    def price_analyze(self):
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

                    price_check_result=self.__price_check(price_base,price_vs)
                    #如果价格可以进行买卖刚返回
                    if price_check_result :
                        #对于达到要求的保存到类变量中，交易函数进行处理
                        self.__market_base=market_base
                        self.__market_vs=market_vs
                        self.__price_base=price_base
                        self.__price_vs=price_vs
                        #满足交易的coin code
                        self.__trans_coin_code=coin
                        #把交易实例保存起来
                        # Base account的交易实例
                        self.__order_base = ordermanage.OrderManage(self.__market_base)
                        # VS市场
                        self.__order_vs = ordermanage.OrderManage(self.__market_vs)

                        #预期盈利金额
                        profitamt=(self.__std_amount/price_vs.buy_cny)*(price_vs.buy_cny-price_base.sell_cny)

                        print('Coin:%s,BaseMarket(Buy):%s, VSmarket(Sell):%s,Buy price:%f,Sell price:%f,投资%f预期盈利:%f'\
                              %(coin,market_base,market_vs,price_base.sell_cny,price_vs.buy_cny,self.__std_amount,profitamt))
                        #开始处理交易
                        if self.__check_account():
                            trans_status=self.__trans_apply()
                            if trans_status:
                                print('交易成功!')
                                self.__trans_log()
                            else:
                                print('交易失败！')
                        else:
                            print('帐户余额不足！')


    #'''把交易过程写入日志'''
    def __trans_log(self):
        profitamt = (self.__std_amount / self.__price_vs.buy_cny) * (self.__price_vs.buy_cny - self.__price_base.sell_cny)
        #买入价格是当前市场上最低的卖方价格
        buy_price=self.__price_base.sell_cny
        #卖出价格是当前市场上的最高买入价格
        sell_price=self.__price_vs.buy_cny
        #价格盈利百分比
        profitrate=float((sell_price-buy_price)/buy_price)
        buy_cny=float(self.__price_base.sell_cny)
        sell_cny=float(self.__price_vs.buy_cny)
        trans_units=float(round(self.__std_amount/buy_cny,2))
        currtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        try:
            logging.info('%s|%s|%s|%s|%f|%f|%f|%f|%f|%f|'%(currtime,\
            self.__trans_coin_code,self.__market_base,self.__market_vs, \
            float(profitamt),float(profitrate),float(self.__std_amount),\
            float(self.__price_base.sell_cny),float(self.__price_vs.buy_cny),float(trans_units)))
        except:
            print('log写错误！')
            pass
        pass

    '''比例两个市场价格，确认是不是可以进行买卖操作,BASE市场是买入市场'''
    def __price_check(self,base_price, vs_price):
        #买入价格是当前市场上最低的卖方价格
        buy_price=base_price.sell_cny
        #卖出价格是当前市场上的最高买入价格
        sell_price=vs_price.buy_cny
        #价格盈利百分比
        profitrate=(sell_price-buy_price)/buy_price
        #价格差异大于盈利标准则返回True
        if profitrate>=self.__std_profit_rate:
            return True
        else:
            return False


    pass

#test
if __name__=='__main__':
    #price_base = pricemanage.PriceManage('bter', 'doge').get_coin_price()
    robot=TradeRobot()
    robot.start()
    #robot.testlog()
