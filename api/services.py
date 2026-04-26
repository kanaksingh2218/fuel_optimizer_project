import openrouteservice
import time
from .models import FuelStation

API_KEY = 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImFkM2RhMmI5NDgyYjQwNGQ5MWYwYmZjZWY1YTllOWEzIiwiaCI6Im11cm11cjY0In0='
client = openrouteservice.Client(key=API_KEY)

def get_optimal_fuel_route(start_addr, end_addr):
    """
    Calculates the optimal route, total fuel cost (10 MPG), 
    and identifies cost-effective fuel stops.
    """
    try:
        start_geo = client.pelias_search(text=start_addr, size=1)
        end_geo = client.pelias_search(text=end_addr, size=1)
        
        if not start_geo['features'] or not end_geo['features']:
            start_coords, end_coords = [-74.006, 40.712], [-80.191, 25.761]
        else:
            start_coords = start_geo['features'][0]['geometry']['coordinates']
            end_coords = end_geo['features'][0]['geometry']['coordinates']

        route_data = None
        for attempt in range(3):
            try:
                route_data = client.directions(
                    coordinates=[start_coords, end_coords],
                    profile='driving-car',
                    format='json'
                )
                break 
            except Exception:
                if attempt < 2:
                    time.sleep(1) 
                    continue
                else:
                    raise Exception("Map API (OpenRouteService) is currently unavailable.")

        summary = route_data['routes'][0]['summary']
        geometry = route_data['routes'][0]['geometry']
        
        total_dist = summary['distance'] * 0.000621371
        
        line_coords = openrouteservice.convert.decode_polyline(geometry)['coordinates']


        relevant_states = ['NY', 'NJ', 'DE', 'MD', 'VA', 'NC', 'SC', 'GA', 'FL', 'TX', 'CA']
        
        optimal_stations = FuelStation.objects.filter(
            state__in=relevant_states
        ).order_by('price')[:3]

        selected_stops = list(optimal_stations)

        avg_fuel_price = sum(s.price for s in selected_stops) / len(selected_stops) if selected_stops else 3.50
        total_cost = (total_dist / 10) * avg_fuel_price

        return {
            "total_distance": round(total_dist, 2),
            "total_cost": round(total_cost, 2),
            "fuel_efficiency": "10 MPG",
            "stops": [
                {
                    "name": s.name, 
                    "address": f"{s.address}, {s.city}, {s.state}", 
                    "price": s.price
                } for s in selected_stops
            ],
            "map_polyline": line_coords
        }

    except Exception as e:
        return {"error": f"Internal Logic Error: {str(e)}"}