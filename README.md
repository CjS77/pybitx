# pybitx
BitX API for python ([See API documentation](https://www.luno.com/en/api)).

# Installation
```bash
pip install pybitx
```

#### For Developers
Clone this repo and create a virtual environment
```bash
git clone https://github.com/CjS77/pybitx
cd pybitx
virtualenv -p /usr/bin/python2.7 env
source env/bin/activate
pip install -e .[dev]
python2.7 tests/test_api.py # For good measure
```

# Usage

See the [tests](tests/) for detailed usage examples, but basically:

## API object creation

    from pybitx.api import BitX
    api = BitX(key, secret. options)

Where `options` can be

| option key   | description      | default |
|--------------|------------------|---------|
|hostname | the API host | api.mybitx.com |
|port | the TCP port to attach to | 443 |
|pair | The currency pair to provide results for | XBTZAR |
|ca | The root certificate | None |
|timeout | The maximum time to wait for requests | 30 (s) |

## API calls

### Latest ticker

    api.get_ticker()

**Returns**: dictionary containing the latest ticker values

### All tickers

    api.get_all_tickers()

**Returns**: dictionary containing the latest ticker values for all currency pairs

# Acknowledgements

A nod to @bausmeier/node-bitx for the node.js version, which helped
accelerate the development of this code