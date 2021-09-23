from rest_framework import serializers

from instructions.models import InstructionPageModel


class InstructionPageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructionPageModel
        fields = '__all__'

