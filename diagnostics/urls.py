from django.urls import path
from .views import AnalyzeDTCView

urlpatterns = [
    path('analyze/', AnalyzeDTCView.as_view(), name='analyze_dtc'),
]