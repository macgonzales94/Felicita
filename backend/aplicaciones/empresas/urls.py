from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'empresas'

# Router para ViewSets
router = DefaultRouter()
# router.register(r'empresas', EmpresaViewSet)

urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # URLs personalizadas
    # path('mi-empresa/', MiEmpresaView.as_view(), name='mi_empresa'),
    # path('validar-ruc/', ValidarRucView.as_view(), name='validar_ruc'),
]
