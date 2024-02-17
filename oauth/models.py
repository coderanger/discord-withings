import datetime
import os

import httpx
from django.db import models
from django.utils import timezone

CLIENT = httpx.AsyncClient()


class OAuthUser(models.Model):
    userid = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    scope = models.CharField(max_length=255)
    token_type = models.CharField(max_length=255)

    discord_id = models.BigIntegerField(unique=True)
    discord_mention = models.CharField(max_length=255)

    async def get_access_token(self):
        if self.expires_at < timezone.now():
            return self.access_token
        # Need to refresh!
        resp = await CLIENT.post(
            "https://wbsapi.withings.net/v2/oauth2",
            data={
                "action": "requesttoken",
                "client_id": os.environ["WITHINGS_CLIENT_ID"],
                "client_secret": os.environ["WITHINGS_CLIENT_SECRET"],
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        if data["status"] != 0:
            raise Exception(data["error"])
        self.access_token = data["body"]["access_token"]
        self.expires_at = timezone.now() + datetime.timedelta(
            seconds=data["body"]["expires_in"]
        )
        await self.asave(update_fields=["access_token", "expires_at"])
        return self.access_token
