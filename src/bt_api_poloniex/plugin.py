from __future__ import annotations

from bt_api_base.gateway.registrar import GatewayRuntimeRegistrar
from bt_api_base.plugins.protocol import PluginInfo
from bt_api_base.registry import ExchangeRegistry

from bt_api_poloniex import __version__
from bt_api_poloniex.registry_registration import register_poloniex


def register_plugin(
    registry: type[ExchangeRegistry],
    runtime_factory: type[GatewayRuntimeRegistrar],
) -> PluginInfo:
    register_poloniex(registry)

    return PluginInfo(
        name="bt_api_poloniex",
        version=__version__,
        core_requires=">=0.15,<1.0",
        supported_exchanges=("POLONIEX___SPOT",),
        supported_asset_types=("SPOT",),
    )
