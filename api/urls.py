from django.urls import path
from .views import FuelOptimizerView

urlpatterns = [
    path('optimize/', FuelOptimizerView.as_view(), name='fuel-optimize'),
]