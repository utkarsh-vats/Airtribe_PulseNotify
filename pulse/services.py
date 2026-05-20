import requests
import logging
import random
from django.conf import settings
from django.core.cache import cache
from .mock_data import MOCK_PRICES

logger = logging.getLogger(__name__)

API_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"

# get_price(origin, destination)
    # 1. check redis cache (TTL: 30min)
        # >  HIT --> return cached price
    # 2. call api
        # > success --> cache in redis --> return price
    # 3. fallback to mock_data.py
        # > return mock price (app never breaks)
class PriceService:
    def get_price(self, origin, destination) -> float | None:
        cache_key = f"flight_price:{origin}:{destination}"
        try:
            route_price = cache.get(cache_key)
            if route_price:
                logger.debug(f"Price fetched from cache for {origin}-{destination}: {route_price}")
                return route_price
        except Exception as e:
            logger.error(f"Error fetching price from cache: {e}")
        try:
            route_price = self._fetch_from_api(origin, destination)
            if route_price:
                cache.set(cache_key, route_price, timeout=1800)
                logger.debug(f"Price fetched from API for {origin}-{destination}: {route_price}")
                return route_price
        except Exception as e:
            logger.error(f"Error fetching price from API: {e}")
        try:
            route_price = self._fetch_from_mock(origin, destination)
            if route_price:
                return route_price
        except Exception as e:
            logger.error(f"Error fetching price from mock data: {e}")
        return None


    def _fetch_from_api(self, origin, destination):
        params = {
            'origin': origin,
            'destination': destination,
            'currency': 'inr',
            'sorting': 'price',
            'limit': 1,
            'unique': 'true'
        }
        headers = {
            'X-Access-Token': settings.TRAVELPAYOUTS_API_TOKEN
        }
        try:
            response = requests.get(API_URL, params=params, headers=headers, timeout=10)
            response_data = response.json()
            
            if response_data.get("success") and response_data.get("data"):
                return response_data["data"][0]["price"]
        except (requests.RequestException, KeyError, IndexError) as e:
            logger.warning(f"API fetch failed for {origin}-{destination}: {e}")
        
        return None


    def _fetch_from_mock(self, origin, destination):
        price_range = MOCK_PRICES.get(f"{origin}-{destination}")
        if price_range:
            return random.randint(*price_range)
        return None
