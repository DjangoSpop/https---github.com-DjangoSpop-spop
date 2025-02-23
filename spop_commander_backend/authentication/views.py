# authentication/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken , AccessToken


from .serializers import UserSerializer, UserDetailSerializer, UserUpdateSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['register', 'create', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action
        """
        if self.action == 'update':
            return UserUpdateSerializer
        elif self.action in ['retrieve', 'me']:
            return UserDetailSerializer
        return UserSerializer
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)  # This is the correct way to get access token
                },
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
            # return Response(
            #
            #     # UserDetailSerializer(user).data,
            #     # status=status.HTTP_201_CREATED
            # )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """Override create to use register action"""
        return self.register(request)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action (detail=False, methods=['post'])
    def login(self, request):
        serializer = UserDetailSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token = self.request.data.get('token')
            return Response({'token': token, 'user':UserDetailSerializer(user).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create refresh token
            refresh = RefreshToken.for_user(user)

            # Return response with tokens
            return Response({
                'user': serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)  # This is the correct way to get access token
                },
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)