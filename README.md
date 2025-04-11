# Stock Market Game

A real-time stock market simulation game where users can trade virtual stocks, compete on a leaderboard, and experience market dynamics in a risk-free environment.

## Overview

This platform simulates a stock market with realistic price movements, order book dynamics, and trading mechanics. Users can create accounts, trade stocks, place limit orders, track their portfolio performance, and compete against other players on the leaderboard.

## Features

### Account Management
- **Create Account**: Start with initial virtual cash to begin trading
- **Account Dashboard**: View your current cash balance, open positions, and profit/loss
- **Portfolio Tracking**: Monitor the performance of your investments in real-time

### Stock Trading
- **Market Data**: View current stock prices, volatility, and trading volume
- **Place Orders**: Execute two types of orders:
  - **Market Orders**: Buy or sell stocks immediately at the current market price
  - **Limit Orders**: Set your desired price for buying or selling stocks, which execute when the market reaches that price
- **Order Management**: View and cancel your open orders

### Stock Market Data
- **Real-time Prices**: See live stock price updates
- **Historical Data**: View price history charts with different timeframes:
  - 1-minute intervals
  - 5-minute intervals
  - 15-minute intervals
  - 30-minute intervals
  - 1-hour intervals
- **Market Depth**: Access the orderbook to see buy and sell orders at different price levels

### Leaderboard
- **Competitive Rankings**: See how your trading performance compares to other players
- **Performance Metrics**: Players ranked by net worth (cash + portfolio value)

### Trade History
- **Personal Trade History**: View all your executed trades
- **Transaction Details**: See trade timestamp, stock symbol, price, quantity, and side (buy/sell)

## How to Use the Interface

### Navigation
The main interface is divided into sections, accessible from the sidebar:
- **Stocks**: View current stock prices and data
- **Stock History**: View price charts and historical data
- **My Account**: Access your account details and balance
- **Leaderboard**: Check rankings
- **Orderbook**: See market depth with buy and sell orders
- **Place Order**: Execute market or limit orders
- **My Open Orders**: Manage your pending orders
- **My Trades**: View your trade history

### Placing an Order
1. Navigate to the "Place Order" section
2. Enter your User ID
3. Select the stock symbol (e.g., "HACK")
4. Choose the order type (Market or Limit)
5. Select the side (Buy or Sell)
6. Enter the quantity
7. For limit orders, specify your desired price
8. Click "Place Order" to submit

### Viewing Stock History
1. Go to the "Stock History" section
2. Enter the stock symbol
3. Select the desired timeframe (1m, 5m, 15m, 30m, or 1h)
4. Set the number of data points to retrieve
5. Click "Get History" to view the price chart

### Managing Open Orders
1. Navigate to "My Open Orders"
2. View all your pending limit orders
3. Cancel individual orders or use "Cancel All Orders" to remove all pending orders

## API Endpoints

For developers or advanced users, the following API endpoints are available:

### Account Endpoints
- `GET /accounts/{user_id}`: Get account details
- `POST /accounts/create`: Create a new account

### Stock Endpoints
- `GET /stocks`: Get all available stocks
- `GET /stocks/{symbol}`: Get specific stock data
- `GET /stocks/{symbol}/history`: Get historical price data

### Order Endpoints
- `POST /orders`: Place a new order
- `GET /orders/pending`: Get pending limit orders for a user
- `DELETE /orders/cancel`: Cancel a pending order

### Leaderboard Endpoint
- `GET /leaderboard`: Get the current leaderboard rankings

### Trade Endpoints
- `GET /trades/my`: Get a user's trade history

### Orderbook Endpoints
- `GET /orderbook`: Get the current orderbook with buy and sell orders

## Getting Started

1. Create an account with a User ID and password
2. Log in to access the trading platform
3. Start by checking current stock prices in the "Stocks" section
4. Place your first trade in the "Place Order" section
5. Track your performance and compete on the leaderboard

## Trading Strategies

- **Market Making**: Place limit buy orders below market price and limit sell orders above market price to profit from the spread
- **Trend Following**: Analyze price charts to identify trends and trade in the direction of the trend
- **Volatility Trading**: Look for stocks with high volatility for potential larger price swings
- **Value Investing**: Buy stocks you believe are undervalued and hold for longer periods

Happy trading!

