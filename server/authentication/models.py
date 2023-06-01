import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    client = models.ForeignKey(
        "oauth.Client",
        default=None,
        null=True,
        on_delete=models.SET_NULL,
        related_name="clients",
    )
