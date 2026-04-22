from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

from bt_api_base.containers.requestdatas.request_data import RequestData
from bt_api_base.feeds.capability import Capability
from bt_api_base.feeds.feed import Feed
from bt_api_base.logging_factory import get_logger
from bt_api_base.rate_limiter import RateLimiter, RateLimitRule

from bt_api_poloniex.containers.balances import PoloniexRequestBalanceData
from bt_api_poloniex.containers.orders import PoloniexRequestOrderData
from bt_api_poloniex.exchange_data import PoloniexExchangeDataSpot
from bt_api_poloniex.tickers import PoloniexRequestTickerData, PoloniexWssTickerData


class PoloniexRequestData(Feed, RequestData):
    @classmethod
    def _capabilities(cls) -> set[Capability]:
        return {
            Capability.GET_TICK,
            Capability.GET_DEPTH,
            Capability.GET_KLINE,
            Capability.MAKE_ORDER,
            Capability.CANCEL_ORDER,
            Capability.QUERY_ORDER,
            Capability.QUERY_OPEN_ORDERS,
            Capability.GET_DEALS,
            Capability.GET_BALANCE,
            Capability.GET_ACCOUNT,
            Capability.GET_EXCHANGE_INFO,
            Capability.GET_SERVER_TIME,
        }

    def __init__(self, data_queue: Any = None, **kwargs: Any) -> None:
        super().__init__(data_queue, **kwargs)
        self.public_key = kwargs.get("public_key") or kwargs.get("api_key")
        self.private_key = (
            kwargs.get("private_key") or kwargs.get("secret_key") or kwargs.get("api_secret")
        )
        self.asset_type = kwargs.get("asset_type", "spot")
        self.exchange_name = "POLONIEX"
        self.logger_name = kwargs.get("logger_name", "poloniex_feed.log")
        self._params = PoloniexExchangeDataSpot()
        self.request_logger = get_logger("request")
        self.async_logger = get_logger("async_request")
        self._rate_limiter = kwargs.get("rate_limiter", self._create_default_rate_limiter())

    @staticmethod
    def _create_default_rate_limiter():
        return RateLimiter(
            rules=[
                RateLimitRule(
                    name="poloniex_public",
                    type="request_count",
                    interval=1,
                    limit=200,
                    scope="ip",
                ),
                RateLimitRule(
                    name="poloniex_private",
                    type="request_count",
                    interval=1,
                    limit=50,
                    scope="ip",
                ),
            ],
        )

    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        if self.private_key is None:
            return ""
        sign_str = f"{timestamp}{method}{path}{body}"
        signature = hmac.new(
            self.private_key.encode(),
            sign_str.encode(),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _build_auth_headers(self, method: str, path: str, body: str = "") -> dict:
        timestamp = str(int(time.time()))
        signature = self._generate_signature(timestamp, method, path, body)
        headers = {"Content-Type": "application/json"}
        if self.public_key is not None:
            headers["Key"] = self.public_key
            headers["Sign"] = signature
        return headers

    @staticmethod
    def _extract_data_normalize_function(input_data, extra_data):
        if input_data is None:
            return [], False
        if isinstance(input_data, dict):
            return [input_data], True
        if isinstance(input_data, list):
            return input_data, True
        return [], False

    def request(self, path, params=None, body=None, extra_data=None, timeout=10):
        if params is None:
            params = {}
        headers = self._build_auth_headers("GET" if body is None else "POST", path, body or "")
        url = f"{self._params.rest_url}{path}"
        return self._http_client.request(
            "GET" if body is None else "POST",
            url,
            params=params,
            json=body,
            headers=headers,
            timeout=timeout,
            rate_limiter=self._rate_limiter,
        )

    def async_request(self, path, params=None, body=None, extra_data=None, timeout=10):
        if params is None:
            params = {}
        headers = self._build_auth_headers("GET" if body is None else "POST", path, body or "")
        url = f"{self._params.rest_url}{path}"
        return self._http_client.async_request(
            "GET" if body is None else "POST",
            url,
            params=params,
            json=body,
            headers=headers,
            timeout=timeout,
            rate_limiter=self._rate_limiter,
        )

    def async_callback(self, response, extra_data=None):
        return response
