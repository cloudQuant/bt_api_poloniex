from unittest.mock import AsyncMock

import pytest
from bt_api_base.containers.requestdatas.request_data import RequestData

from bt_api_poloniex.feeds.live_poloniex import PoloniexRequestData


def test_poloniex_defaults_exchange_name() -> None:
    request_data = PoloniexRequestData(public_key="public-key", private_key="secret-key")

    assert request_data.exchange_name == "POLONIEX"


@pytest.mark.asyncio
async def test_poloniex_async_request_allows_missing_extra_data(monkeypatch) -> None:
    request_data = PoloniexRequestData(
        public_key="public-key",
        private_key="secret-key",
        exchange_name="POLONIEX___SPOT",
    )

    async_request_mock = AsyncMock(return_value={"code": 200, "data": []})
    monkeypatch.setattr(request_data, "async_http_request", async_request_mock)

    result = await request_data.async_request("GET /markets/BTC_USDT/ticker24h")

    assert isinstance(result, RequestData)
    assert result.get_extra_data() == {}
    assert result.get_input_data() == {"code": 200, "data": []}
