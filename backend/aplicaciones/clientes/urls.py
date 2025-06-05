from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'clientes'

# Router para ViewSets
router = DefaultRouter()
# router.register(r'clientes', ClienteViewSet)
# router.register(r'contactos', ContactoClienteViewSet)

urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # URLs personalizadas
    # path('buscar/', BuscarClienteView.as_view(), name='buscar'),
    # path('validar-documento/', ValidarDocumentoView.as_view(), name='validar_documento'),
    # path('importar/', ImportarClientesView.as_view(), name='importar'),
]