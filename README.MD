Fuel Route Optimizer API
A robust Django REST API that calculates the most cost-effective fuel stops for a long-distance trip. This project specifically optimizes routes between New York and Miami (or any US route) based on a 10 MPG fuel efficiency and a 500-mile vehicle range.

🛠️ Tech Stack
Backend: Django, Django REST Framework

External API: OpenRouteService (Directions V2)

Data Analysis: Pandas

Database: SQLite

🚀 Key Features & Logic
Dynamic Routing: Uses real-time map data to calculate distances and generate route polylines.

Cost Optimization: Due to the source CSV lacking GPS coordinates, I implemented a State-Based Corridor Filter. The algorithm identifies the states along the route (e.g., NY, NJ, VA, NC, GA, FL) and selects the most competitive fuel prices from those specific regions.

10 MPG Math: Automatically calculates the total trip cost based on the requirement of 10 miles per gallon.

Resiliency: Built-in retry logic to handle potential 502/504 errors from external map providers.

📦 Installation & Setup
1. Prerequisites
Ensure you have Python 3.10+ installed.

2. Environment Setup
Bash
# Clone the repository
cd fuel_optimizer_project

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
3. Database & Data Ingestion
You must import the provided fuel station CSV into the local database before the API will return stops.

Bash
# Run migrations
python manage.py migrate

# Run the custom import command
python manage.py shell -c "import pandas as pd; from api.models import FuelStation; df = pd.read_csv('fuel-prices-for-be-assessment.csv'); FuelStation.objects.all().delete(); stations = [FuelStation(name=r['Truckstop Name'], address=r['Address'], city=r['City'], state=r['State'], price=float(r['Retail Price']), latitude=0.0, longitude=0.0) for _, r in df.iterrows()]; FuelStation.objects.bulk_create(stations); print(f'Successfully loaded {FuelStation.objects.count()} stations')"
🧪 API Usage
Endpoint: GET /api/optimize/

Query Parameters:

start: (Optional) Starting location. Default: New York, NY

finish: (Optional) Destination. Default: Miami, FL

Example Request:
http://127.0.0.1:8000/api/optimize/?start=New York,NY&finish=Miami,FL

Example Response:
JSON
{
    "total_distance": 1290.15,
    "total_cost": 367.21,
    "fuel_efficiency": "10 MPG",
    "stops": [
        {
            "name": "SHEETZ #512",
            "address": "I-40, EXIT 203 & SR-66, Kernersville, NC",
            "price": 2.84
        }
    ],
    "map_polyline": [[-74.006, 40.712], ...]
}
📁 Project Structure
api/services.py: The "Brain" of the app. Handles external API calls and fuel cost logic.

api/models.py: Defines the FuelStation schema for SQLite.

api/views.py: Handles the GET request and input parameters.

.gitignore: Configured to exclude venv and __pycache__ for a clean submission.