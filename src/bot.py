"""
src/bot.py — Typed bot subclass.

Kept in its own module so both base_app.py and src/utils/commands.py
can import it without creating a circular dependency.
"""
from datetime import datetime, timezone, timedelta
from typing import Any

import discord
from discord.ext import commands, tasks

IST = timezone(timedelta(hours=5, minutes=30))


class LureBanBot(commands.Bot):
    """commands.Bot subclass with typed custom attributes."""

    start_time: datetime
    live_announcement: tasks.Loop[Any]

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True          # Required for kick and member-related events
        intents.message_content = True  # Required to read message content

        super().__init__(command_prefix="!", intents=intents)

        # Set before the event loop starts so the first live_announcement
        # tick has a valid uptime reference.
        self.start_time = datetime.now(IST)
