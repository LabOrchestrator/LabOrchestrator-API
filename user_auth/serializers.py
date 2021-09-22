from dj_rest_auth import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers as r_serializers


# used for rest-auth plugin
class CustomLoginSerializer(serializers.LoginSerializer):
    username = None


# used for rest-auth plugin
class CustomRegisterSerializer(RegisterSerializer):
    username = None
    first_name = r_serializers.CharField(allow_blank=False, max_length=150, trim_whitespace=True)
    last_name = r_serializers.CharField(allow_blank=True, max_length=150, trim_whitespace=True)
    display_name = r_serializers.CharField(allow_blank=True, max_length=150, trim_whitespace=True)

    def get_cleaned_data(self):
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'display_name': self.validated_data.get('display_name', '')
        }


class CustomUserDetailsSerializer(serializers.UserDetailsSerializer):
    display_name = r_serializers.CharField(allow_blank=True, max_length=150, trim_whitespace=True)
    real_display_name = r_serializers.SerializerMethodField()

    def get_real_display_name(self, obj):
        return obj.get_real_display_name()

    class Meta:
        extra_fields = ['display_name', 'real_display_name']
        UserModel = get_user_model()
        if hasattr(UserModel, "USERNAME_FIELD"):
            extra_fields.append(UserModel.USERNAME_FIELD)
        if hasattr(UserModel, "EMAIL_FIELD"):
            extra_fields.append(UserModel.EMAIL_FIELD)

        model = UserModel
        fields = ('pk', 'first_name', 'last_name', *extra_fields)
        read_only_fields = ('email',)

