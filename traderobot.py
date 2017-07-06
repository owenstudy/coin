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
    def __init__(self,std_profit_rate=0.008):
        #监测市场列表，目前只支持下面2个市场，如需要增加市场，需要增加对应的市场交易接口
        self.__market_list=['bter','btc38']
        #监控的coin列表，由于交易需要对应的coin做为基础，如果需要对相应的币种进行监控并交易，需要准备一些币种作为种子
        #不能交易coin列表，因为两个市场没有同时存在
        #xlm,ardr
        #可以使用的列表
        #'xrp','ltc','doge','xpm','nxt','bts','ppc','dash'
        #可工作列表  'doge','xrp','ltc'
        self.__coin_list=['doge','ltc','ppc','xrp']
        #盈利操作的起点
        self.__std_profit_rate=std_profit_rate
        #原始的盈利水平，因为仓位会调整标准 的盈利比例
        self.__std_profit_rate_bk=std_profit_rate
        #coin在市场之间传送的费用，有的是免费的，有的是收费的,需要地看各个市场的情况进行初始化
        self.__transfer_charge_rate={'ltc':0.002,'doge':0,'xpm':0.002,'ppc':0.001}
        #每次投资的金额标准
        self.__std_amount=10
        #rounding num，根据币种得到交易单位的小数位
        #ltc的小数位只能<=3
        self.__rounding_num={'ltc':3, 'doge':2,'ppc':4}
        self.__price_rounding_num={'ltc':2, 'doge':4,'ppc':2}

        #价格检查次数
        self.__check_price_num=0
        pass

    '''开始检测交易'''
    def start(self):
        processnum = 1
        while (1==1):
            try:
                self.price_analyze()
            except Exception as e:
                exstr = traceback.format_exc()
                print(exstr)
                print(str(e))
                print('%d 次process error!' % processnum)
            finally:
                time.sleep(0.1)
                currtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                if processnum % 10 == 0:
                    print('%s: 已经处理了:%d次' % (currtime,processnum))
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

    '''获取射程的rounding 位数，默认为2位'''
    def get_rounding_num(self,coin_code,priceflag=None):
        if priceflag:
            #价格的rounding规则
            return self.__price_rounding_num.get(coin_code,3)
        else:
            #trans unit的rounding rule
            return self.__rounding_num.get(coin_code,2)

    '''test twin_trans'''
    def test_twin_trans(self):
        # VS市场
        #测试卖出操作
        test_market = 'bter'
        self.__order_vs = ordermanage.OrderManage(test_market)
        self.__order_base = ordermanage.OrderManage(test_market)
        status_bter=False
        status_bter = self.twin_trans(self.__order_base,'buy', 'doge', 100, 0.05)
        print('test trans(SELL) exec result @%s:' % test_market)
        if status_bter:
            print('transaction done successfully!')
        else:
            print('transaction failed!')
        test_market = 'btc38'
        """
        self.__order_vs = ordermanage.OrderManage(test_market)
        status_btc38 = self.twin_trans(self.__order_vs,'sell', 'doge', 1000, 0.05)
        print('test trans(SELL) exec result @%s:' % test_market)
        if status_btc38:
            print('transaction done successfully!')
        else:
            print('transaction failed!')
        """
        #测试买入操作
        test_market='bter'
        self.__order_base = ordermanage.OrderManage(test_market)
        status_bter=self.twin_trans(self.__order_base,'buy','doge',200,0.012)
        print('test trans(BUY) exec result @%s:'%test_market)
        if status_bter:
            print('transaction done successfully!')
        else:
            print('transaction failed!')
        test_market = 'btc38'
        self.__order_base = ordermanage.OrderManage(test_market)
        status_btc38=self.twin_trans(self.__order_base,'buy','doge',200,0.012)
        print('test trans(BUY) exec result @%s:'%test_market)
        if status_btc38:
            print('transaction done successfully!')
        else:
            print('transaction failed!')

    def test_twin_trans_sell_overtime(self):

        self.__order_base = ordermanage.OrderManage('bter')
        order_market = self.__order_base
        sell_order=order_market.submitOrder('doge_cny','sell',0.03,150)
        sell_order_id=sell_order.order_id
        resell_status=self.__twin_trans_sell_overtime_process(order_market,sell_order_id,'doge',0.01735,100)
        pass
    '''卖出超时处理,重卖处理完成为非0,表示重卖降价次数'''
    def __twin_trans_sell_overtime_process(self,order_market,order_id,coin_code,origin_sell_price,trans_units):
        try:
            #通过不断循环来降低价格去促进成交,每次下降0.002个百分点
            down_rate_step=0.002
            # 对新订单进行跟踪处理直到完成
            resell_times=0
            # 每次卖单的等候时间
            max_waiting_seconds=5
            new_order_status=None
            cancel_fail_times=0
            while ( new_order_status!='closed' and cancel_fail_times<10 ):
                waiting_seconds = 0
                #每个订单循环检查X秒
                while(waiting_seconds<max_waiting_seconds and new_order_status!=None):
                    new_order_status = order_market.getOrderStatus(new_order_id, coin_code)
                    time.sleep(1)
                    waiting_seconds=waiting_seconds+1
                    if new_order_status=='closed':
                        waiting_seconds=max_waiting_seconds+1
                #降价没有卖出去，继续取消降价
                if new_order_status!='closed':
                    resell_times=resell_times+1
                    if new_order_status==None:
                        new_order_id=order_id
                    # 取消上一次的订单,第一次为传进来的订单号
                    previous_order=order_market.cancelOrder(new_order_id,coin_code)
                    if previous_order=='success':
                        #每次降低down_rate_step（0.002)
                        new_sell_price=round(float(origin_sell_price*(1-down_rate_step*resell_times)),self.get_rounding_num(coin_code,'price'))
                        new_order=order_market.submitOrder(coin_code+'_cny','sell',new_sell_price,trans_units)
                        new_order_id=new_order.order_id
                        #新提交订单的状态
                        new_order_status=order_market.getOrderStatus(new_order_id,coin_code)
                    elif previous_order=='trans_done':
                        new_order_status='closed'
                        # 取消过程中发生的成交，并没有降价成交
                        resell_times=resell_times-1
                        print('在降价取消的过程，订单已经成交或已取消！')
                    else:
                        print('订单降价过程中取消失败!')
                        cancel_fail_times=cancel_fail_times+1
                pass
            pass
        except Exception as e:
            print(str(e))
            return 0
        if new_order_status=='closed':
            return resell_times
        else:
            return 0
        pass

    '''twin trans, sell or buy in different market'''
    """
    @:parameter trans_type, sell, buy
    @:parameter coin_code, trans coin code
    @:parameter trans_price, trans price
    """
    def twin_trans(self,order_market,trans_type,coin_code,trans_units,trans_price):
        # 默认交易是失败的，只有在满足特定的条件才算成功
        trans_succ_flag=False
        #max waitting seconds
        max_wait_seconds=8
        #Check trans type, sell or buy
        """
        if trans_type=='buy':
            order_market=self.__order_base
        elif trans_type=='sell':
            order_market=self.__order_vs
        else:
            trans_succ_flag= False
            raise('Unknow trans_type:%s'%trans_type)
        """
        trans_order=order_market.submitOrder(coin_code+'_cny',trans_type,trans_price,trans_units)
        order_id=trans_order.order_id
        #让服务器运行一会
        time.sleep(0.1)
        order_status=order_market.getOrderStatus(order_id,coin_code)
        if order_status=='closed':
            trans_succ_flag=True
        else:
            #todo循环处理，直到成功
            waitseconds = 0
            while (waitseconds < max_wait_seconds):
                #每1秒检查 一次
                time.sleep(1)
                order_status = order_market.getOrderStatus(order_id, coin_code)
                if order_status == 'closed':
                    waitseconds = max_wait_seconds+5  # 退出
                    trans_succ_flag = True
                else:  # 没有成效刚继续等待检查
                    waitseconds = waitseconds + 1
            # 超过时间后则取消该订单，任务取消
            if waitseconds == max_wait_seconds:
                #先测试 只有买不成交时才取消，卖出不进行取消，直到等到交易结束
                if trans_type=='buy':
                    cancelorder = order_market.cancelOrder(order_id, coin_code)
                    # 如果取消失败需要处理，这时订单可能已经成交，导致显示的提示不正确
                    if cancelorder=='success':
                        print('买入超时取消!')
                        trans_succ_flag=False
                    # order finished when cancel
                    elif cancelorder=='trans_done':
                        trans_succ_flag = True
                    else:
                        #可能出现在取消的时候订单成交的情况，只能取消成功的订单才算取消，默认是成交了
                        trans_succ_flag = True
                else:
                    print('卖出超时，等待降价卖出......')
                    # 卖出超时取消卖单
                    resell_times=self.__twin_trans_sell_overtime_process(order_market,order_id,coin_code,trans_price,trans_units)
                    if resell_times>0:
                        print('降价%d次后成功卖出'%resell_times)
                        trans_succ_flag=True
                    else:
                        print('降价卖出时错误，请人工检查卖出情况!')
                        trans_succ_flag = False
        return trans_succ_flag

    def test_trans_apply(self):
        self.__market_base='bter'
        self.__market_vs='btc38'
        self.__trans_coin_code='doge'
        price_base = pricemanage.PriceManage('bter', 'doge').get_coin_price()
        # 需要对比的市场价格
        price_vs = pricemanage.PriceManage('btc38', 'doge').get_coin_price()
        self.__price_base = price_base
        self.__price_vs = price_vs
        self.__price_base.sell_cny=0.03
        self.__price_vs.buy_cny=0.04

        trans_success=self.__trans_apply()
        if trans_success:
            print('交易成功！')
        else:
            print('交易处理失败!')

    #改进的交易函数处理
    def __trans_apply(self):
        trans_success=False
        buy_cny=self.__price_base.sell_cny
        sell_cny=self.__price_vs.buy_cny
        rounding_num=self.get_rounding_num(self.__trans_coin_code)
        trans_units=round(self.__std_amount/buy_cny,rounding_num)
        self.__order_base = ordermanage.OrderManage(self.__market_base)
        self.__order_vs = ordermanage.OrderManage(self.__market_vs)
        # 调用买入操作
        buy_success=self.twin_trans(self.__order_base,'buy',self.__trans_coin_code,trans_units,buy_cny)
        if buy_success:
            sell_success=self.twin_trans(self.__order_vs,'sell',self.__trans_coin_code,trans_units,sell_cny)
            #目前的方案只要买入成功，则卖出订单不取消，只是检查状态当时有没有成交
            self.__trans_log()
            if sell_success:
                trans_success=True
            # 检查帐户的仓位并调整相应的盈利比例,使得下一次交易按新的盈利比例处理
            self.__update_profit_rate((self.__order_vs))
        return trans_success

    '''test check_account'''
    def test_check_account(self):
        self.__order_base = ordermanage.OrderManage('bter')
        self.__order_vs=ordermanage.OrderManage('btc38')
        self.__trans_coin_code='ppc'

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
                        profitamt = (self.__std_amount / price_base.sell_cny) * (price_vs.buy_cny - price_base.sell_cny)
                        currtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        print('Date:%s,Coin:%s,BaseMarket(Buy):%s, VSmarket(Sell):%s,Buy price:%f,Sell price:%f,投资%f预期盈利:%f' \
                              % (currtime,coin, market_base, market_vs, price_base.sell_cny, price_vs.buy_cny, self.__std_amount,
                                 profitamt))
    '''根据当前的仓位自动调整盈利比例'''
    def __update_profit_rate(self,order_vs):
        money_bal=order_vs.getMyBalance('cny')
        money_pool_size=self.__std_amount*100
        #当仓位比较 低时自动增加盈利比例，降低资金的消耗速度
        money_rate=money_bal/money_pool_size
        if money_rate<0.4:
            self.__std_profit_rate=self.__std_profit_rate*1.2
        elif money_rate<0.3:
            self.__std_profit_rate = self.__std_profit_rate * 1.3
        elif money_rate < 0.2:
            self.__std_profit_rate = self.__std_profit_rate * 1.4
        else:
            self.__std_profit_rate = self.__std_profit_rate_bk

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
                    #print('%s:is requesting price@%s' % (self.__get_curr_time(),market_base))
                    price_base=pricemanage.PriceManage(market_base,coin).get_coin_price()
                    #需要对比的市场价格
                    #print('%s:is requesting price@%s' % (self.__get_curr_time(),market_vs))
                    price_vs=pricemanage.PriceManage(market_vs,coin).get_coin_price()
                   # print('%s:is comparing price'%self.__get_curr_time())
                    price_check_result=self.__price_check(coin,price_base,price_vs)

                    self.__check_price_num=self.__check_price_num+1
                    if self.__check_price_num % 10 == 0:
                        print('%s: 已经检查了%d次的价格' % (self.__get_curr_time(), self.__check_price_num))

                    # TODO for testing
                    #price_check_result=True
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

                        print('%s: Coin:%s,BaseMarket(Buy):%s, VSmarket(Sell):%s,Buy price:%f,Sell price:%f,投资%f预期盈利:%f'\
                              %(self.__get_curr_time(),coin,market_base,market_vs,price_base.sell_cny,price_vs.buy_cny,self.__std_amount,profitamt))
                        #开始处理交易
                        # 检查帐户的仓位并调整相应的盈利比例
                        #print('%s: is checking account balance'%self.__get_curr_time())
                        account_balance=self.__check_account()
                        if account_balance:
                            #检查帐户的仓位并调整相应的盈利比例
                            #print('%s: is doing transaction.'%self.__get_curr_time())
                            trans_status=self.__trans_apply()
                            if trans_status:
                                print('交易成功!')
                            else:
                                print('交易失败/或卖出当时未成功！')
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
        rounding_num=self.get_rounding_num(self.__trans_coin_code)
        trans_units=float(round(self.__std_amount/buy_cny,rounding_num))
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
        #价格非空时才进行检查
        if  base_price!=None and vs_price!=None:
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


    def __get_curr_time(self):
        currtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return currtime

#test
if __name__=='__main__':
    #price_base = pricemanage.PriceManage('bter', 'doge').get_coin_price()
    robot=TradeRobot(0.009)
    robot.start()
    #robot.test_twin_trans_sell_overtime()
    #twin trans test
    #robot.test_twin_trans()

    #robot.test_twin_trans()
    #robot.price_analyze()
    #robot.start_rearch()
    #coinlist=['ltc','doge','xrp','bts','xlm','nxt','ardr','blk','xem','emc','dash','xzc','sys','vash','eac','xcn','ppc','mgc','hlb','zcc','xpm','ncs','ybc','anc','bost','mec','wdc','qrk','dgc','bec','ric','src','tag']
    #coinlist = ['ltc','xrm']
    #x=robot.check_shared_coin_list(coinlist)
    #sharedcoinlist={}
    #for x1 in x:
    #    sharedcoinlist[x1.coin_code_base]=x1.coin_code_base
    #for coin in sharedcoinlist:
    #    print(coin)