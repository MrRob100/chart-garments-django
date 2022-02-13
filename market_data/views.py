import json
import os
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
    formatted = pair[:3].upper() + '_' + pair[3:].upper()
    url = 'https://api-fxtrade.oanda.com/v3/accounts/' + os.environ.get('OANDA_ACCOUNT_ID') + '/candles/latest?instrument=' + formatted

    headers = {
        'Authorization': 'Bearer ' + os.environ.get('OANDA_TOKEN')
    }

    response = requests.request("GET", url, headers=headers)

    print(response.text)

    return HttpResponse('ok')


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

    # return HttpResponse(r.text)
    # return HttpResponse(sorted(dict.lastPrice))