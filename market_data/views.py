import json
import math
import os
from symtable import Symbol
import time
from datetime import datetime, timedelta
import requests
from django.http import HttpResponse
from django.shortcuts import render

from .models import Candle, SymbolList


def stock_candles(request, symbol):
    time_threshold = datetime.now() - timedelta(hours=5)
    record = Candle.objects.filter(asset_class='stock', symbol=symbol, date_added__gt=time_threshold)

    if record.exists():
        response = record.latest('data').data
    else:
        headers = {
            'APCA-API-KEY-ID': os.environ.get('ALPACA_KEY'),
            'APCA-API-SECRET-KEY': os.environ.get('ALPACA_SECRET')
        }

        start = (datetime.today() - timedelta(days=200)).date()
        end = (datetime.today() - timedelta(days=1)).date()
        r = requests.get('https://data.alpaca.markets/v2/stocks/' + symbol + '/bars?timeframe=1Day&start=' + str(start) + '&end=' + str(end), headers=headers)
        if r.status_code == 200:
            response = r.text
            Candle.objects.create(symbol=symbol.upper(), asset_class='stock', data=response)
        else:
            return HttpResponse(status=r.status_code)

    """Format response"""


    return HttpResponse(response)

def crypto_candles(request, symbol):
    time_threshold = datetime.now() - timedelta(hours=5)
    record = Candle.objects.filter(asset_class='crypto', symbol=symbol, date_added__gt=time_threshold)

    if record.exists():
        candles = record.latest('data').data
    else:
        Candle.objects.filter(asset_class='crypto', symbol=symbol).delete()
        r = requests.get('https://www.binance.com/api/v3/klines?symbol=' + symbol.upper() + 'USDT&interval=1d')
        if r.status_code == 200:
            response = r.text
            list = json.loads(response)

            data = []
            for item in list:
                data.append([item[0], float(item[1]), float(item[2]), float(item[3]), float(item[4])])

            candles = json.dumps(data)
            Candle.objects.create(symbol=symbol.upper(), asset_class='crypto', data=candles)
        else:
            return HttpResponse(status=r.status_code)

    return HttpResponse(candles)

def forex_candles(request, pair):
    time_threshold = datetime.now() - timedelta(hours=5)
    pair = (pair[:3] + pair[3:]).upper()
    record = Candle.objects.filter(asset_class='forex', symbol=pair, date_added__gt=time_threshold)

    if record.exists():
        candles = record.latest('data').data
    else:
        pair_formatted = pair[:3].upper() + '_' + pair[3:].upper()
        url = 'https://api-fxtrade.oanda.com/v3/accounts/' + os.environ.get('OANDA_ACCOUNT_ID') + '/candles/latest?instrument=' + pair_formatted + '&granularity=D'

        headers = {
            'Authorization': 'Bearer ' + os.environ.get('OANDA_TOKEN')
        }

        r = requests.request("GET", url, headers=headers)

        if (r.status_code == 200):
            response = r.text

            list = json.loads(response)

            data = []
            for item in list['candles']:
                time_string = item['time'][:10]
                unix = time.mktime(datetime.strptime(time_string, "%Y-%m-%d").timetuple())
                o = item['mid']['o']
                h = item['mid']['h']
                l = item['mid']['l']
                c = item['mid']['c']
                data.append([math.floor(unix), float(o), float(h), float(l), float(c)])

            candles = json.dumps(data)
            Candle.objects.create(symbol=pair, asset_class='forex', data=candles)
        else:
            return HttpResponse(r.text, status=r.status_code)

    return HttpResponse(candles)

def stock_symbols(request):
    """Gets list of stock symbols from Apaca"""

    time_threshold = datetime.now() - timedelta(days=10)
    record = SymbolList.objects.filter(asset_class='stockFFF', date_added__gt=time_threshold)

    if record.exists():
        data = record.latest('data').symbols
    else:
        headers = {
            'APCA-API-KEY-ID': os.environ.get('ALPACA_KEY'),
            'APCA-API-SECRET-KEY': os.environ.get('ALPACA_SECRET')
        }

        r = requests.get('https://broker-api.alpaca.markets/v1/assets', headers=headers)

        if r.status_code == 200:
            list = json.loads(r.text)

            data = []
            for item in list:
                data.append({'name': item['symbol']})


            SymbolList.objects.create(asset_class='stock', symbols=data, source='alpaca')
        else:
            return HttpResponse(data, status=r.status_code)


    return HttpResponse(data)

def crypto_symbols(request):
    """Gets list of symbols on binance ordering in a a sinsible order"""

    time_threshold = datetime.now() - timedelta(days=10)
    record = SymbolList.objects.filter(asset_class='crypto', date_added__gt=time_threshold)

    if record.exists():
        formatted = record.latest('symbols').symbols
    else:
        r = requests.get('https://api3.binance.com/api/v3/ticker/24hr')

        if r.status_code == 200:
            list = json.loads(r.text)


            # def myFunc(e):
            #     return float(e['prevClosePrice'])

            # list.sort(key=myFunc)


            data = []
            for item in list:
                if item['symbol'][-4:] == 'USDT':
                    data.append({'name': item['symbol'][:-4]})


            formatted = json.dumps(data)

            SymbolList.objects.create(asset_class='crypto', symbols=formatted, source='binance')
        else:
            return HttpResponse(status=r.status_code)


    return HttpResponse(formatted)


def forex_symbols(request):
    """Gets list of forex pairs"""
    #GBP
    #USD
    #EUR
    #CHF
    #CAD
    #AUD
    #JPY
    #NZD
    #CNH

    return HttpResponse([
        {'name': 'NZDUSD'},
        {'name': 'USDJPY'},
        {'name': 'USDCAD'},
        {'name': 'USDCHF'},
        {'name': 'USDCNH'},
        {'name': 'GBPCHF'},
        {'name': 'GBPCAD'},
        {'name': 'GBPAUD'},
        {'name': 'GBPJPY'},
        {'name': 'GBPUSD'},
        {'name': 'GBPNZD'},
        {'name': 'EURUSD'},
        {'name': 'EURJPY'},
        {'name': 'EURCAD'},
        {'name': 'EURNZD'},
        {'name': 'EURAUD'},
        {'name': 'AUDUSD'},
        {'name': 'AUDNZD'},
        {'name': 'AUDCAD'},
        {'name': 'AUDCHF'},
        {'name': 'AUDJPY'},
        {'name': 'AUDUSD'},
    ])