from __future__ import annotations

from bt_api_base.containers.exchanges.exchange_data import ExchangeData


class PoloniexExchangeData(ExchangeData):
    def __init__(self) -> None:
        super().__init__()
        self.exchange_name = "poloniex"
        self.rest_url = "https://api.poloniex.com"
        self.wss_url = "wss://ws.poloniex.com/ws/public"
        self.acct_wss_url = "wss://ws.poloniex.com/ws/private"
        self.rest_paths = {}
        self.wss_paths = {}
        self.kline_periods = {
            "1m": "MINUTE_1",
            "5m": "MINUTE_5",
            "10m": "MINUTE_10",
            "15m": "MINUTE_15",
            "30m": "MINUTE_30",
            "1h": "HOUR_1",
            "2h": "HOUR_2",
            "4h": "HOUR_4",
            "6h": "HOUR_6",
            "12h": "HOUR_12",
            "1d": "DAY_1",
            "3d": "DAY_3",
            "1w": "WEEK_1",
            "1M": "MONTH_1",
        }
        self.reverse_kline_periods = {v: k for k, v in self.kline_periods.items()}
        self.legal_currency = ["USDT", "USD", "BTC", "ETH"]

    def get_symbol(self, symbol: str) -> str:
        symbol = symbol.upper().replace("/", "_").replace("-", "_")
        if "_" in symbol:
            return symbol
        for lc in sorted(self.legal_currency, key=len, reverse=True):
            if symbol.endswith(lc) and len(symbol) > len(lc):
                return f"{symbol[: -len(lc)]}_{lc}"
        return symbol

    def account_wss_symbol(self, symbol: str) -> str:
        for lc in self.legal_currency:
            if lc in symbol:
                symbol = f"{symbol.split(lc)[0]}/{lc}".lower()
                break
        return symbol

    def get_period(self, key: str) -> str:
        return self.kline_periods.get(key, key)

    def get_rest_path(self, request_type: str, **kwargs) -> str:
        path = self.rest_paths.get(request_type)
        if path is None:
            raise ValueError(f"Unknown rest path: {request_type}")
        return path


class PoloniexExchangeDataSpot(PoloniexExchangeData):
    def __init__(self) -> None:
        super().__init__()
        self.exchange_name = "POLONIEX___SPOT"
        self.asset_type = "SPOT"
        self.rest_paths = {
            "get_markets": "GET /markets",
            "get_ticker": "GET /markets/{symbol}/ticker24h",
            "get_tickers": "GET /markets/ticker24h",
            "get_price": "GET /markets/{symbol}/price",
            "get_prices": "GET /markets/price",
            "get_orderbook": "GET /markets/{symbol}/orderBook",
            "get_kline": "GET /markets/{symbol}/candles",
            "get_trades": "GET /markets/{symbol}/trades",
            "get_server_time": "GET /markets/time",
            "make_order": "POST /orders",
            "cancel_order": "DELETE /orders/{id}",
            "cancel_orders": "DELETE /orders",
            "query_order": "GET /orders/{id}",
            "get_open_orders": "GET /orders",
            "get_order_history": "GET /orders/history",
            "get_deals": "GET /trades",
            "get_balance": "GET /accounts/balances",
            "get_account": "GET /accounts/balances",
            "get_config": "GET /accounts/config",
        }
        self.wss_paths = {
            "ticker": {"params": ["ticker"], "method": "SUBSCRIBE", "id": 1},
            "trades": {"params": ["trades"], "method": "SUBSCRIBE", "id": 2},
            "book": {"params": ["book"], "method": "SUBSCRIBE", "id": 3},
            "book_lv2": {"params": ["book_lv2"], "method": "SUBSCRIBE", "id": 4},
            "candles_1m": {"params": ["candles_1m"], "method": "SUBSCRIBE", "id": 5},
            "candles_5m": {"params": ["candles_5m"], "method": "SUBSCRIBE", "id": 6},
            "candles_15m": {"params": ["candles_15m"], "method": "SUBSCRIBE", "id": 7},
            "candles_30m": {"params": ["candles_30m"], "method": "SUBSCRIBE", "id": 8},
            "candles_1h": {"params": ["candles_1h"], "method": "SUBSCRIBE", "id": 9},
            "candles_4h": {"params": ["candles_4h"], "method": "SUBSCRIBE", "id": 10},
            "candles_1d": {"params": ["candles_1d"], "method": "SUBSCRIBE", "id": 11},
        }
        self.status_dict = {
            "NEW": "live",
            "PARTIALLY_FILLED": "partially_filled",
            "FILLED": "filled",
            "CANCELED": "canceled",
            "REJECTED": "rejected",
            "EXPIRED": "expired",
        }
        self.rate_limit_type = "sliding_window"
        self.interval = "1"
        self.limit = 200
        self.rate_limits = [
            {
                "name": "public",
                "type": "sliding_window",
                "interval": "1",
                "limit": 200,
                "scope": "endpoint",
            },
            {
                "name": "private",
                "type": "sliding_window",
                "interval": "1",
                "limit": 50,
                "scope": "endpoint",
            },
            {
                "name": "trade",
                "type": "sliding_window",
                "interval": "1",
                "limit": 50,
                "scope": "endpoint",
            },
        ]
        self.server_time = 0.0
        self.local_update_time = 0.0
        self.timezone = "UTC"

    def get_symbol_path(self, symbol: str) -> str:
        return symbol.replace("/", "_")

    def get_instrument_name(self, symbol: str) -> str:
        return symbol.replace("/", "_")

    def get_symbol_from_instrument(self, instrument_name: str) -> str:
        return instrument_name.replace("_", "/")

    def validate_symbol(self, symbol: str) -> bool:
        if not symbol:
            return False
        if "_" in symbol:
            parts = symbol.split("_")
            return len(parts) == 2 and len(parts[0]) > 0 and len(parts[1]) > 0
        return True

    def get_depth_levels(self, depth: int = 50) -> int:
        return min(max(1, depth), 50)

    def get_kline_period(self, period: str) -> str:
        return self.kline_periods.get(period, period)

    def get_period_from_kline(self, kline_period: str) -> str:
        return self.reverse_kline_periods.get(kline_period, kline_period)
