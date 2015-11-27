import requests
import logging
from concurrent.futures import ThreadPoolExecutor

log = logging.getLogger(__name__)

__version__ = '0.1.0'


# --------------------------- constants -----------------------

class BitXAPIError(ValueError):
    def __init__(self, response):
        self.url = response.url
        self.code = response.status_code
        self.message = response.text

    def __str__(self):
        return "BitX request %s failed with %d: %s" % (self.url, self.code, self.message)


class BitX:
    def __init__(self, key, secret, options={}):
        self.options = options
        self.auth = (key, secret)
        if 'hostname' in options:
            self.hostname = options['hostname']
        else:
            self.hostname = 'api.mybitx.com'
        self.port = options['port'] if 'port' in options else 443
        self.pair = options['pair'] if 'pair' in options else 'XBTZAR'
        self.ca = options['ca'] if 'ca' in options else None
        self.timeout = options['timeout'] if 'timeout' in options else 30
        self.headers = {
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8',
            'User-Agent': 'py-bitx v' + __version__
        }
        self._executor = ThreadPoolExecutor(max_workers=5)

    def close(self):
        log.info('Asking MultiThreadPool to shutdown')
        self._executor.shutdown(wait=True)
        log.info('MultiThreadPool has shutdown')

    def construct_url(self, call):
            base = self.hostname
            if self.port != 443:
                base += ':%d' % (self.port,)
            return "https://%s/api/1/%s" % (base, call)

    def api_request(self, call, params, kind='auth'):
        """
        General API request. Generally, use the convenience functions below
        :param kind: the type of request to make. 'auth' makes an authenticated call; 'basic' is unauthenticated
        :param call: the API call to make
        :param params: a dict of query parameters
        :return: a json response, a BitXAPIError is thrown if the api returns with an error
        """
        url = self.construct_url(call)
        if kind == 'auth':
            future = self._executor.submit(requests.get, url, params, headers=self.headers, auth=self.auth)
        else:
            future = self._executor.submit(requests.get, url, params, headers=self.headers)
        response = future.result(timeout=self.timeout)
        try:
            result = response.json()
        except ValueError:
            result = {'error': 'No JSON content returned'}
        if response.status_code != 200 or 'error' in result:
            raise BitXAPIError(response)
        else:
            return result

    def get_ticker(self, kind='auth'):
        params = {'pair': self.pair}
        return self.api_request('ticker', params, kind=kind)

    def get_all_tickers(self, kind='auth'):
        return self.api_request('tickers', None, kind=kind)

    def get_order_book(self, kind='auth'):
        params = {'pair': self.pair}
        return self.api_request('orderbook', params, kind=kind)

    def get_trades(self, kind='auth'):
        params = {'pair': self.pair}
        return self.api_request('trades', params, kind=kind)

    def get_orders(self, state=None, kind='auth'):
        """
        Returns a list of the most recently placed orders. You can specify an optional state='PENDING' parameter to
        restrict the results to only open orders. You can also specify the market by using the optional pair parameter.
        The list is truncated after 100 items.
        :param state: String optional 'COMPLETE', 'PENDING', or None (default)
        :return:
        """
        params = {'pair': self.pair}
        if state is not None:
            params['state'] = state
        return self.api_request('listorders', params, kind=kind)
