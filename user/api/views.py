from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from user.api.serializers import UserRegisterSerializer

class RegistroView(APIView):
    # Única vista abierta a propósito: darse de alta tiene que ser posible sin cuenta previa.
    # El resto de la API exige token (`DEFAULT_PERMISSION_CLASSES` en core/settings.py).
    # OJO: hoy esta vista NO está conectada a ninguna ruta (ver AGENTS.md §11.6 y §13.7).
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        
        # Si no es válido, drf lanza un 400 automáticamente. Si es válido, continúa abajo.
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Devolvemos un JSON limpio y un estado de éxito HTTP 201 Created (esencial para registros)
        return Response(
            {"message": "Usuario registrado correctamente"}, 
            status=status.HTTP_201_CREATED
        )