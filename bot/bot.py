import json
import os
import traceback
import urllib.parse
from datetime import datetime, timedelta

import discord

from oauth.models import CLIENT, OAuthUser

from .utils import make_sleep_chart

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    try:
        if message.author == client.user:
            return

        if message.content == "!sleep register":
            oauth_url_params = urllib.parse.urlencode(
                {
                    "response_type": "code",
                    "client_id": os.environ["WITHINGS_CLIENT_ID"],
                    "state": f"{message.author.id},{message.author.name}",
                    "scope": "user.activity",
                    "redirect_uri": "http://localhost:8000/sleep/",
                }
            )
            oauth_url = f"https://account.withings.com/oauth2_user/authorize2?{oauth_url_params}"
            await message.channel.send(f"Please open {oauth_url} to register")

        if message.content == "!sleep info":
            user = await OAuthUser.objects.aget(discord_id=message.author.id)
            access_token = await user.get_access_token()
            resp = await CLIENT.post(
                "https://wbsapi.withings.net/v2/sleep",
                data={
                    "action": "getsummary",
                    "startdateymd": "2023-05-22",
                    "enddateymd": "2023-05-23",
                },
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            data = resp.json()
            await message.channel.send(json.dumps(data, indent=2))

        if message.content == "!sleep chart":
            user = await OAuthUser.objects.aget(discord_id=message.author.id)
            access_token = await user.get_access_token()
            now = datetime.now()
            resp = await CLIENT.post(
                "https://wbsapi.withings.net/v2/sleep",
                data={
                    "action": "get",
                    "startdate": str(int((now - timedelta(days=1)).timestamp())),
                    "enddate": str(int(now.timestamp())),
                },
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            data = resp.json()
            chartf = make_sleep_chart(data)
            chartf.seek(0, 0)
            await message.channel.send(
                file=discord.File(chartf, filename="sleep-chart.png")
            )

        if message.content.startswith("$hello"):
            await message.channel.send("Hello!")
    except Exception:
        traceback.print_exc()
