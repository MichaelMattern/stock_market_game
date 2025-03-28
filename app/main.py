# File: stock_market_game/app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.api.endpoints import stocks, accounts, leaderboard, orderbook, orders, admin_accounts, trades, stock_history, admin_stats
from app.tasks.background_tasks import start_background_tasks
import logging
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Stock Market Game API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    path = request.url.path
    logging.info(f"Request: {request.method} {path}")
    
    # Log auth headers (sanitized)
    auth_header = request.headers.get("Authorization")
    if auth_header:
        if auth_header.startswith("Basic "):
            logging.info("Authorization: Basic [REDACTED]")
        else:
            logging.info(f"Authorization: {auth_header[:10]}... [REDACTED]")
    
    admin_key = request.headers.get("x-admin-api-key")
    if admin_key:
        logging.info("x-admin-api-key: [REDACTED]")
        
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response

# Add a root endpoint that redirects to index.html
@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

# First include all API routers - these take precedence over static files
app.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
app.include_router(stock_history.router, prefix="/stocks", tags=["Stock History"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(orderbook.router, prefix="/orderbook", tags=["Orderbook"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(admin_accounts.router, prefix="/admin/accounts", tags=["Admin Accounts"], include_in_schema=False)
app.include_router(admin_stats.router, prefix="/admin", tags=["Admin Stats"], include_in_schema=False)
app.include_router(trades.router, prefix="/trades", tags=["Trades"])

# Mount static files last, so they don't override API routes
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def startup_event():
    logging.info("Starting Stock Market Game application")
    start_background_tasks()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
