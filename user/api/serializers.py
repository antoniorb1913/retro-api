from rest_framework import serializers
from user.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password']
        
        
        def create(self, validated_data):
        # Usamos create_user para que Django encripte la contraseña automáticamente con PBKDF2
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', '')
            )
            return user