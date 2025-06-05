from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'configuraciones'

# Router para ViewSets
router = DefaultRouter()
# router.register(r'configuraciones', ConfiguracionViewSet)
# router.register(r'parametros', ParametroSistemaViewSet)

urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # URLs personalizadas
    # path('empresa/', ConfiguracionEmpresaView.as_view(), name='empresa'),
    # path('sistema/', ConfiguracionSistemaView.as_view(), name='sistema'),
    # path('backup/', BackupView.as_view(), name='backup'),
]