#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__='Owen_Study/owen_study@126.com'

'''自动检查市场行情并进行交易'''

import logging;logging.basicConfig(level=logging.INFO,filename='translog.log')
import time,os,traceback
import ordermanage
import pricemanage,sharedmarketcoin

class TradeRobot(object):
    '''自动侦测并进行交易，如果有指定盈利比例则按指定的标准进行，否则自动计算'''
    def __init__(self,std_profit_rate=0.009):
        #监测市场列表，目前只支持下面2个市场，如需要增加市场，需要增加对应的市场交易接口
        self.__market_list=['bter','btc38']
        #监控的coin列表，由于交易需要对应的coin做为基础，如果需要对相应的币种进行监控并交易，需要准备一些币种作为种子
        #不能交易coin列表，因为两个市场没有同时存在
        #xlm,ardr
        #可以使用的列表
        #'xrp','ltc','doge','xpm','nxt','bts','ppc','dash'
        #可工作列表  'doge','xrp','ltc'
        self.__coin_list=['xrp','ltc','doge','xpm','nxt','bts','ppc','dash']
        #盈利操作的起点
        self.__std_profit_rate=std_profit_rate
        #coin在市场之间传送的费用，有的是免费的，有的是收费的,需要地看各个市场的情况进行初始化
        self.__transfer_charge_rate={'ltc':0.01,'doge':0,'xpm':0,'ppc':0}
        #每次投资的金额标准
        self.__std_amount=100
        pass

    '''开始检测交易'''
    def start(self):
        processnum = 1
        while (1==1):

            try:
                self.price_analyze()
                time.sleep(0.1)
                if processnum % 10 == 0:
                    print('已经处理了:%d次' % processnum)
            except Exception as e:
                exstr = traceback.format_exc()
                print(exstr)
                print('%d 次process error!' % processnum)
            finally:
                processnum = processnum + 1
        pass

    '''开始检测交易'''
    def start_rearch(self):
        processnum = 0
        while (1==1):
            processnum = processnum + 1
            try:
                self.__coin_rearch()
                #time.sleep(0.5)
                if processnum % 10 == 0:
                    print('已经研究了:%d次' % processnum)
            except Exception as e:
                exstr = traceback.format_exc()
                print(exstr)
                print('%d 次process error!' % processnum)
        pass


    '''检测价格'''
    '''多市场同时交易,交易之前已经检查过余额'''
    def __trans_apply(self):
        buy_cny=self.__price_base.sell_cny
        sell_cny=self.__price_vs.buy_cny
        trans_units=round(self.__std_amount/buy_cny,2)
        #bterorder.submitOrder(coincode+'_cny','buy',buyprice,transunit)
        trans_base=self.__order_base.submitOrder(self.__trans_coin_code+'_cny','buy',buy_cny,trans_units)
        orderid=trans_base.order_id
        transflag=False
        trans_succ_flag=False
        #等OPEN交易的最长秒数
        max_wait_seconds = 5
        if orderid:
            #检查order_id是不是成交TODO
            orderstatus=self.__order_base.getOrderStatus(orderid,self.__trans_coin_code)
            if orderstatus=='closed':
                transflag=True
            #没有成交的订单则等预定的秒数，超时还没有成交刚取消
            else:
                waitseconds=0
                transflag=False
                while (waitseconds<max_wait_seconds):
                    time.sleep(1)
                    orderstatus = self.__order_base.getOrderStatus(orderid,self.__trans_coin_code)
                    if orderstatus=='closed':
                        waitseconds=max_wait_seconds+5    #退出
                        transflag=True
                    else:  #没有成效刚继续等待检查
                        waitseconds=waitseconds+1
                    #超过时间后则取消该订单，任务取消
                    if waitseconds==max_wait_seconds:
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
                    while (waitseconds < max_wait_seconds):
                        #每1秒检查 一次
                        time.sleep(1)
                        orderstatus = self.__order_base.getOrderStatus(orderid, self.__trans_coin_code)
                        if orderstatus == 'closed':
                            waitseconds = max_wait_seconds+5  # 退出
                            trans_succ_flag = True
                        else:  # 没有成效刚继续等待检查
                            waitseconds = waitseconds + 1
                        # 超过时间后则取消该订单，任务取消
                        if waitseconds == max_wait_seconds:
                            #取消原订单
                            self.__order_base.cancelOrder(orderid)
                            #按市场当前价卖出
                            newtrans_vs = self.__order_vs.submitOrder(self.__trans_coin_code + '_cny', 'sell', sell_cny*0.8,\
                                                                   trans_units)
                            logging.info('江湖有危险，打8折去卖的，成交价就听天由命了，参考下面的明细！')
                            neworder_id=newtrans_vs.order_id
                            neworderstatus = self.__order_base.getOrderStatus(neworder_id, self.__trans_coin_code)
                            if neworderstatus=='closed':
                                trans_succ_flag = True
                            else:
                                #8折的报价还没有卖出，则取消
                                self.__order_base.cancelOrder(neworder_id)
                                trans_succ_flag=False
                                logging.info('我努力了%f秒钟打8折都没有卖出去，说明市场在狂跌，买的:%s那%f份就存手里面等着以后发了再说，散了吧......'\
                                             %(max_wait_seconds,self.__trans_coin_code,self.__std_amount))

                pass
            pass
        return trans_succ_flag



    '''检查帐户余额是不是满足交易'''
    def __check_account(self):
        try:
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
        except Exception as e:
            print(str(e))
            return False
        finally:
            pass


    '''市场价格分析，只分析结果不进行处理，显示分析结果供后面交易时参考'''
    def __coin_rearch(self):
        # 比较多个市场之间的价格
        for market_base in self.__market_list:
            market_vs_list = list(self.__market_list)
            # 移除作为base 的市场
            market_vs_list.remove(market_base)
            # 对比每一个其它的市场
            for market_vs in market_vs_list:
                # 对每个coin进行分析
                for coin in self.__coin_list:
                    # base的市场价格
                    price_base = pricemanage.PriceManage(market_base, coin).get_coin_price()
                    # 需要对比的市场价格
                    price_vs = pricemanage.PriceManage(market_vs, coin).get_coin_price()

                    price_check_result = self.__price_check(coin,price_base, price_vs)
                    # 如果价格可以进行买卖刚返回
                    if price_check_result:
                        # 对于达到要求的保存到类变量中，交易函数进行处理
                        self.__market_base = market_base
                        self.__market_vs = market_vs
                        self.__price_base = price_base
                        self.__price_vs = price_vs
                        # 满足交易的coin code
                        self.__trans_coin_code = coin
                        # 把交易实例保存起来
                        # Base account的交易实例
                        self.__order_base = ordermanage.OrderManage(self.__market_base)
                        # VS市场
                        self.__order_vs = ordermanage.OrderManage(self.__market_vs)

                        # 预期盈利金额
                        profitamt = (self.__std_amount / price_vs.buy_cny) * (price_vs.buy_cny - price_base.sell_cny)
                        currtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        print('Date:%s,Coin:%s,BaseMarket(Buy):%s, VSmarket(Sell):%s,Buy price:%f,Sell price:%f,投资%f预期盈利:%f' \
                              % (currtime,coin, market_base, market_vs, price_base.sell_cny, price_vs.buy_cny, self.__std_amount,
                                 profitamt))

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

                    price_check_result=self.__price_check(coin,price_base,price_vs)
                    #如果价格可以进行买卖刚返回
                    if price_check_result :
                        #对于达到要求的保存到类变量中，交易函数进行处理
                        self.__market_base=market_base
                        self.__market_vs=market_vs
                        self.__price_base=price_base
                        self.__price_vs=price_vs
                        # 满足交易的coin code
                        self.__trans_coin_code=coin
                        #把交易实例保存起来
                        # Base account的交易实例
                        self.__order_base = ordermanage.OrderManage(self.__market_base)
                        # VS市场
                        self.__order_vs = ordermanage.OrderManage(self.__market_vs)

                        #预期盈利金额
                        profitamt=(self.__std_amount/price_base.sell_cny)*(price_vs.buy_cny-price_base.sell_cny)

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
    def __price_check(self,coin_code,base_price, vs_price):
        #买入价格是当前市场上最低的卖方价格
        buy_price=base_price.sell_cny
        #卖出价格是当前市场上的最高买入价格
        sell_price=vs_price.buy_cny
        #价格盈利百分比
        profitrate=(sell_price-buy_price)/buy_price
        #调整费率需要从标准盈利率中考虑加进来
        transfer_charge_rate=self.__transfer_charge_rate.get(coin_code,0)
        #价格差异大于盈利标准则返回True
        if profitrate>=self.__std_profit_rate+transfer_charge_rate:
            return True
        else:
            return False

    '''检测两个市场可共用的coin列表'''
    def check_shared_coin_list(self,coinlist):
        #比较多个市场之间的价格
        sharedcoinlist = []
        for market_base in self.__market_list:
            market_vs_list=list(self.__market_list)
            #移除作为base 的市场
            market_vs_list.remove(market_base)
            #对比每一个其它的市场
            for market_vs in market_vs_list:
                #对每个coin进行分析
                for coin in coinlist:
                    try:
                        #base的市场价格
                        price_base=pricemanage.PriceManage(market_base,coin).get_coin_price()
                        #需要对比的市场价格
                        price_vs=pricemanage.PriceManage(market_vs,coin).get_coin_price()
                        x=price_base.buy_cny
                        if x:
                            sharedcoin = sharedmarketcoin.SharedMarketCoin(market_base, market_vs, coin)
                            sharedcoinlist.append(sharedcoin)
                            print(str(sharedcoin))
                    except Exception as e:
                        pass
                        #print(str(e))
        coinlist = {}
        for x1 in sharedcoinlist:
            coinlist[x1.coin_code_base] = x1.coin_code_base
        for coin in coinlist:
            print(coin)
        return coinlist

    pass

#test
if __name__=='__main__':
    #price_base = pricemanage.PriceManage('bter', 'doge').get_coin_price()
    robot=TradeRobot()
    robot.start()
    #robot.start_rearch()
    #coinlist=['ltc','doge','xrp','bts','xlm','nxt','ardr','blk','xem','emc','dash','xzc','sys','vash','eac','xcn','ppc','mgc','hlb','zcc','xpm','ncs','ybc','anc','bost','mec','wdc','qrk','dgc','bec','ric','src','tag']
    #coinlist = ['ltc','xrm']
    #x=robot.check_shared_coin_list(coinlist)
    #sharedcoinlist={}
    #for x1 in x:
    #    sharedcoinlist[x1.coin_code_base]=x1.coin_code_base
    #for coin in sharedcoinlist:
    #    print(coin)