from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'contabilidad'

# Router para ViewSets
router = DefaultRouter()
# router.register(r'plan-cuentas', PlanCuentasViewSet)
# router.register(r'asientos', AsientoContableViewSet)
# router.register(r'cuentas-por-cobrar', CuentaPorCobrarViewSet)

urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # URLs personalizadas
    # path('balance-general/', BalanceGeneralView.as_view(), name='balance_general'),
    # path('estado-resultados/', EstadoResultadosView.as_view(), name='estado_resultados'),
    # path('libro-diario/', LibroDiarioView.as_view(), name='libro_diario'),
    # path('libro-mayor/', LibroMayorView.as_view(), name='libro_mayor'),
]
