from rest_framework import serializers

from .models import Reply, Ticket


class ReplySerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Reply
        fields = ["id", "author", "body", "created_at"]


class TicketSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "category",
            "ai_summary",
            "company",
            "created_by",
            "assigned_to",
            "created_at",
            "updated_at",
            "replies",
        ]
        read_only_fields = ["ai_summary"]

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        return value
