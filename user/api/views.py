from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.api.serializers import UserRegisterSerializer

class RegistroView(APIView):
    permission_classes = []
    
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