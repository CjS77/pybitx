import requests
import logging
from concurrent.futures import ThreadPoolExecutor

log = logging.getLogger(__name__)

__version__ = '0.1.0'


# --------------------------- constants -----------------------

class BitXAPIError(ValueError):
    def __init__(self, url, response):
        self.url = url
        self.code = response.status_code
        self.message = response.text

    def __str__(self):
        return "BitX request %s failed with %d: %s" % (self.url, self.code, self.message)


class BitX:
    def __init__(self, key, secret, options={}):
        self.options = options
        self.auth = "%s:%s" % (key, secret)
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

    def construct_url(self, call, kind='basic'):
        if kind == 'basic':
            base = self.hostname
            if self.port != 443:
                base += ':%d' % (self.port,)
            return "https://%s/api/1/%s" % (base, call)

    def api_request(self, call, params):
        """
        General API request. Generally, use the convenience functions below
        :param call: the API call to make
        :param params: a dict of query parameters
        :return: a json response, a BitXAPIError is thrown if the api returns with an error
        """
        url = self.construct_url(call)
        future = self._executor.submit(requests.get, url, params)
        response = future.result(timeout=self.timeout)
        result = response.json()
        if 'error' in result:
            raise BitXAPIError(url, response)
        else:
            return result

    def get_ticker(self):
        params = {
            'pair': self.pair
        }
        return self.api_request('ticker', params)

    def get_all_tickers(self):
        return self.api_request('tickers', None)
