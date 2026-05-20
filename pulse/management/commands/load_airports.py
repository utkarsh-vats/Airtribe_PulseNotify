from typing import Any
import requests
from django.core.management.base import BaseCommand
from pulse.models import Airport

API_URL = "https://api.travelpayouts.com/data/en/"
AIRPORT_URL = API_URL + "airports.json"
CITIES_URL = API_URL + "cities.json"
COUNTRIES_URL = API_URL + "countries.json"

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        try:
            airports = requests.get(AIRPORT_URL, timeout=30).json()
            cities = requests.get(CITIES_URL, timeout=30).json()
            countries = requests.get(COUNTRIES_URL, timeout=30).json()
        except Exception as e:
            self.stdout.write(f"Error fetching data from {API_URL}: {e}")
            exit(1)

        city_lookup = {city["code"]: city["name"] for city in cities}
        country_lookup = {country["code"]: country["name"] for country in countries}

        count = 0
        for airport in airports:
            if airport.get("iata_type") != "airport":
                continue
            Airport.objects.update_or_create(
                code=airport["code"],
                defaults={
                    "name": airport.get("name", ""),
                    "city": city_lookup.get(airport["city_code"], airport["city_code"]),
                    "country": country_lookup.get(airport["country_code"], airport["country_code"]),
                    "timezone": airport.get("timezone", "")
                }
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Successfully loaded {count} airports"))
        

