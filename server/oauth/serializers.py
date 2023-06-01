from rest_framework import serializers

from oauth.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Mate:
        models = Client
        fields = "__all__"
