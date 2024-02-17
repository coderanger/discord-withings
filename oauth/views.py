import datetime
import os
from urllib.parse import urlsplit, urlunsplit

from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from .models import CLIENT, OAuthUser


async def oauth_landing(req: HttpRequest) -> HttpResponse:
    access_code = req.GET.get("code")
    if not access_code:
        raise ValueError("Unable to find access code")
    state = req.GET["state"]
    discord_id, discord_mention = state.split(",", 1)
    parsed = urlsplit(req.build_absolute_uri())
    clean_uri = urlunsplit(
        (
            parsed[0],
            parsed[1],
            parsed[2],
            None,
            None,
        )
    )
    resp = await CLIENT.post(
        "https://wbsapi.withings.net/v2/oauth2",
        data={
            "action": "requesttoken",
            "client_id": os.environ["WITHINGS_CLIENT_ID"],
            "client_secret": os.environ["WITHINGS_CLIENT_SECRET"],
            "grant_type": "authorization_code",
            "code": access_code,
            "redirect_uri": clean_uri,
        },
    )
    resp.raise_for_status()
    data = resp.json()
    if data["status"] != 0:
        raise Exception(data["error"])
    body = data["body"]
    await OAuthUser.objects.aupdate_or_create(
        userid=body["userid"],
        discord_id=discord_id,
        defaults={
            "access_token": body["access_token"],
            "refresh_token": body["refresh_token"],
            "expires_at": timezone.now()
            + datetime.timedelta(seconds=body["expires_in"]),
            "scope": body["scope"],
            "token_type": body["token_type"],
            "discord_mention": discord_mention,
        },
    )
    return HttpResponse(f"Successfully registered user {body['userid']}")


async def temp_sleep_chart(req: HttpRequest) -> HttpResponse:
    from bot.tmp_fixture import fixture
    from bot.utils import make_sleep_chart

    return HttpResponse(make_sleep_chart(fixture).getvalue(), content_type="image/png")
