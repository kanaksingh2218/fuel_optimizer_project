import pandas as pd
import time
from django.core.management.base import BaseCommand
from api.models import FuelStation
from geopy.geocoders import Nominatim

class Command(BaseCommand):
    help = 'Imports fuel prices and geocodes city/state coordinates'

    def handle(self, *args, **options):
        df = pd.read_csv('fuel-prices-for-be-assessment.csv')
        geolocator = Nominatim(user_agent="fuel_optimizer_v1")
        city_cache = {}

        self.stdout.write("Starting import... (This geocodes locations for speed)")
        
        for _, row in df.iterrows():
            location_key = f"{row['City'].strip()}, {row['State'].strip()}, USA"
            
            if location_key not in city_cache:
                try:
                    loc = geolocator.geocode(location_key)
                    if loc:
                        city_cache[location_key] = (loc.latitude, loc.longitude)
                        time.sleep(1) # Respect rate limits
                except:
                    continue
            
            coords = city_cache.get(location_key)
            if coords:
                FuelStation.objects.create(
                    name=row['Truckstop Name'],
                    address=row['Address'],
                    city=row['City'],
                    state=row['State'],
                    price=row['Retail Price'],
                    latitude=coords[0],
                    longitude=coords[1]
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported fuel data'))