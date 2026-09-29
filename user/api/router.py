from django.urls import path

from user.api.views_token import LoginConLimiteView, RefreshConLimiteView

urlpatterns = [
    # Login y refresh con freno de intentos (tarea E6): ver `user/api/views_token.py`.
    path('api/token/', LoginConLimiteView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', RefreshConLimiteView.as_view(), name='token_refresh'),
]
