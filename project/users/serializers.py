from rest_framework import serializers
from users.models import Client


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = Client
        fields = (
            "email",
            "password",
            "name",
            "surname",
            "contact_info",
        )

    def create(self, validated_data):
        user = Client.objects.create_client(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data["name"],
            surname=validated_data["surname"],
            contact_info=validated_data["contact_info"],
        )

        return user
