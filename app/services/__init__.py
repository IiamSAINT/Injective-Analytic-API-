"""
Services package
"""
from app.services.injective_client import get_injective_client, InjectiveClient
from app.services.market_service import get_market_service, MarketService
from app.services.analytics_service import get_analytics_service, AnalyticsService
from app.services.ninja_service import get_ninja_service, NinjaService
from app.services.supply_service import get_supply_service, SupplyService
from app.services.wallet_service import convert_address, evm_to_injective, injective_to_evm, cosmos_to_injective
