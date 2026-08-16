"""Module-level docstring."""
from __future__ import annotations

import json
import time
from typing import Any

from bt_api_base.containers.tickers.ticker import TickerData
from bt_api_base.functions.utils import from_dict_get_float, from_dict_get_string


class PoloniexTickerData(TickerData):
    """Class PoloniexTickerData"""
    def __init__(
        self,
        ticker_info: Any,
        symbol_name: str,
        asset_type: str = "SPOT",
        has_been_json_encoded: bool = False,
    ) -> None:
        """__init__ method"""
        super().__init__(ticker_info, has_been_json_encoded)
        self.exchange_name = "POLONIEX"
        self.local_update_time = time.time()
        self.symbol_name = symbol_name
        self.asset_type = asset_type
        self.ticker_data: dict[str, Any] | None = (
            ticker_info if has_been_json_encoded and isinstance(ticker_info, dict) else None
        )
        self.ticker_symbol_name: str | None = None
        self.server_time: float | None = None
        self.bid_price: float | None = None
        self.ask_price: float | None = None
        self.bid_volume: float | None = None
        self.ask_volume: float | None = None
        self.last_price: float | None = None
        self.all_data: dict[str, Any] | None = None
        self.has_been_init_data = False

    def init_data(self) -> "PoloniexTickerData":
        """init_data method"""
        raise NotImplementedError

    def get_all_data(self) -> dict[str, Any]:
        """get_all_data method"""
        if self.all_data is None:
            self.init_data()
            self.all_data = {
                "exchange_name": self.exchange_name,
                "symbol_name": self.symbol_name,
                "asset_type": self.asset_type,
                "local_update_time": self.local_update_time,
                "ticker_symbol_name": self.ticker_symbol_name,
                "server_time": self.server_time,
                "bid_price": self.bid_price,
                "ask_price": self.ask_price,
                "bid_volume": self.bid_volume,
                "ask_volume": self.ask_volume,
                "last_price": self.last_price,
            }
        return self.all_data or {}

    def __str__(self) -> str:
        self.init_data()
        return str(json.dumps(self.get_all_data()))

    def __repr__(self) -> str:
        return self.__str__()

    def get_exchange_name(self) -> str:
        """get_exchange_name method"""
        return str(self.exchange_name)

    def get_local_update_time(self) -> float:
        """get_local_update_time method"""
        return float(self.local_update_time)

    def get_symbol_name(self) -> str:
        """get_symbol_name method"""
        return str(self.symbol_name)

    def get_ticker_symbol_name(self) -> str | None:
        """get_ticker_symbol_name method"""
        val = self.ticker_symbol_name
        return None if val is None else str(val)

    def get_asset_type(self) -> str:
        """get_asset_type method"""
        return str(self.asset_type)

    def get_server_time(self) -> float | None:
        """get_server_time method"""
        return self.server_time

    def get_bid_price(self) -> float | None:
        """get_bid_price method"""
        return self.bid_price

    def get_ask_price(self) -> float | None:
        """get_ask_price method"""
        return self.ask_price

    def get_bid_volume(self) -> float | None:
        """get_bid_volume method"""
        return self.bid_volume

    def get_ask_volume(self) -> float | None:
        """get_ask_volume method"""
        return self.ask_volume

    def get_last_price(self) -> float | None:
        """get_last_price method"""
        return self.last_price


class PoloniexRequestTickerData(PoloniexTickerData):
    """Class PoloniexRequestTickerData"""
    def init_data(self) -> "PoloniexRequestTickerData":
        """init_data method"""
        if not self.has_been_json_encoded:
            self.ticker_data = (
                json.loads(self.ticker_info)
                if isinstance(self.ticker_info, str)
                else self.ticker_info
            )
            self.has_been_json_encoded = True
        if self.has_been_init_data:
            return self

        data = self.ticker_data or {}
        self.ticker_symbol_name = from_dict_get_string(data, "symbol")
        self.server_time = from_dict_get_float(data, "ts") or time.time() * 1000
        self.bid_price = from_dict_get_float(data, "bid")
        self.ask_price = from_dict_get_float(data, "ask")
        self.bid_volume = from_dict_get_float(data, "bidQuantity")
        self.ask_volume = from_dict_get_float(data, "askQuantity")
        self.last_price = from_dict_get_float(data, "close")
        self.has_been_init_data = True
        return self


class PoloniexWssTickerData(PoloniexTickerData):
    """Class PoloniexWssTickerData"""
    def init_data(self) -> "PoloniexWssTickerData":
        """init_data method"""
        if not self.has_been_json_encoded:
            self.ticker_data = (
                json.loads(self.ticker_info)
                if isinstance(self.ticker_info, str)
                else self.ticker_info
            )
            self.has_been_json_encoded = True
        if self.has_been_init_data:
            return self

        data = self.ticker_data or {}
        self.ticker_symbol_name = from_dict_get_string(data, "symbol")
        self.server_time = from_dict_get_float(data, "ts") or time.time() * 1000
        self.bid_price = from_dict_get_float(data, "bid")
        self.ask_price = from_dict_get_float(data, "ask")
        self.bid_volume = from_dict_get_float(data, "bidQuantity")
        self.ask_volume = from_dict_get_float(data, "askQuantity")
        self.last_price = from_dict_get_float(data, "close")
        self.has_been_init_data = True
        return self
