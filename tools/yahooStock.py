
import requests
import json
import sys
import time

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

colors = {
    'grey': '1;30',
    'red': '0;31',
    'green': '0;32',
    'yellow': '1;33',
}


def build_yql(stockid):
    if isinstance(stockid, list):
        stockid = ', '.join(['"%s"' %(i) for i in stockid])
    else:
        stockid = '"%s"' %(stockid)
    yql = 'select * from yahoo.finance.quotes where symbol in (%s)' %(stockid)
    return yql


def get_stock(stockid):
    if not stockid:
        return None
    paras = {
        'q': build_yql(stockid),
        'format': 'json',
        'env': 'store://datatables.org/alltableswithkeys',
        'callback': '',
    }
    url = 'http://query.yahooapis.com/v1/public/yql?'+ urlencode(paras)
    r = requests.get(url)
    if r.status_code != 200:
        return None
    result = json.loads(r.text)
    return result


def print_stock(sdata, color=True):
    try:
        price_now = float(sdata['LastTradePriceOnly'])
        price_last = float(sdata['PreviousClose'])
    except (ValueError, TypeError):
        val_str = sdata['symbol'] + ' error'
        if color:
            print('\033[%sm %10s \033[0m' %(colors['grey'], val_str))
        else:
            print(val_str)
        return
    change = price_now - price_last
    crate = 100 * change / price_last
    val_str = '%10s %-8s %7.2f %6.3f%% %-8s %-8s %-8s %-8s %s -' %(sdata['symbol'],
        sdata['LastTradePriceOnly'], change, crate,
        sdata['Open'], sdata['PreviousClose'], sdata['DaysHigh'], sdata['DaysLow'],
        sdata['LastTradeTime'])
    if change > 0:
        color_code = colors['red']
    elif change < 0:
        color_code = colors['green']
    else:
        color_code = colors['yellow']
    if color:
        print('\033[%sm %s \033[0m' %(color_code, val_str))
    else:
        print(val_str)

def print_stocks(stock_data, color=True):
    stock_data = stock_data['query']['results']
    if stock_data is None:
        return
    for sdata in stock_data['quote']:
        print_stock(sdata, color)
    print('')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.exit('not any stock')
    while True:
        try:
            r = get_stock(sys.argv[1:])
            if r is not None:
                print_stocks(r)
        finally:
            pass
        time.sleep(10)

