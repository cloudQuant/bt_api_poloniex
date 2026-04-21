# bt_api_poloniex

Poloniex exchange plugin for `bt_api`.

## Installation

```bash
pip install bt_api_poloniex
```

## Usage

```python
from bt_api_poloniex import PoloniexRequestDataSpot

feed = PoloniexRequestDataSpot(public_key="your_key", private_key="your_secret")
ticker = feed.get_ticker("BTCUSDT")
```

## Architecture

```
bt_api_poloniex/
├── exchange_data/         # Exchange configuration and REST/WSS paths
├── errors/               # Error translator
├── tickers/              # Ticker data container
├── feeds/live_poloniex/ # REST API implementation
├── containers/orders/    # Order data container
└── containers/balances/ # Balance data container
```