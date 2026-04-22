from __future__ import annotations

from typing import Any

from bt_api_base.balance_utils import nested_balance_handler as _poloniex_balance_handler
from bt_api_base.registry import ExchangeRegistry

from bt_api_poloniex.exchange_data import PoloniexExchangeDataSpot
from bt_api_poloniex.feeds.live_poloniex.spot import PoloniexRequestDataSpot


def _poloniex_spot_subscribe_handler(
    data_queue: Any,
    exchange_params: Any,
    topics: Any,
    bt_api: Any,
) -> None:
    topic_list = [i["topic"] for i in topics]
    bt_api.log(f"Poloniex Spot topics requested: {topic_list}")


def register_poloniex(registry: type[ExchangeRegistry]) -> None:
    registry.register_feed("POLONIEX___SPOT", PoloniexRequestDataSpot)
    registry.register_exchange_data("POLONIEX___SPOT", PoloniexExchangeDataSpot)
    registry.register_balance_handler("POLONIEX___SPOT", _poloniex_balance_handler)
    registry.register_stream("POLONIEX___SPOT", "subscribe", _poloniex_spot_subscribe_handler)
