# Telegram Currency & Crypto Tracking Bot

An asynchronous Telegram bot built with Python and aiogram 3 for real-time cryptocurrency and fiat currency monitoring, featuring an interactive FSM currency converter.

## Features
- **Real-Time Crypto Tracking:** Fetches live prices for BTC, ETH, and SOL using the CoinGecko API.
- **Official Exchange Rates:** Displays USD and EUR rates from the National Bank of Ukraine (NBU) API.
- **FSM-Powered Calculator:** Fast interactive currency conversion between USD, UAH, and Bitcoin (with satoshi breakdown).
- **Asynchronous & Non-Blocking:** Utilizes `httpx.AsyncClient` with `asyncio` for smooth concurrent requests.
- **Secure Configuration:** Environment variables managed via `python-dotenv`.

## Tech Stack
- **Language:** Python 3.11+
- **Framework:** aiogram 3.x
- **Networking:** httpx, asyncio
- **Environment Management:** python-dotenv

## Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Denisskam/telegram-crypto-tracker-bot.git](https://github.com/Denisskam/telegram-crypto-tracker-bot.git)
   cd telegram-crypto-tracker-bot
