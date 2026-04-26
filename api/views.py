from rest_framework.views import APIView
from rest_framework.response import Response
from .services import get_optimal_fuel_route

class FuelOptimizerView(APIView):
    def get(self, request):
        start = request.query_params.get('start')
        finish = request.query_params.get('finish')
        
        if not start or not finish:
            return Response({"error": "Missing start or finish location"}, status=400)
            
        try:
            data = get_optimal_fuel_route(start, finish)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)