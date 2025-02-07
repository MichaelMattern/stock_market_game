# File: stock_market_game/app/main.py
from fastapi import FastAPI
from app.api.endpoints import stocks, accounts, leaderboard, orderbook, orders, admin_accounts, trades
from app.tasks.background_tasks import start_background_tasks

app = FastAPI(title="Stock Market Game")

app.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(orderbook.router, prefix="/orderbook", tags=["Orderbook"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(admin_accounts.router, prefix="/admin/accounts", tags=["Admin Accounts"])
app.include_router(trades.router, prefix="/trades", tags=["Trades"])

@app.on_event("startup")
async def startup_event():
    start_background_tasks()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
