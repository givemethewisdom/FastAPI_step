import logging

from starlette import status

from app.exceptions import CustomException
from app.models.models_price import TickerPriceModel
from app.services.cashe.rabbit_ticker_cash import RedisCache


logger = logging.getLogger(__name__)


class PriceService:
    def __init__(self, cache: RedisCache):
        self.cache = cache

    async def get_cached_price_serv(self, instrument: str):
        "get ticker from cache"
        return self.cache.get(f"ticker:{instrument}")

    async def get_ticker_serv(self, instrument: str):
        "get ticker data"
        data = await self.get_cached_price_serv(instrument)

        if not data:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ticker not found",
                message="for now its for bts_used, eth_usd",
            )

        res = TickerPriceModel(
            ticker=data["ticker"],
            price=data["price"],
            estimated_delivery_price=data["estimated_delivery_price"],
            timestamp=data["timestamp"],
        )

        return res.model_dump()
