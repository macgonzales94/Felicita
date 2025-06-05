from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name = 'usuarios'

# Router para ViewSets
router = DefaultRouter()
# router.register(r'usuarios', UsuarioViewSet)
# router.register(r'sesiones', SesionUsuarioViewSet)

urlpatterns = [
    # Autenticación JWT
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # URLs del router
    path('', include(router.urls)),
    
    # URLs personalizadas
    # path('perfil/', PerfilUsuarioView.as_view(), name='perfil'),
    # path('cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),
    # path('logout/', LogoutView.as_view(), name='logout'),
]