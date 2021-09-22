from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    real_display_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_real_display_name(self, obj):
        return obj.get_real_display_name()

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "first_name", "last_name", "full_name",
                  "display_name", "real_display_name", "date_joined",
                  "is_staff", "is_active", "is_superuser"]
