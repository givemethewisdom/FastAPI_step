import logging

from fastapi import APIRouter

from app.models.models_price import TickerPriceModel
from app.services.dependencies import PriceServiceDep


router = APIRouter(prefix="/price", tags=["price"])

logger = logging.getLogger(__name__)


@router.get("/price/{instrument}")
async def get_price(instrument: str, price_serv: PriceServiceDep) -> TickerPriceModel:
    """получает информацию об инструменте по его названию (eth_usd, btc_usd)"""
    return await price_serv.get_ticker_serv(instrument)
