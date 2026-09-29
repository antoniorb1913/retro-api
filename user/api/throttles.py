"""
Freno de intentos (throttling) de la aplicación de usuarios.

Se usa `ScopedRateThrottle`: cada vista declara su propio límite con `throttle_scope`, y los
números viven en `DEFAULT_THROTTLE_RATES` (`core/settings.py`), para poder ajustarlos sin tocar
código.

**Cómo se cuenta el límite**: por IP mientras nadie ha iniciado sesión, y por usuario cuando la
petición ya va autenticada. Es el comportamiento propio de DRF.
"""
from rest_framework.throttling import ScopedRateThrottle


class ThrottleConExencionStaff(ScopedRateThrottle):
    """
    El freno normal, pero **el dueño no se frena a sí mismo** en los endpoints ya autenticados.

    Motivo: con una sola cuenta, un límite bajo hace que el propio dueño se bloquee mientras prueba
    su aplicación (subir fotos, hacer cambios). Es incómodo y no aporta seguridad, porque el dueño
    ya conoce sus credenciales.

    ⚠️ **Ámbito de la exención**: solo funciona donde la petición **ya va autenticada** (la subida
    de imágenes, que manda el token). En el **login no puede funcionar**, y no es un fallo de este
    código: cuando alguien pide un token, todavía no ha demostrado quién es, así que DRF ve un
    usuario anónimo (`request.user` es `AnonymousUser`) y el límite se cuenta por IP. Es decir, el
    dueño **sí** se frena si se pasa de intentos al entrar; como el límite es de 10 por minuto y se
    recupera solo, en la práctica no molesta.

    Lo que esto **no** es: una puerta abierta para los demás. Quien intenta adivinar la contraseña
    no está autenticado, así que se le aplica el límite con normalidad. Y si algún día hay más
    usuarios, a todos ellos se les frena igual (`is_staff` no se concede por registrarse).
    """

    def allow_request(self, request, view):
        usuario = getattr(request, 'user', None)

        if usuario is not None and usuario.is_authenticated and usuario.is_staff:
            return True

        return super().allow_request(request, view)
