# -*- coding: UTF-8 -*-
import time
import requests
from FCoinAPI import api_controller
import datetime
import math
import pandas
import logging
import logging.handlers

def generate_logger(log_file_name,tag):

    logger = logging.getLogger(tag)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter( logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s") )
    logger.addHandler(ch)

    fh = logging.handlers.RotatingFileHandler(log_file_name, maxBytes=32 * 1024 * 1024, backupCount=5)
    fh.setFormatter( logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s") )
    logger.addHandler(  fh )

    return logger

logging = generate_logger("hfstrategy_v1.log", "hf_v1")

apiKEY_1 = ''
apiSECRET_1 = '' 

apiKEY_2 = ''
apiSECRET_2 = ''

api_1 = api_controller(apiKEY_1,apiSECRET_1)
api_2 = api_controller(apiKEY_2,apiSECRET_2)

logging.info('Program started...')

#balance=api.get_balance()

def GetCurrentTime():
    return str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def get_ticker(symbol):
    r = requests.get('https://api.fcoin.com/v2/market/ticker/{}'.format(symbol))
    #logging.info(r.json())
    max_buy=r.json()['data']['ticker'][2]
    min_sell = r.json()['data']['ticker'][4]
    logging.info('%s\t%s' % (max_buy,min_sell))
    return max_buy,min_sell

def get_bch_usdt(api):
    balance = api.get_balance()
    for i in balance['data']:
        if i['currency'] == 'bch':
            balance_bch = float(i['available'])
        if i['currency'] == 'usdt':
            balance_usdt = float(i['available'])
    return balance_bch,balance_usdt

def buyapi1(price, symbol, amount):
    r1=api_1.create_order(symbol, 'buy', 'limit', price, amount)
    logging.info(r1)
    if r1['status'] == 1016:
        order_ID_buy = None
        order_api1 = api_1.get_orders_list(symbol, 'submitted', '', '2', 20)
        logging.info(order_api1)
        if order_api1['data'] != []:
            a = api_1.cancle_order(order_api1['data'][0]['id'])
            logging.info(a)
    else:
        order_ID_buy = r1['data']
    return order_ID_buy


def sellapi1(price, symbol, amount):
    r2=api_1.create_order(symbol, 'sell', 'limit', price, amount)
    logging.info(r2)
    if r2['status'] == 1016:
        order_ID_sell = None
        order_api1 = api_1.get_orders_list(symbol, 'submitted', '', '2', 20)
        logging.info(order_api1)
        if order_api1['data'] != []:
            a = api_1.cancle_order(order_api1['data'][0]['id'])
            logging.info(a)
    else:
        order_ID_sell = r2['data']
    return order_ID_sell

def buyapi2(price, symbol, amount):
    r1=api_2.create_order(symbol, 'buy', 'limit', price, amount)
    logging.info(r1)
    if r1['status'] == 1016:
        order_ID_buy = None
        order_api2 = api_2.get_orders_list(symbol, 'submitted', '', '2', 20)
        logging.info(order_api2)
        if order_api2['data'] != []:
            a = api_2.cancle_order(order_api2['data'][0]['id'])
            logging.info(a)
    else:
        order_ID_buy = r1['data']
    return order_ID_buy


def sellapi2(price, symbol, amount):
    r2=api_2.create_order(symbol, 'sell', 'limit', price, amount)
    logging.info(r2)
    if r2['status'] == 1016:
        order_ID_sell = None
        order_api2 = api_2.get_orders_list(symbol, 'submitted', '', '2', 20)
        logging.info(order_api2)
        if order_api2['data'] != []:
            a = api_2.cancle_order(order_api2['data'][0]['id'])
            logging.info(a)
    else:
        order_ID_sell = r2['data']
    return order_ID_sell

ncount = 1
amount = 0.2356   # 下单量
symbol = 'bchusdt'
gapvalue = 0.03       # 价差阈值
dgap = 0.01         # 下单价小量

while 1:
    logging.info("Program running...")
    max_buy, min_sell = get_ticker(symbol)
    gap = min_sell - max_buy
    logging.info(gap)
    if(gap>=gapvalue):
        # ncount += 1
        logging.info(GetCurrentTime()+'开始下单')
        price = max_buy + dgap
        price = round(price,2)
        if (ncount % 2 ==0):
            order_ID_buy = buyapi1(price, symbol, amount)
            order_ID_sell = sellapi2(price, symbol, amount)
            ncount +=1
            if not order_ID_buy:
                logging.info(order_ID_buy)
                logging.info('账户余额不足')
                order_api1 = api_1.get_orders_list(symbol, 'submitted', '', '2', 20)
                order_api2 = api_2.get_orders_list(symbol, 'submitted', '', '2', 20)
                if len(order_api1['data'])>0:
                    api_1.cancle_order(order_api1['data'][0]['id'])
                if len(order_api2['data'])>0:   
                    api_2.cancle_order(order_api2['data'][0]['id'])
                continue
            elif not order_ID_sell:
                logging.info(order_ID_sell)
                logging.info('账户余额不足')
                order_api1 = api_1.get_orders_list(symbol, 'submitted', '', '2', 20)
                order_api2 = api_2.get_orders_list(symbol, 'submitted', '', '2', 20)
                if len(order_api1['data'])>0:
                    api_1.cancle_order(order_api1['data'][0]['id'])
                if len(order_api2['data'])>0:   
                    api_2.cancle_order(order_api2['data'][0]['id'])
                continue
            else:
                logging.info('进行第%d次交易' % ncount)
        else:
            order_ID_buy = buyapi2(price, symbol, amount)
            order_ID_sell = sellapi1(price, symbol, amount)
            ncount +=1
            if not order_ID_buy:
                logging.info(order_ID_buy)
                logging.info('账户余额不足，重新开始')
                order_api1 = api_1.get_orders_list(symbol, 'submitted', '', '2', 20)
                order_api2 = api_2.get_orders_list(symbol, 'submitted', '', '2', 20)
                if len(order_api1['data'])>0:
                    api_1.cancle_order(order_api1['data'][0]['id'])
                if len(order_api2['data'])>0:   
                    api_2.cancle_order(order_api2['data'][0]['id'])
                continue
            elif not order_ID_sell:
                logging.info(order_ID_sell)
                logging.info('账户余额不足，重新开始')
                order_api1 = api_1.get_orders_list(symbol, 'submitted', '', '2', 20)
                order_api2 = api_2.get_orders_list(symbol, 'submitted', '', '2', 20)
                if len(order_api1['data'])>0:
                    logging.info('len(order_api1_buy[data])>0  cancle_order')
                    logging.info(order_api1['data'][0]['id'])
                    api_1.cancle_order(order_api1['data'][0]['id'])
                if len(order_api2['data'])>0:
                    logging.info('len(order_api2_sell[data])>0  cancle_order')
                    logging.info(order_api2['data'][0]['id'])
                    api_2.cancle_order(order_api2['data'][0]['id'])
                continue
            else:
                logging.info('进行第%d次交易' % ncount)
    else:
        logging.info('###################   gap太小   ###################')
        logging.info(GetCurrentTime())
        continue

    t=0

    while (t<1):

        order_api1 = api_1.get_orders_list(symbol, 'submitted', '', '2', 20)
        order_api2 = api_2.get_orders_list(symbol, 'submitted', '', '2', 20)

        if len(order_api1['data'])>1 or len(order_api2['data'])>1:
            #raise Exception('more than 1 submitted order')
            logging.info('\nmore than 1 submitted order\n')
            #撤单机制
            if len(order_api1['data'])>0:
                logging.info('len(order_api1_buy[data])>0  cancle_order')
                logging.info(order_api1['data'][0]['id'])
                api_1.cancle_order(order_api1['data'][0]['id'])
            if len(order_api2['data'])>0:
                logging.info('len(order_api2_sell[data])>0  cancle_order')
                logging.info(order_api2['data'][0]['id'])
                api_2.cancle_order(order_api2['data'][0]['id'])
        elif len(order_api1['data']) ==1 or len(order_api2['data']) ==1:
            time.sleep(0.2)
            t=t + 0.2
            logging.info('未成交，已下单{}秒'.format(t))
            continue
        elif len(order_api1['data']) ==0:
            if len(api_1.get_orders_list(symbol, 'partial_filled', '', '2', 20)['data'])==1:
                time.sleep(0.2)
                t = t + 0.2
                logging.info('p   t:{}'.format(t))
                continue
            else:
            #order filled
                break
        elif len(order_api2['data']) ==0:
            if len(api_2.get_orders_list(symbol, 'partial_filled', '', '2', 20)['data'])==1:
                time.sleep(0.2)
                t = t + 0.2
                logging.info('p   t:{}'.format(t))
                continue
            else:
            #order filled
                break
    # if (t>1):
        #order not filled,cancel order
    api_1.cancle_order(order_ID_buy)
    api_2.cancle_order(order_ID_sell)
    
    # logging.info('取消订单')
    # logging.info()
    # else:
    logging.info("#####################")
    logging.info('订单已成交!')
    logging.info("#####################\n")
    logging.info('\n')
    balance_bch1, balance_usdt1 = get_bch_usdt(api_1)
    balance_bch2, balance_usdt2 = get_bch_usdt(api_2)
    logging.info('#当前账户1持仓:\n   bch:{}  usdt:{}  市值:{} usdt'.format(balance_bch1, balance_usdt1,balance_bch1 * max_buy + balance_usdt1))
    logging.info('#当前账户2持仓:\n   bch:{}  usdt:{}  市值:{} usdt'.format(balance_bch2, balance_usdt2,balance_bch2 * max_buy + balance_usdt2))
    logging.info('\n')

    time.sleep(2)
