import unittest
import requests_mock
from api import BitX, BitXAPIError


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
        self.assertEqual(api.auth, key + ':' + secret)

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
        key = 'cnz2yjswbv3jd'
        secret = '0hydMZDb9HRR3Qq-iqALwZtXLkbLR4fWxtDZvkB9h4I'
        self.api = BitX(key, secret, options)

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
            self.assertEqual(e.url, url)

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


def main():
    unittest.main()


if __name__ == '__main__':
    main()
