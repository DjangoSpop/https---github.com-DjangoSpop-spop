from rest_framework import serializers
from .models import Order, OrderAcknowledgment

class OrderAcknowledgmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = OrderAcknowledgment
        fields = ['id', 'user', 'user_name', 'acknowledged_at', 'comments']
        read_only_fields = ['user', 'acknowledged_at']

class OrderSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    assigned_to_name = serializers.CharField(
        source='assigned_to.get_full_name',
        read_only=True
    )
    acknowledgments = OrderAcknowledgmentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']