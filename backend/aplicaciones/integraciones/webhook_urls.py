"""
WEBHOOK URLs - PROYECTO FELICITA
URLs para webhooks de integraciones externas (NubeFact, etc.)
"""

from django.urls import path
from django.http import JsonResponse
from django.views import View

class WebhookStubView(View):
    """Vista stub para webhooks - TODO: Implementar"""
    
    def post(self, request):
        return JsonResponse({'mensaje': 'Webhook en desarrollo'})
    
    def get(self, request):
        return JsonResponse({'mensaje': 'Webhook en desarrollo'})

# URLs para webhooks
urlpatterns = [
    path('webhook/', WebhookStubView.as_view(), name='nubefact-webhook'),
]

app_name = 'integraciones'