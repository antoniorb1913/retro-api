"""
Vistas de autenticación con freno de intentos.

SimpleJWT trae `TokenObtainPairView` y `TokenRefreshView` listas para usar, pero **no tienen dónde
declarar un límite**: son clases cerradas. Estas dos heredan de ellas y solo añaden el freno
(`throttle_scope`), sin cambiar nada de su comportamiento.

Motivo (tarea E6): sin límite se pueden probar contraseñas a miles por minuto con un programa.
"""
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.api.throttles import ThrottleConExencionStaff


class LoginConLimiteView(TokenObtainPairView):
    """
    Login (`POST /api/api/token/`): como máximo `login` intentos por minuto y por IP
    (el número está en `DEFAULT_THROTTLE_RATES`).
    """
    throttle_classes = [ThrottleConExencionStaff]
    throttle_scope = 'login'


class RefreshConLimiteView(TokenRefreshView):
    """
    Refresco del token (`POST /api/api/token/refresh/`): límite propio, independiente del login.
    """
    throttle_classes = [ThrottleConExencionStaff]
    throttle_scope = 'refresh'
