import asyncio
import os

from django.apps import AppConfig


class BotConfig(AppConfig):
    name = "bot"
    models_module = None

    def ready(self):
        from .bot import client

        # Check if we're in an async context.
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return

        asyncio.create_task(
            client.start(os.environ["DISCORD_BOT_TOKEN"]), name="bot-start"
        )
