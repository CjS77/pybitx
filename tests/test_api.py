import base64
import unittest
import requests_mock

from pybitx import api
from pybitx.api import BitX, BitXAPIError


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

    @staticmethod
    def make_auth_header(auth):
        s = ':'.join(auth)
        k = base64.b64encode(s)
        return 'Basic %s' % (k,)

    def setUp(self):
        options = {
            'hostname': 'api.dummy.com',
            'pair': 'XBTZAR'
        }
        key = 'mykey'
        secret = 'mysecret'
        self.api = BitX(key, secret, options)
        self.auth_string = TestAPICalls.make_auth_header(self.api.auth)

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
        result = self.api.get_order_book(1)
        self.assertDictEqual(result, {
            "timestamp": 1366305398592,
            "bids": [
                {
                    "volume": "0.10",
                    "price": "1100.00"
                }
            ],
            "asks": [
                {
                    "volume": "0.10",
                    "price": "1180.00"
                }
            ]
        })


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
        result = self.api.get_trades(1)
        self.assertDictEqual(result, {"trades": [response['trades'][0]]} )

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

    @requests_mock.Mocker()
    def testListOrdersAuth(self, m):
        response = {
            "order_id": "BXHW6PFRRXKFSB4",
            "creation_timestamp": 1402866878367,
            "expiration_timestamp": 0,
            "type": "ASK",
            "state": "PENDING",
            "limit_price": "6500.00",
            "limit_volume": "0.05",
            "base": "0.03",
            "counter": "195.02",
            "fee_base": "0.000",
            "fee_counter": "0.00",
            "trades": [
                {
                    "price": "6501.00",
                    "timestamp": 1402866878467,
                    "volume": "0.02"
                },
                {
                    "price": "6500.00",
                    "timestamp": 1402866878567,
                    "volume": "0.01"
                }
            ],
        }
        url = 'https://api.dummy.com/api/1/orders/BXHW6PFRRXKFSB4'
        m.get(url, json=response, request_headers={'Authorization': self.auth_string})
        result = self.api.get_order('BXHW6PFRRXKFSB4')
        self.assertDictEqual(result, response)

    @requests_mock.Mocker()
    def testFundingAddresses(self, m):
        response = {"asset": "XBT", "address": "1GVZeHQVCkJfKLz2pL5LiPeAKwdMXrgoNs", "name": "",
                    "account_id": "123456", "assigned_at": 1412659801000, "total_received": "0.67",
                    "total_unconfirmed": "0.00"}
        url = 'https://api.dummy.com/api/1/funding_address?asset=XBT'
        m.get(url, json=response, request_headers={'Authorization': self.auth_string})
        result = self.api.get_funding_address('XBT')
        self.assertDictEqual(result, response)

    @requests_mock.Mocker()
    def testWithdrawalsStatus(self, m):
        response = {
            "withdrawals": [
                {
                    "status": "PENDING",
                    "id": "2221"
                },
                {
                    "status": "COMPLETED",
                    "id": "1121"
                }
            ]
        }
        url = 'https://api.dummy.com/api/1/withdrawals'
        m.get(url, json=response, request_headers={'Authorization': self.auth_string})
        result = self.api.get_withdrawals_status()
        self.assertDictEqual(result, response)

    @requests_mock.Mocker()
    def testWithdrawalsStatus(self, m):
        response = {"status": "COMPLETED", "id": "1121"}
        url = 'https://api.dummy.com/api/1/withdrawals/1121'
        m.get(url, json=response, request_headers={'Authorization': self.auth_string})
        result = self.api.get_withdrawals_status("1121")
        self.assertDictEqual(result, response)

    @requests_mock.Mocker()
    def testBalance(self, m):
        response = {
            "balance": [
                {
                    "account_id": "1224342323",
                    "asset": "XBT",
                    "balance": "1.012423",
                    "reserved": "0.01",
                    "unconfirmed": "0.421",
                    "name": "XBT Account"
                },
                {
                    "account_id": "2997473",
                    "asset": "ZAR",
                    "balance": "1000.00",
                    "reserved": "0.00",
                    "unconfirmed": "0.00",
                    "name": "ZAR Account"
                }
            ]
        }
        url = 'https://api.dummy.com/api/1/balance'
        m.get(url, json=response, request_headers={'Authorization': self.auth_string})
        result = self.api.get_balance()
        self.assertDictEqual(result, response)

    @requests_mock.Mocker()
    def testTransactions(self, m):
        trec = [
            {
                "row_index": 2,
                "timestamp": 1429908835000,
                "balance": 0.08,
                "available": 0.08,
                "balance_delta": -0.02,
                "available_delta": -0.02,
                "currency": "XBT",
                "description": "Sold 0.02 BTC"
            },
            {
                "row_index": 1,
                "timestamp": 1429908701000,
                "balance": 0.1,
                "available": 0.1,
                "balance_delta": 0.1,
                "available_delta": 0.1,
                "currency": "XBT",
                "description": "Bought 0.1 BTC"
            }
        ]
        url = 'https://api.dummy.com/api/1/accounts/319232323/transactions'
        m.get(url, json={"id": "319232323", "transactions": trec}, request_headers={'Authorization': self.auth_string})
        m.get(url+'?max_row=1', json={"id": "319232323", "transactions": [trec[0]]}, request_headers={'Authorization': self.auth_string})
        m.get(url+'?min_row=2', json={"id": "319232323", "transactions": [trec[1]]}, request_headers={'Authorization': self.auth_string})
        result = self.api.get_transactions('319232323')
        self.assertDictEqual(result, {"id": "319232323", "transactions": trec})
        result = self.api.get_transactions('319232323', max_row=1)
        self.assertDictEqual(result, {"id": "319232323", "transactions": [trec[0]]})
        result = self.api.get_transactions('319232323', 1, 1)
        self.assertDictEqual(result, {"id": "319232323", "transactions": [trec[0]]})
        result = self.api.get_transactions('319232323', min_row=2)
        self.assertDictEqual(result, {"id": "319232323", "transactions": [trec[1]]})
        result = self.api.get_transactions('319232323', 2, 2)
        self.assertDictEqual(result, {"id": "319232323", "transactions": [trec[1]]})

    @requests_mock.Mocker()
    def testPending(self, m):
        response = {
            "id": "319232323",
            "pending": [
                {
                    "timestamp": 1429908835000,
                    "balance": 0.03,
                    "available": 0.03,
                    "balance_delta": 0.03,
                    "available_delta": 0.03,
                    "currency": "XBT",
                    "description": "Received Bitcoin - 1 of 3 confirmations"
                }
            ]
        }
        url = 'https://api.dummy.com/api/1/accounts/319232323/pending'
        m.get(url, json=response, request_headers={'Authorization': self.auth_string})
        result = self.api.get_pending_transactions('319232323')
        self.assertDictEqual(result, response)

    @requests_mock.Mocker()
    def testCreateOrder(self, m):
        response = {
            "order_id": "BXMC2CJ7HNB88U4"
        }
        url = 'https://api.dummy.com/api/1/postorder'
        m.post(url, json=response, request_headers={'Authorization': self.auth_string})
        result = self.api.create_limit_order('buy', 0.1, 500)
        data = {s.split('=')[0]:s.split('=')[1] for s in m.request_history[0].text.split('&')}
        self.assertEqual(data['pair'], 'XBTZAR')
        self.assertEqual(data['volume'], '0.1')
        self.assertEqual(data['price'], '500')
        self.assertDictEqual(result, response)

def main():
    unittest.main()


if __name__ == '__main__':
    main()
