import pandas as pd
import time
from django.core.management.base import BaseCommand
from api.models import FuelStation
from geopy.geocoders import Nominatim

class Command(BaseCommand):
    def handle(self, *args, **options):
        df = pd.read_csv('fuel-prices-for-be-assessment.csv')
        geolocator = Nominatim(user_agent="fuel_v1")
        city_cache = {}

        self.stdout.write("Geocoding cities... please wait.")
        for _, row in df.iterrows():
            loc_key = f"{row['City'].strip()}, {row['State'].strip()}, USA"
            if loc_key not in city_cache:
                try:
                    loc = geolocator.geocode(loc_key)
                    if loc:
                        city_cache[loc_key] = (loc.latitude, loc.longitude)
                        time.sleep(1) # Rate limit
                except: continue
            
            coords = city_cache.get(loc_key)
            if coords:
                FuelStation.objects.create(
                    name=row['Truckstop Name'], address=row['Address'],
                    city=row['City'], state=row['State'],
                    price=row['Retail Price'], latitude=coords[0], longitude=coords[1]
                )
        self.stdout.write("Import complete!")