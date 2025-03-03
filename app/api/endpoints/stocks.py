# File: stock_market_game/app/api/endpoints/stocks.py
from fastapi import APIRouter, HTTPException
from app.schemas import StockData
from app.redis_client import redis_client
import json

router = APIRouter()

@router.get("/", response_model=list[StockData])
def get_stocks():
    # Retrieve the global stock data for symbol "HACK" from Redis.
    data = redis_client.get("HACK")
    if data is None:
        raise HTTPException(status_code=404, detail="Stock data not available")
    
    # Parse the JSON string into a Python dictionary.
    stock_dict = json.loads(data)
    
    # Create a StockData instance from the dictionary.
    stock = StockData(**stock_dict)
    return [stock]
