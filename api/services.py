import openrouteservice
from geopy.distance import geodesic
from .models import FuelStation

def get_optimal_fuel_route(start_addr, end_addr):
    # REPLACE WITH YOUR ACTUAL KEY
    client = openrouteservice.Client(key='YOUR_ORS_API_KEY')
    
    # 1. Single API call for the route
    coords = [
        client.pelias_search(text=start_addr)['features'][0]['geometry']['coordinates'],
        client.pelias_search(text=end_addr)['features'][0]['geometry']['coordinates']
    ]
    
    route_res = client.directions(coordinates=coords, profile='driving-car', format='geojson')
    geometry = route_res['features'][0]['geometry']['coordinates'] # [lon, lat]
    total_dist_miles = route_res['features'][0]['properties']['summary']['distance'] / 1609.34
    
    # 2. Optimization Algorithm
    selected_stops = []
    total_cost = 0
    current_pos = (coords[0][1], coords[0][0]) # lat, lon
    miles_remaining = total_dist_miles
    mpg = 10
    max_range = 500

    # Greedy approach: Find the cheapest stop in the next 500 miles
    while miles_remaining > max_range:
        # Get all stations in the DB
        # Optimization: In a real app, use a bounding box query here
        reachable = [s for s in FuelStation.objects.all() if geodesic(current_pos, (s.latitude, s.longitude)).miles <= max_range]
        
        if not reachable:
            break
            
        best_stop = min(reachable, key=lambda x: x.price)
        dist_to_stop = geodesic(current_pos, (best_stop.latitude, best_stop.longitude)).miles
        
        total_cost += (dist_to_stop / mpg) * best_stop.price
        selected_stops.append({
            "name": best_stop.name,
            "address": f"{best_stop.address}, {best_stop.city}, {best_stop.state}",
            "price": best_stop.price
        })
        
        current_pos = (best_stop.latitude, best_stop.longitude)
        miles_remaining -= dist_to_stop

    # Final cost to destination
    if selected_stops:
        total_cost += (miles_remaining / mpg) * selected_stops[-1]['price']
    else:
        total_cost = (total_dist_miles / mpg) * 3.50 # default if no stops needed

    return {
        "total_distance": round(total_dist_miles, 2),
        "total_fuel_cost": round(total_cost, 2),
        "fuel_stops": selected_stops,
        "map_polyline": geometry
    }