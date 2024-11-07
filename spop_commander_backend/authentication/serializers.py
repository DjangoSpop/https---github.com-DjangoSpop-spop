from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

User = get_user_model()

# IMPORTANT: Keep all three serializers in this file:
# 1. UserSerializer - for registration
# 2. UserUpdateSerializer - for profile updates
# 3. UserDetailSerializer - for retrieving user details

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'confirm_password',
            'phone_number', 'rank', 'is_commander'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': "Passwords do not match."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        return User.objects.create_user(**validated_data)

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'phone_number',
            'rank', 'is_commander'
        )
        extra_kwargs = {
            'email': {'required': False},
            'is_commander': {'read_only': True}  # Only admins can change this
        }

    def validate_email(self, value):
        """Validate email is unique if being changed"""
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def update(self, instance, validated_data):
        """Update and return user"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    rank = serializers.ChoiceField(choices=[
        ('commander', 'Commander'),
        ('lieutenant', 'Lieutenant'),
        ('captain', 'Captain'),
        ('major', 'Major'),
        ('colonel', 'Colonel'),
    ])

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'confirm_password',
            'email',
            'phone_number',
            'rank',
            'is_commander',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'phone_number': {'required': True},
            'rank': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'كلمات المرور غير متطابقة'
            })

        # Validate password
        validate_password(data['password'])

        # Remove confirm_password from the data
        data.pop('confirm_password', None)

        # Set is_commander based on rank
        data['is_commander'] = data['rank'].lower() == 'commander'

        return data

    def create(self, validated_data):
        # Create user instance
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            rank=validated_data['rank'],

            is_commander=validated_data['is_commander'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for retrieving user details"""
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email',
            'phone_number', 'rank', 'is_commander', 'date_joined',
            'last_login'
        )
        read_only_fields = (
            'id', 'username', 'date_joined', 'last_login', 'is_commander'
        )

# You might also want to add a password change serializer:
class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "New passwords do not match."
            })
        return attrs