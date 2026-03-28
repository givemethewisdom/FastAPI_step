from datetime import datetime

from pydantic import BaseModel, computed_field


class TickerPriceModel(BaseModel):
    ticker: str  # btc_usd eth_usd
    price: float
    estimated_delivery_price: float
    timestamp: int  # Unix timestamp в секундах

    @computed_field
    @property
    def datetime_iso(self) -> str:
        # считаю что api должно отдавать timestamp но сделал для удобства отладки
        """ISO формат: 2026-03-25 12:08:44"""
        dt = datetime.fromtimestamp(self.timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
