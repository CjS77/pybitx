import unittest
import requests_mock
import api
from api import BitX, BitXAPIError
import base64


def make_auth_header(auth):
    s = ':'.join(auth)
    k = base64.b64encode(s)
    return 'Basic %s' % (k,)


class TestBitX(unittest.TestCase):
    def testConstructor(self):
        api = BitX('', '', {})
        self.assertTrue(isinstance(api, BitX))

    def testOptions(self):
        api = BitX('', '')
        self.assertEqual(api.hostname, 'api.mybitx.com')
        self.assertEqual(api.port, 443)
        self.assertEqual(api.pair, 'XBTZAR')

    def testCustomOptionsAndAuth(self):
        options = {
            'hostname': 'localhost',
            'port': 8000,
            'pair': 'XBTUSD'
        }
        key = 'cnz2yjswbv3jd'
        secret = '0hydMZDb9HRR3Qq-iqALwZtXLkbLR4fWxtDZvkB9h4I'
        api = BitX(key, secret, options)
        self.assertEqual(api.hostname, options['hostname'])
        self.assertEqual(api.port, options['port'])
        self.assertEqual(api.pair, options['pair'])
        self.assertEqual(api.auth, (key, secret))

    def testConstructURL(self):
        api = BitX('', '')
        url = api.construct_url('test')
        self.assertEqual(url, 'https://api.mybitx.com/api/1/test')

    def testConstructURLWithHost(self):
        options = {
            'hostname': 'localhost',
        }
        api = BitX('', '', options)
        url = api.construct_url('test')
        self.assertEqual(url, 'https://localhost/api/1/test')

    def testConstructURLWithPort(self):
        options = {
            'port': 40000
        }
        api = BitX('', '', options)
        url = api.construct_url('test')
        self.assertEqual(url, 'https://api.mybitx.com:40000/api/1/test')

    def testConstructURLWithPortAndHost(self):
        options = {
            'hostname': 'localhost',
            'port': 40000
        }
        api = BitX('', '', options)
        url = api.construct_url('test')
        self.assertEqual(url, 'https://localhost:40000/api/1/test')


class TestAPICalls(unittest.TestCase):
    def setUp(self):
        options = {
            'hostname': 'api.dummy.com',
            'pair': 'XBTZAR'
        }
        key = 'mykey'
        secret = 'mysecret'
        self.api = BitX(key, secret, options)
        self.auth_string = make_auth_header(self.api.auth)


    @requests_mock.Mocker()
    def testHeaders(self, m):
        headers = {
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8',
            'User-Agent': 'py-bitx v' + api.__version__
        }
        m.get('https://api.dummy.com/api/1/ticker?pair=XBTZAR', json={'success': True}, request_headers=headers)
        result = self.api.get_ticker()
        self.assertTrue(result['success'])

    @requests_mock.Mocker()
    def testTickerCall(self, m):
        response = {
            "ask": "1050.00",
            "timestamp": 1366224386716,
            "bid": "924.00",
            "rolling_24_hour_volume": "12.52",
            "last_trade": "950.00"
        }
        m.get('https://api.dummy.com/api/1/ticker?pair=XBTZAR', json=response)
        result = self.api.get_ticker()
        self.assertDictEqual(result, response)

    @requests_mock.Mocker()
    def testInvalidTickerCall(self, m):
        response = {"error": "Invalid currency pair.", "error_code": "ErrInvalidPair"}
        m.get('https://api.dummy.com/api/1/ticker', json=response)
        url = 'https://api.dummy.com/api/1/ticker'
        try:
            self.api.get_ticker()
            self.fail('Exception not thrown')
        except BitXAPIError as e:
            self.assertEqual(e.code, 200)
            self.assertEqual(e.url, url + '?pair=' + self.api.pair)

    @requests_mock.Mocker()
    def testAllTickers(self, m):
        response = {"tickers": [
            {"timestamp": 1448572753005, "bid": "72630.00", "ask": "78345.00", "last_trade": "72630.00",
             "rolling_24_hour_volume": "0.00", "pair": "XBTNGN"},
            {"timestamp": 1448572752955, "bid": "1451.00", "ask": "1465.00", "last_trade": "1453.00",
             "rolling_24_hour_volume": "155.025742", "pair": "XBTMYR"},
            {"timestamp": 1448572752983, "bid": "4899.00", "ask": "4900.00", "last_trade": "4900.00",
             "rolling_24_hour_volume": "142.516363", "pair": "XBTZAR"}
        ]}
        m.get('https://api.dummy.com/api/1/tickers', json=response)
        result = self.api.get_all_tickers()
        self.assertDictEqual(result, response)

    @requests_mock.Mocker()
    def testOrderBook(self, m):
        response = {
            "timestamp": 1366305398592,
            "bids": [
                {
                    "volume": "0.10",
                    "price": "1100.00"
                },
                {
                    "volume": "0.10",
                    "price": "1000.00"
                },
                {
                    "volume": "0.10",
                    "price": "900.00"
                }
            ],
            "asks": [
                {
                    "volume": "0.10",
                    "price": "1180.00"
                },
                {
                    "volume": "0.10",
                    "price": "2000.00"
                }
            ]
        }
        m.get('https://api.dummy.com/api/1/orderbook', json=response)
        result = self.api.get_order_book()
        self.assertDictEqual(result, response)

    @requests_mock.Mocker()
    def testTrades(self, m):
        response = {
            "trades": [
                {
                    "volume": "0.10",
                    "timestamp": 1366052621774,
                    "price": "1000.00"
                },
                {
                    "volume": "1.20",
                    "timestamp": 1366052621770,
                    "price": "1020.50"
                }
            ]
        }
        m.get('https://api.dummy.com/api/1/trades', json=response)
        result = self.api.get_trades()
        self.assertDictEqual(result, response)

    @requests_mock.Mocker()
    def testListOrdersAuth(self, m):
        response = {
            "orders": [
                {
                    "base": "0.027496",
                    "counter": "81.140696",
                    "creation_timestamp": 1423990327333,
                    "expiration_timestamp": 0,
                    "fee_base": "0.00",
                    "fee_counter": "0.00",
                    "limit_price": "2951.00",
                    "limit_volume": "0.027496",
                    "order_id": "BXF3J88PZAYGXH7",
                    "pair": "XBTZAR",
                    "state": "COMPLETE",
                    "type": "ASK",

                }
            ]
        }
        url = 'https://api.dummy.com/api/1/listorders?pair=XBTZAR'
        m.get(url, json=response, request_headers={'Authorization': self.auth_string})
        result = self.api.get_orders()
        self.assertDictEqual(result, response)

    @requests_mock.Mocker()
    def testListOrdersUnAuth(self, m):
        url = 'https://api.dummy.com/api/1/listorders?pair=XBTZAR'
        m.get(url, text='', status_code=401)
        try:
            self.api.get_orders(kind='basic')
            self.fail('Exception not thrown')
        except BitXAPIError as e:
            self.assertEqual(e.code, 401)
            self.assertEqual(e.url, url)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
