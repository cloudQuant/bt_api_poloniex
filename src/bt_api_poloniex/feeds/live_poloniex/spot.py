from __future__ import annotations

from typing import Any

from bt_api_base.functions.utils import update_extra_data
from bt_api_base.logging_factory import get_logger

from bt_api_poloniex.containers.balances import PoloniexRequestBalanceData
from bt_api_poloniex.containers.orders import PoloniexRequestOrderData
from bt_api_poloniex.feeds.live_poloniex import PoloniexRequestData
from bt_api_poloniex.tickers import PoloniexRequestTickerData


class PoloniexRequestDataSpot(PoloniexRequestData):
    def __init__(self, data_queue: Any = None, **kwargs: Any) -> None:
        kwargs["asset_type"] = "spot"
        kwargs.setdefault("logger_name", "poloniex_spot_feed.log")
        super().__init__(data_queue, **kwargs)
        self._params = self._params
        self.request_logger = get_logger("request")
        self.async_logger = get_logger("async_request")

    def _get_ticker(self, symbol, extra_data=None, **kwargs) -> Any:
        request_symbol = self._params.get_symbol(symbol)
        path = f"/markets/{request_symbol}/ticker24h"
        extra_data = update_extra_data(
            extra_data,
            request_type="get_ticker",
            symbol_name=symbol,
            exchange_name=self.exchange_name,
            asset_type=self.asset_type,
            normalize_function=PoloniexRequestDataSpot._get_ticker_normalize_function,
        )
        return path, {}, extra_data

    @staticmethod
    def _get_ticker_normalize_function(input_data, extra_data):
        if input_data is None:
            return [], False
        if isinstance(input_data, dict):
            ticker_data = input_data.get("data") or input_data
            return [
                PoloniexRequestTickerData(
                    ticker_data,
                    extra_data["symbol_name"],
                    extra_data["asset_type"],
                    True,
                ),
            ], True
        return [], False

    def get_ticker(self, symbol, extra_data=None, **kwargs) -> Any:
        path, params, extra_data = self._get_ticker(symbol, extra_data, **kwargs)
        return self.request(path, params=params, extra_data=extra_data)

    def get_tick(self, symbol, extra_data=None, **kwargs) -> Any:
        return self.get_ticker(symbol, extra_data=extra_data, **kwargs)

    def async_get_ticker(self, symbol, extra_data=None, **kwargs) -> None:
        path, params, extra_data = self._get_ticker(symbol, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def async_get_tick(self, symbol, extra_data=None, **kwargs) -> None:
        self.async_get_ticker(symbol, extra_data=extra_data, **kwargs)

    def _get_balance(self, extra_data=None, **kwargs) -> Any:
        path = "/accounts/balances"
        extra_data = update_extra_data(
            extra_data,
            request_type="get_balance",
            symbol_name="ALL",
            exchange_name=self.exchange_name,
            asset_type=self.asset_type,
            normalize_function=PoloniexRequestDataSpot._get_balance_normalize_function,
        )
        return path, {}, extra_data

    @staticmethod
    def _get_balance_normalize_function(input_data, extra_data):
        if input_data is None:
            return [], False
        if isinstance(input_data, dict):
            data = input_data.get("data", [])
            result = [
                PoloniexRequestBalanceData(item, extra_data["asset_type"], True) for item in data
            ]
            return result, True
        return [], False

    def get_balance(self, extra_data=None, **kwargs) -> Any:
        path, params, extra_data = self._get_balance(extra_data, **kwargs)
        return self.request(path, params=params, extra_data=extra_data)

    def get_account(self, symbol=None, extra_data=None, **kwargs) -> Any:
        return self.get_balance(extra_data=extra_data, **kwargs)

    def async_get_balance(self, extra_data=None, **kwargs) -> None:
        path, params, extra_data = self._get_balance(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _make_order(
        self,
        symbol,
        vol,
        price=None,
        order_type="buy-limit",
        client_order_id=None,
        extra_data=None,
        **kwargs,
    ):
        request_symbol = self._params.get_symbol(symbol)
        path = "/orders"
        side, otype = order_type.split("-") if "-" in order_type else (order_type, "limit")
        body = {
            "symbol": request_symbol,
            "side": side.upper(),
            "type": otype.upper(),
            "quantity": str(vol),
        }
        if price is not None:
            body["price"] = str(price)
        if client_order_id:
            body["clientOrderId"] = str(client_order_id)
        extra_data = update_extra_data(
            extra_data,
            request_type="make_order",
            symbol_name=symbol,
            exchange_name=self.exchange_name,
            asset_type=self.asset_type,
            normalize_function=PoloniexRequestDataSpot._make_order_normalize_function,
        )
        return path, body, extra_data

    @staticmethod
    def _make_order_normalize_function(input_data, extra_data):
        if input_data is None:
            return [], False
        if isinstance(input_data, dict):
            data = input_data.get("data", {})
            return [
                PoloniexRequestOrderData(
                    data,
                    extra_data["symbol_name"],
                    extra_data["asset_type"],
                    True,
                ),
            ], True
        return [], False

    def make_order(
        self,
        symbol,
        vol,
        price=None,
        order_type="buy-limit",
        client_order_id=None,
        extra_data=None,
        **kwargs,
    ):
        path, body, extra_data = self._make_order(
            symbol,
            vol,
            price,
            order_type,
            client_order_id,
            extra_data,
            **kwargs,
        )
        return self.request(path, body=body, extra_data=extra_data)

    def async_make_order(
        self,
        symbol,
        vol,
        price=None,
        order_type="buy-limit",
        client_order_id=None,
        extra_data=None,
        **kwargs,
    ) -> None:
        path, body, extra_data = self._make_order(
            symbol,
            vol,
            price,
            order_type,
            client_order_id,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _cancel_order(
        self,
        symbol,
        order_id=None,
        client_order_id=None,
        extra_data=None,
        **kwargs,
    ) -> Any:
        path = f"/orders/{order_id or client_order_id}"
        extra_data = update_extra_data(
            extra_data,
            request_type="cancel_order",
            order_id=order_id or client_order_id,
            symbol_name=symbol,
            exchange_name=self.exchange_name,
            asset_type=self.asset_type,
            normalize_function=None,
        )
        return path, {}, extra_data

    def cancel_order(self, symbol, order_id=None, client_order_id=None, extra_data=None, **kwargs):
        path, params, extra_data = self._cancel_order(
            symbol,
            order_id,
            client_order_id,
            extra_data,
            **kwargs,
        )
        return self.request(path, params=params, extra_data=extra_data)

    def _query_order(
        self,
        symbol,
        order_id=None,
        client_order_id=None,
        extra_data=None,
        **kwargs,
    ) -> Any:
        path = f"/orders/{order_id or client_order_id}"
        extra_data = update_extra_data(
            extra_data,
            request_type="query_order",
            order_id=order_id or client_order_id,
            symbol_name=symbol,
            exchange_name=self.exchange_name,
            asset_type=self.asset_type,
            normalize_function=PoloniexRequestDataSpot._query_order_normalize_function,
        )
        return path, {}, extra_data

    @staticmethod
    def _query_order_normalize_function(input_data, extra_data):
        if input_data is None:
            return [], False
        if isinstance(input_data, dict):
            data = input_data.get("data", {})
            return [
                PoloniexRequestOrderData(
                    data,
                    extra_data["symbol_name"],
                    extra_data["asset_type"],
                    True,
                ),
            ], True
        return [], False

    def query_order(self, symbol, order_id=None, client_order_id=None, extra_data=None, **kwargs):
        path, params, extra_data = self._query_order(
            symbol,
            order_id,
            client_order_id,
            extra_data,
            **kwargs,
        )
        return self.request(path, params=params, extra_data=extra_data)

    def _get_kline(self, symbol, period="1m", limit=100, extra_data=None, **kwargs) -> Any:
        request_symbol = self._params.get_symbol(symbol)
        request_period = self._params.get_period(period)
        path = f"/markets/{request_symbol}/candles"
        params = {"interval": request_period, "limit": limit}
        extra_data = update_extra_data(
            extra_data,
            request_type="get_kline",
            symbol_name=symbol,
            exchange_name=self.exchange_name,
            asset_type=self.asset_type,
            normalize_function=PoloniexRequestData._extract_data_normalize_function,
        )
        return path, params, extra_data

    def get_kline(self, symbol, period="1m", limit=100, extra_data=None, **kwargs) -> Any:
        path, params, extra_data = self._get_kline(symbol, period, limit, extra_data, **kwargs)
        return self.request(path, params=params, extra_data=extra_data)

    def async_get_kline(self, symbol, period="1m", limit=100, extra_data=None, **kwargs) -> None:
        path, params, extra_data = self._get_kline(symbol, period, limit, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def get_server_time(self, extra_data=None, **kwargs) -> Any:
        path = "/markets/time"
        extra_data = update_extra_data(
            extra_data,
            request_type="get_server_time",
            symbol_name="ALL",
            exchange_name=self.exchange_name,
            asset_type=self.asset_type,
            normalize_function=PoloniexRequestData._extract_data_normalize_function,
        )
        return self.request(path, params={}, extra_data=extra_data)
