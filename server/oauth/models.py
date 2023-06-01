from __future__ import annotations

import secrets
import uuid

from django.db import models
from django.utils import timezone

from authentication.models import User


class ClientManager(models.Manager):
    def create(self, client_name: str, redirect_uris: str, owner: User) -> Client:
        client = super().create(
            client_id=uuid.uuid5(owner.user_id, client_name),
            client_secret=secrets.token_urlsafe(32),
            client_name=client_name,
            redirect_uris=redirect_uris,
        )
        owner.clients.add(client)
        return client


class Client(models.Model):
    class GrantType(models.TextChoices):
        AUTHENTICATION_CODE = "code"

    class ResponseType(models.TextChoices):
        AUTHENTICATION_CODE = "code"

    client_id = models.UUIDField(unique=True, editable=False)
    client_secret = models.CharField(max_length=32, blank=True)
    client_name = models.CharField(max_length=120)
    redirect_uris = models.TextField()
    grant_type = models.CharField(
        max_length=10,
        default=GrantType.AUTHENTICATION_CODE,
        choices=GrantType.choices,
    )
    response_type = models.CharField(
        max_length=10,
        default=ResponseType.AUTHENTICATION_CODE,
        choices=ResponseType.choices,
    )
    scopes = models.TextField(default="read write")

    user = models.ForeignKey(
        User,
        default=None,
        null=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )

    objects = ClientManager()


class TokenManager(models.Manager):
    def create(self, client: Client, scope: str = "read") -> Token:
        # revoke the old token and create a new token
        return self.update_or_create(
            user=client.user,
            client=client,
            defaults={
                "access_token": secrets.token_urlsafe(32),
                "refresh_token": secrets.token_urlsafe(32),
                "scope": scope,
            },
        )


class Token(models.Model):
    access_token = models.CharField(max_length=255, unique=True, null=False)
    refresh_token = models.CharField(max_length=255, db_index=True)
    scope = models.TextField(default="read")
    issued_at = models.DateTimeField(auto_now_add=True, auto_now=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    @property
    def expires_at(self) -> timezone.datetime:
        return self.issued_at + timezone.timedelta(hours=2)

    objects = TokenManager()
