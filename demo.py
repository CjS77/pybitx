from pybitx.api import BitX
import os
import pprint

pp = pprint.PrettyPrinter(indent=4, width=80)


def format_call(name, results):
    print '-'*80
    print '%50s' % (name,)
    print '-'*80
    pp.pprint(results)
    print '-'*80


def runDemo():
    user = ''
    password = ''
    auth = 'BITX_KEY' in os.environ and 'BITX_SECRET' in os.environ
    if auth:
        user = os.environ['BITX_KEY']
        password = os.environ['BITX_SECRET']
    else:
        print "Note: I couldn't find a BITX_KEY environment variable. This means that none of the API queries\nthat " \
              "require authentication will work. I'll carry on anyway, but make sure your credentials are available " \
              "in the BITX_KEY and BITX_SECRET environment variables and run this demo again"
    api = BitX(user, password)
    kind = 'auth' if auth else 'none'
    format_call('  Ticker   ', api.get_ticker(kind))
    format_call('All Tickers', api.get_all_tickers(kind))
    format_call('Order book ', api.get_order_book(5, kind))
    format_call('   Trades  ', api.get_trades(10, kind))
    if auth:
        format_call('   Orders  ', api.get_orders())
        format_call('Funding address', api.get_funding_address('XBT'))
        format_call('   Balance ', api.get_balance())


if __name__ == '__main__':
    runDemo()