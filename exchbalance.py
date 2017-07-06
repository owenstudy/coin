#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__='Owen_Study/owen_study@126.com'

import logging;logging.basicConfig(level=logging.INFO,filename='exchange_balance.log')
import time
import pricemanage,ordermanage,traderobot

#TODO
'''解决两个市场的资金池平衡'''
"""
思路：A，B两个市场如果出现币和现金不均衡的情况，出现不能买出或者进出，用两个市场进行同步操作以平衡
如：A中货币RMB不足时，通过卖出指定的币种（如DOGE）来产生RMB，同时在市场B同等价格买入DOGE，这样实现A中的现金增加，同时B
中的COIN增加，两者之间的差异就是交易费率
这个交易需要完全完成才行进行下一次的操作，原则上是小额交易，确保两次交易都在短时间内完成，如果没有完成则继续等等直至完成
"""

class ExchAccountBal(object):
    '''对指定的市场和帐户进行平衡'''
    def __init__(self,market_list, coin_list,std_trans_amt):
        self.__market_list=market_list
        self.__coin_list=coin_list
        #交易市场
        self.__market_base=None
        self.__market_vs=None
        #交易处理
        self.__order_base=None
        self.__order_vs=None
        #每次交易的金额
        self.__std_amount=std_trans_amt

        #均衡交易的倍数
        self.__exch_times=2
        #最大open均衡的订单
        self.__max_open_num=20
        #自动均衡的POOL的大小，是每次交易的整数倍
        self.__money_pool_size=100
        #自动进行资金池均衡的coin
        self.__money_pool_coin=['ltc','doge']
        #均衡时两个市场价格的差异比例，如0.005
        self.__money_pool_price_rate_diff=0.003
        pass

    '''开始平衡处理'''
    def start(self):
        # 当前均衡的次数，即使是失败也计算在内
        bal_times = 0
        while(True):
            # 循环处理市场
            for market_base in self.__market_list:
                market_vs_list=list(self.__market_list)
                #移除作为base 的市场
                market_vs_list.remove(market_base)
                #对比每一个其它的市场
                for market_vs in market_vs_list:
                    #对每个coin进行分析
                    for coin in self.__coin_list:
                        #当前处理的市场
                        self.__market_base=market_base
                        self.__market_vs=market_vs
                        self.__order_base = ordermanage.OrderManage(self.__market_base)
                        self.__order_vs = ordermanage.OrderManage(self.__market_vs)
                        #开始处理帐户对倒,
                        if coin in self.__money_pool_coin:
                            #对资金池进行均衡
                            exch_status = self.single_balance_market(market_base, market_vs, coin,'Y')
                        else:
                            #对COIN进行均衡
                            exch_status = self.single_balance_market(market_base,market_vs,coin)
                        bal_times=bal_times+1
                        #time.sleep(10)
                        if bal_times%10==0:
                            print('%s: 执行了%d次均衡同步' % (self.__get_curr_time(), bal_times))

        pass

    '''得到市场价格的趋势，上升还是下降,返回True-上长'''
    def __price_rising_trend(self,coin_code):
        # TODO 先手工处理，需要 根据价格趋势进行判断
        return True

    '''指定交易价格'''
    def __get_trans_price(self,price_base, price_vs, coin_code):
        #只有在两个系统的交易价格相关比较小的时候才进行
        #卖出市场是缺现金的市场，买入的市场是变身把现金转移到卖出市场
        #price_base==>买入市场，有丰富的现金    price_vs==>卖出市场，缺现金市场
        diff_rate=round((price_vs.buy_cny-price_vs.sell_cny)/price_vs.buy_cny,3)
        #卖出市场的买入价大于买入市场的卖出钱则直接用卖出市场的价格
        #TODO 需要考虑当前市场的涨跌趋势，上涨市场以卖出价格优先，下跌市场以买入价格优先
        if price_vs.buy_cny>=price_base.sell_cny:
            trans_price=price_vs.buy_cny
        else:
            #只有两个市场的价格相差在0.5%之内才进行
            if abs(diff_rate)<self.__money_pool_price_rate_diff:
                if self.__price_rising_trend(coin_code):
                    #优先用买方市场的卖出价格，因为价格最近上涨趋势，先锁定买入
                    trans_price=price_base.sell_cny
                else:
                    trans_price=price_vs.buy_cny
            else:
                trans_price=None

        return trans_price

        pass
    #测试exch_balance
    def test_exch_balance(self):
        exch_status=False
        while(not exch_status):
            exch_status=self.exch_balance('btc38','bter','doge')
        if exch_status:
            print('执行成功！')
        else:
            print('执行失败!')

    '''比例两个市场价格，确认是不是可以进行买卖操作,BASE市场是买入市场'''

    def __price_check(self, coin_code, base_price, vs_price):
        # 价格非空时才进行检查
        if base_price != None and vs_price != None:
            # 买入价格是当前市场上最低的卖方价格
            buy_price = base_price.sell_cny
            # 卖出价格是当前市场上的最高买入价格
            sell_price = vs_price.buy_cny
            # 价格盈利百分比
            profitrate = (sell_price - buy_price) / buy_price
            # 调整费率需要从标准盈利率中考虑加进来
            transfer_charge_rate = 0.001
            # 价格差异大于盈利标准则返回True
            if profitrate >= transfer_charge_rate:
                return True
            else:
                return False
        else:
            return False
    '''对指定的市场和coin进行平衡处理，返回True/False'''
    def exch_balance(self,market_base, market_vs, coin_code):
        order_base = ordermanage.OrderManage(market_base)
        order_vs = ordermanage.OrderManage(market_vs)
        # base的市场价格
        price_base = pricemanage.PriceManage(market_base, coin_code).get_coin_price()
        # 需要对比的市场价格
        price_vs = pricemanage.PriceManage(market_vs, coin_code).get_coin_price()
        #trans_price = float(self.__get_trans_price(price_base, price_vs, coin_code))

        match_price_flag=self.__price_check(coin_code,price_base,price_vs)
        #在约定的范围价格变动范围之内
        if match_price_flag:
            trans_price_buy=price_base.sell_cny
            trans_price_sell=price_vs.buy_cny
        else:
            return False
        #TODO test purpose
        #trans_price=0.01598
        # 价格两个市场变动范围不在约定的范围 内则不返回价格，不需要进行交易
        #if trans_price == None:
        #    return False
        trans_amount=self.__std_amount*self.__exch_times
        # 交易的单位是每次交易的X倍,
        # 要非常 小心 这里面的小数位，需要BTC38的接口小数位数太长会报错，接口太SB了， 不知道自己处理一下
        robot=traderobot.TradeRobot()
        trans_units = round(float(self.__std_amount / trans_price_buy * self.__exch_times),robot.get_rounding_num(coin_code))

        tradeapi=robot
        trans_status=False
        # 调用买入操作
        buy_success = tradeapi.twin_trans(order_base, 'buy', coin_code, trans_units, trans_price_buy)
        if buy_success:
            sell_success = tradeapi.twin_trans(order_vs, 'sell', coin_code, trans_units, trans_price_sell)
            # 目前的方案只要买入成功，则卖出订单不取消，只是检查状态当时有没有成交
            if sell_success:
                trans_status = True
                print('%s:均衡交易：成功,已经成功卖出:%s@%s,金额:%f,从市场@%s同样买入：当前成交！' \
                             % (self.__get_curr_time(), coin_code, market_vs, trans_amount, market_base))
                logging.info('%s:均衡交易：成功,已经成功卖出:%s@%s,金额:%f,从市场@%s同样买入：当前成交！' \
                             % (self.__get_curr_time(), coin_code, market_vs, trans_amount, market_base))
            else:
                logging.warning('%s:均衡交易：在途,已经成功卖出:%s@%s,金额:%f,从市场@%s同样买入：当前未成交！' \
                             % (self.__get_curr_time(), coin_code, market_vs, trans_amount, market_base))
        return trans_status
        pass
    '''对指定的市场和coin进行平衡处理，返回True/False'''
    def exch_balanceX(self,market_base, market_vs, coin_code):
        order_base= ordermanage.OrderManage(market_base)
        order_vs=ordermanage.OrderManage(market_vs)
        # base的市场价格
        price_base = pricemanage.PriceManage(market_base, coin_code).get_coin_price()
        # 需要对比的市场价格
        price_vs = pricemanage.PriceManage(market_vs, coin_code).get_coin_price()

        trans_price=self.__get_trans_price(price_base,price_vs,coin_code)
        #价格两个市场变动范围不在约定的范围 内则不返回价格，不需要进行交易
        if trans_price==None:
            return False
        sell_status=None
        buy_status=None
        #交易的单位是每次交易的X倍, TODO test
        trans_units=self.__std_amount/trans_price*self.__exch_times
        #同步交易,先卖后买
        sell_trans=order_vs.submitOrder(coin_code+'_cny','sell',trans_price,trans_units)
        sell_order_id=sell_trans.order_id
        if sell_order_id==1111111:
            sell_status='closed'
        #买入交易
        #buy_trans=order_base.submitOrder(coin_code+'_cny','buy',trans_price,trans_units)
        #buy_order_id=buy_trans.order_id
        #if buy_order_id == 1111111:
        #    buy_status = 'closed'
        #循环检查状态，直至交易成功后才结束返回
        trans_status=False
        waiting_seconds=0
        #最多待时间，持续检查均衡订单的状态
        max_waiting_seconds=5
        #按每次交易金额的X倍来进行帐户之间平衡
        trans_amount=self.__std_amount*self.__exch_times
        while(not trans_status and waiting_seconds<max_waiting_seconds):
            try:
                if sell_status!='closed':
                    sell_status = order_vs.getOrderStatus(sell_order_id, coin_code)
                else:
                    # 成功后再开始买入操作
                    if buy_status==None:
                        buy_trans = order_base.submitOrder(coin_code + '_cny', 'buy', trans_price, trans_units)
                        buy_order_id = buy_trans.order_id
                        time.sleep(0.1)
                        if sell_order_id == 1111111:
                            sell_status = 'closed'
                        else:
                            buy_status = order_base.getOrderStatus(buy_order_id, coin_code)
                    elif buy_status!='closed':
                        buy_status = order_base.getOrderStatus(buy_order_id, coin_code)
            except Exception as e:
                print(str(e))
                pass
            finally:
                time.sleep(1)
                waiting_seconds = waiting_seconds + 1
                if sell_status=='closed' and buy_status=='closed':
                    logging.info('%s:均衡交易：成功,已经成功卖出:%s@%s,金额:%f,从市场@%s同样买入：当前成交！'\
                    %(self.__get_curr_time(),coin_code,market_vs,trans_amount,market_base))
                    trans_status=True
                    waiting_seconds=max_waiting_seconds+5

        if waiting_seconds== max_waiting_seconds:
            #卖出一直未成功，则取消本次的操作
            if sell_status!='closed' and buy_status==None:
                cancel_status=order_base.cancelOrder(sell_order_id,coin_code)
                if cancel_status=='fail':
                    logging.warning('%s:取消卖单状态:失败,均衡交易中卖出%s@%s,金额:%f在指定时间未内成交！'%(self.__get_curr_time(),coin_code),market_vs,trans_amount)
                else:
                    logging.info('%s:取消卖单状态:成功,均衡交易中卖出%s@%s,金额:%f在指定时间未内成交！' % (self.__get_curr_time(), coin_code),
                                 market_vs, trans_amount)
            else:
                logging.warning('%s:均衡交易(buyOrderId:%s）：在途,已经成功卖出:%s@%s,金额:%f,从市场@%s同样买入：当前未成交！' \
                             % (self.__get_curr_time(),buy_order_id, coin_code, market_vs, trans_amount, market_base))

        return trans_status
        pass

    '''对全部的列表进行测试'''

    '''自动均衡两个市场之间的帐户RMB和COIN之间的关系'''
    def single_balance_market(self,market_base,market_vs,coin_code,money_pool_bal_indi=None):
        #如果需要均衡时则循环进行帐户均衡
        need_balance_flag=True
        single_bal_status=False
        order_base= ordermanage.OrderManage(market_base)
        order_vs=ordermanage.OrderManage(market_vs)
        self.__order_base=order_base
        self.__order_vs=order_vs
        # 检查两个市场的帐户状态
        try:
            status_comment='fail'
            #检查帐户状态，是不是需要均衡市场
            if money_pool_bal_indi:
                need_balance_flag = self.__check_money_pool(market_base, market_vs, coin_code)
            else:
                need_balance_flag = self.__check_coin_pool(market_base, market_vs, coin_code)
            exch_open_order_num=self.check_open_order_num(coin_code+'_cny')
            #买和卖方均衡ORDER的总数量不能超过X个，超过X个则等成交后再来生成
            if need_balance_flag and exch_open_order_num<=self.__max_open_num:
                single_bal_status=self.exch_balance(market_base,market_vs,coin_code)
                if single_bal_status:
                    status_comment = 'success'
                else:
                    status_comment = 'fail'
                #logging.info('%s: 已经自动对@%s增加RMB，对%s减少RMB进行了操作,状态:%s！' \
                #             % (self.__get_curr_time(), market_vs, market_base, status_comment))
                    #同步一次失败后10分钟后再进行同步，以确定这个交易能完成，如果完不成同步也确保不会有频繁的多次同步
                    #time.sleep(10*30)
            return status_comment
        except:
            pass
            return 'fail'

    def __get_curr_time(self):
        currtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return currtime

    '''test check balance flag'''
    def test_check_balance_flag(self):
        flag=self.__check_balance_flag('bter','btc38','ppc')
        if flag:
            print('bter市场需要均衡处理')
        else:
            print('bter市场不需要均衡处理')
        pass
    ''''''
    def test_check_money_pool(self):
        result=self.__check_money_pool('btc38','bter','doge')
        if result:
            print('资金池需要均衡')
        else:
            print('资金池不需要均衡')
    '''检查COIN池'''
    '''检查资金池的状态，确定是不是需要均衡，返回True/False'''
    def __check_coin_pool(self,market_base,market_vs,coin_code):
        try:
            order_base= ordermanage.OrderManage(market_base)
            order_vs=ordermanage.OrderManage(market_vs)
            #返回标志
            result_flag=False
            #只检查两个市场的RMB金额，默认coin是足够交易的
            bal_base=float(order_base.getMyBalance('cny'))
            bal_vs=float(order_vs.getMyBalance('cny'))
            #检查coin的数量是不是满足当前市场是总市场容量的一半
            bal_coin_base=float(order_base.getMyBalance(coin_code))
            bal_coin_vs=float(order_vs.getMyBalance(coin_code))
            #大概的交易价格
            # vs的市场价格
            price_vs = pricemanage.PriceManage(market_vs, coin_code).get_coin_price()
            #币种 的阀值倍数
            coiin_bal_times=5
            #每次交易的单位数
            trans_unit_per_time=self.__std_amount/price_vs.buy_cny
            money_pool_amt=float(self.__std_amount*self.__money_pool_size)
            total_coin_bal=(bal_coin_base+bal_coin_vs)
            #资金量在3成以上才进行同步
            if float(bal_base/(bal_base+bal_vs))>0.3 or float(bal_base)>float(money_pool_amt*0.8):
                # 帐户低于总数的30%时进行均衡,只有总的币数大于每次交易的10倍 以上才进行均衡
                if bal_coin_base/total_coin_bal<0.3 and total_coin_bal>trans_unit_per_time*10:
                    result_flag=True
        except Exception as e:
            print(str(e))
            print('获取资金池状态是否需要均衡时出错')
        return result_flag
        pass


    def test_coin_pool(self):
        coin_status=self.__check_coin_pool('bter','btc38','ltc')

        '''检查资金池的状态，确定是不是需要均衡，返回True/False'''
    def __check_money_pool(self,market_base,market_vs,coin_code):
        try:
            order_base= ordermanage.OrderManage(market_base)
            order_vs=ordermanage.OrderManage(market_vs)
            #返回标志
            result_flag=False
            #只检查两个市场的RMB金额，默认coin是足够交易的
            bal_base=order_base.getMyBalance('cny')
            bal_vs=order_vs.getMyBalance('cny')
            #检查coin的数量是不是满足当前市场是总市场容量的一半
            #bal_coin_base=float(order_base.getMyBalance(coin_code))
            bal_coin_vs=float(order_vs.getMyBalance(coin_code))
            #大概的交易价格
            # vs的市场价格
            price_vs = pricemanage.PriceManage(market_vs, coin_code).get_coin_price()
            #币种 的阀值倍数
            coiin_bal_times=5
            #每次交易的单位数
            trans_unit_per_time=self.__std_amount/price_vs.buy_cny
            money_pool_amt=self.__std_amount*self.__money_pool_size
            #帐户标准交易额的X倍，如果低于这个金额则进行两个市场的平衡
            if bal_vs<money_pool_amt:
                #只有待均衡的COIN的金额在资金池的3成以上才进行均衡
                if bal_coin_vs*price_vs.buy_cny/money_pool_amt>0.3:
                    result_flag=True
        except Exception as e:
            print(str(e))
            print('获取资金池状态是否需要均衡时出错')
        return result_flag
        pass

    '''检查COIN池的情况确定是不是需要均衡处理'''
    def __check_balance_flag(self,market_base, market_vs,coin_code):
        order_base= ordermanage.OrderManage(market_base)
        order_vs=ordermanage.OrderManage(market_vs)
        #只检查两个市场的RMB金额，默认coin是足够交易的
        bal_base=order_base.getMyBalance('cny')
        bal_vs=order_vs.getMyBalance('cny')

        #检查coin的数量是不是满足当前市场是总市场容量的一半
        bal_coin_base=float(order_base.getMyBalance(coin_code))
        bal_coin_vs=float(order_vs.getMyBalance(coin_code))
        total_coin_bal=bal_coin_base+bal_coin_vs

        #大概的交易价格
        # base的市场价格
        price_base = pricemanage.PriceManage(market_base, coin_code).get_coin_price()
        # 需要对比的市场价格
        #price_vs = pricemanage.PriceManage(market_vs, coin_code).get_coin_price()


        need_exchange=False
        #均衡市场是标准交易的多少倍
        bal_times=100
        #币种 的阀值倍数
        coiin_bal_times=5
        #每次交易的单位数
        trans_unit_per_time=self.__std_amount/price_base.sell_cny
        #帐户标准交易额的100倍，如果低于这个金额则进行两个市场的平衡
        if bal_vs<float(self.__std_amount*bal_times):
            #需要卖出市场的COIN的比例是不是占总COIN的X成以上并且余额是交易单位的指定倍数以上
            if float(bal_coin_vs)>float(total_coin_bal*0.3):
                # Coin is enough and need sell coin to get money, the estimated amount is greater than 1000
                if float(bal_coin_vs)>float(total_coin_bal*0.3) and (price_base.sell_cny*bal_coin_vs)>1000:
                    need_exchange=True
                else:
                    need_exchange=False
            else:
                # 对于COIN来说，只要是小于总量的30%才需要进行均衡
                if bal_coin_vs<float(trans_unit_per_time*coiin_bal_times) and bal_coin_vs<float(total_coin_bal*0.3):
                    need_exchange=True
        else:
            # 对于COIN来说，只要是小于总量的30%才需要进行均衡
            if bal_coin_vs < float(trans_unit_per_time * coiin_bal_times) and bal_coin_vs < float(total_coin_bal * 0.3):
                need_exchange = True
            else:
                need_exchange=False
        return need_exchange

    '''检查同时操作的完成情况，返回True/False'''
    def check_twin_trans(self,order_id_base, order_id_vs):
        pass
    '''test exch bal status'''
    def test_check_exch_bal_status(self):
        order_base= ordermanage.OrderManage('bter')
        order_vs=ordermanage.OrderManage('btc38')
        self.__order_base=order_base
        self.__order_vs=order_vs

        open_num=self.check_open_order_num('doge_cny')
        print('当前市场的均衡保单数量为:%d'%open_num)

    '''检查均衡交易的成交情况,返回未成交的次数'''
    def check_open_order_num(self,coin_code):

        exch_bal_open_order_num=0
        try:
            open_order_list_base=self.__order_base.getOpenOrderList(coin_code)
            for order in open_order_list_base:
                trans_amount=order.trans_unit*order.trans_price
                diff_rate=(trans_amount/self.__std_amount)
                #均衡交易的金额至少是标准交易的2倍以上
                if abs(diff_rate)>1.8:
                    exch_bal_open_order_num=exch_bal_open_order_num+1
            #vs market
            open_order_list_vs=self.__order_vs.getOpenOrderList(coin_code)
            for order in open_order_list_vs:
                trans_amount=order.trans_unit*order.trans_price
                diff_rate = (trans_amount / self.__std_amount)
                # 均衡交易的金额至少是标准交易的2倍以上
                if abs(diff_rate) > 1.8:
                    exch_bal_open_order_num = exch_bal_open_order_num + 1
        except Exception as e:
            print(str(e))
            #异常
            exch_bal_open_order_num=1000

        return exch_bal_open_order_num
        pass
#test
if __name__=='__main__':
    market_list=['bter','btc38']
    coin_list=['xrp','ltc','doge']
    exchbal=ExchAccountBal(market_list,coin_list,10)
    exchbal.start()

    #exchbal.exch_balance('btc38','bter','ltc')
    #exchbal.test_exch_balance()
    #exchbal.single_balance_market('bter','btc38','ltc')
    #exchbal.test_check_balance_flag()
    #exchbal.test_check_exch_bal_status()

    #test
    #exchbal.test_check_money_pool()
    #exchbal.test_coin_pool()