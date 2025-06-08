"""
URLS FACTURACION - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

URLs para el módulo de facturación
"""

from django.urls import path
from django.http import JsonResponse
from django.views import View

class FacturacionStubView(View):
    """Vista stub para facturación - TODO: Implementar"""
    
    def get(self, request):
        return JsonResponse({'mensaje': 'Módulo de facturación en desarrollo'})
    
    def post(self, request):
        return JsonResponse({'mensaje': 'Módulo de facturación en desarrollo'})

# URLs para facturación
urlpatterns = [
    path('', FacturacionStubView.as_view(), name='facturacion-home'),
    path('facturas/', FacturacionStubView.as_view(), name='facturas-list'),
    path('boletas/', FacturacionStubView.as_view(), name='boletas-list'),
    path('notas-credito/', FacturacionStubView.as_view(), name='notas-credito-list'),
    path('notas-debito/', FacturacionStubView.as_view(), name='notas-debito-list'),
]

app_name = 'facturacion'