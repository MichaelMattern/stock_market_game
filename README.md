# Stock Market Game

This project simulates a stock market game built with FastAPI, Postgres, and Redis.

# Dockerized Environment:

The entire application is containerized using Docker and Docker Compose, with separate containers for the web application, PostgreSQL database, and Redis. 


## Features
Market Data Simulation:

Uses models such as Geometric Brownian Motion (for price evolution) and an Ornstein–Uhlenbeck process (for volatility) to dynamically simulate the stock’s behavior.
Simulates key metrics (price, volume, volatility, liquidity) for the HACK ticker.
Continuously updates this simulated data in Redis so all users see the same current market data.
Simulated Orderbook Generation:

Generates a simulated orderbook with separate lists of buy (bid) and sell (ask) orders based on the current market price.
Stores these orders in Redis under distinct keys (e.g., orderbook:buy:HACK and orderbook:sell:HACK).
Trade Simulation:

Randomly creates trade events (buy or sell) to mimic market activity.
Updates an “order imbalance” value in Redis that feeds back into the market simulation.

# Order Matching Engine:

Accepts user orders (both market and limit orders) through an API endpoint.
For market orders, matches and executes orders immediately using the best available price from the simulated orderbook.
For limit orders, if the specified price conditions are not met, the order is stored as pending in a persistent table.
Updates user accounts by adjusting cash balances and positions when orders are executed, and records executed trades in a trades table.
Persistent Pending Orders:

Stores pending (especially limit) orders in a dedicated database table so that they persist and can be merged with simulated liquidity for display.

# Merged Orderbook Endpoint:

Provides an endpoint that merges the simulated orderbook (from Redis) with pending user orders (from the database) into a single view.
Displays buy and sell orders in separate sections, reflecting both the simulated market liquidity and the user-submitted pending orders.

# Account Management:

An admin-protected endpoint allows for account creation (with fields for user_id, password, cash, open_positions, and profit_loss).
A user-facing endpoint lets users retrieve their account details using their user_id.
The system computes networth dynamically as the sum of cash plus the current market value of open positions (using current prices from Redis).
A background task periodically updates account metrics (like profit_loss) based on market fluctuations.

# Trade History:

Every executed trade is recorded in a persistent trades table.
A dedicated endpoint retrieves the full historic trade data for a given ticker (e.g., HACK) so users can see all market transactions.

# Admin vs. User Separation:

Admin endpoints (e.g., account creation) are protected by an API key, ensuring that only authorized personnel can create new user accounts.
Regular users have separate endpoints to view their account details and place orders.

# Background Tasks & Real-Time Updates:**

Background tasks continuously run to update market data, orderbook data, trade simulation, and dynamic account updates.
This ensures that the entire system (market data, order matching, account status) is kept current and consistent for all users.

# Leadeboard:

Displays all the users in descending order of their networth to show which team is in the lead

