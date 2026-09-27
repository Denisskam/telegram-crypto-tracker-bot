import asyncio
import httpx

NBU_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"


async def get_crypto(client: httpx.AsyncClient) -> dict | None:
    try:
        response = await client.get(COINGECKO_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "BTC": data["bitcoin"]["usd"],
                "ETH": data["ethereum"]["usd"],
                "SOL": data["solana"]["usd"],
            }
        return None
    except Exception as e:
        print(f"Error obtaining crypt: {e}")
        return None


async def get_fiat(client: httpx.AsyncClient) -> dict | None:
    try:
        response = await client.get(NBU_URL, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            fiat_rate = {}
            for item in data:
                if item["cc"] in ["USD", "EUR"]:
                    fiat_rate[item["cc"]] = round(item["rate"], 2)
            return fiat_rate
        return None
    except Exception as e:
        print(f"Error getting fiat: {e}")
        return None


async def get_all_rates():

    async with httpx.AsyncClient() as client:
        crypto_prices, fiat_rates = await asyncio.gather(
            get_crypto(client),
            get_fiat(client),
        )
    return crypto_prices, fiat_rates