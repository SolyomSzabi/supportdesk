from rest_framework import serializers
from .models import User


class MeSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "role", "company"]