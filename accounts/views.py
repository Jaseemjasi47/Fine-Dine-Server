from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.utilities import genarate_otp


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email', 'password', 'name', 'phone', 'profile_image']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        user.is_active = True
        if password is not None:
            user.set_password(password)
        user.save()
        return user
    

class SignUpView(APIView):
    def post(self, request):
        print(request.data['email'],"------------------------in-------------------------")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Check if email already exists
            user = serializer.save()

            print('==============================================================================')
            print(user,'---------------------------------------user----------------------------------')

            response_data = {
                'message': 'User registered successfully',
                'user_id': user.id,
                'email': user.email,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SendOtpView(APIView):
    def post(self, request):
        if User.objects.filter(email=request.data['email']).exists():
            return Response({'message': 'Email is already registered'}, status=status.HTTP_400_BAD_REQUEST)
        otp = genarate_otp(request.data['email'],request.data['name'])
        if otp:
            return Response(otp, status=status.HTTP_201_CREATED)
        elif not otp:
            return Response({'message': 'Email is Not Found!'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Failed'}, status=status.HTTP_400_BAD_REQUEST)


class AuthView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data['access']
        refreshToken = response.data['refresh']
        response.data['accessToken'] = token
        response.data['refreshToken'] = refreshToken
        response.data.pop('access', None)
        response.data.pop('refresh', None)
        email = request.data.get('email')
        user = User.objects.get(email=email)
        response.data['user'] = {
            "name" : str(user.name),
            "email" : str(user.email),
            "staff" : str(user.is_staff), 
            "admin" : str(user.is_admin)
        }
        return response
    



