import json
import pathlib
import discord
from discord import app_commands
from discord.ext import tasks
from datetime import datetime

from src.bot import LureBanBot, IST
from src.config.config import settings
from src.utils.utils import get_logger

logger = get_logger(__name__)

# Resolved at import time so it works regardless of the working directory.
LIVE_MESSAGE_PATH = pathlib.Path(__file__).parent.parent / "config" / "live_message.json"


def setup_commands(tree: app_commands.CommandTree) -> None:
    """Register all slash commands and the live-announcement background task."""
    bot: LureBanBot = tree.client  # type: ignore[assignment]

    # ------------------------------------------------------------------ #
    # Slash commands                                                       #
    # ------------------------------------------------------------------ #

    @tree.command(name="ping", description="Check bot latency")
    async def ping(interaction: discord.Interaction) -> None:
        latency = round(interaction.client.latency * 1000)
        await interaction.response.send_message(
            f"Hi {interaction.user.mention}! Your ping is **{latency} ms**"
        )

    @tree.command(name="hello", description="Greet the bot")
    async def hello(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"Hello {interaction.user.mention}! Nice to meet you!"
        )

    @tree.command(name="echo", description="Echo back your message")
    async def echo(interaction: discord.Interaction, message: str) -> None:
        await interaction.response.send_message(
            f"{interaction.user.mention} said: {message}"
        )

    @tree.command(name="clear", description="Delete last N messages (requires Manage Messages)")
    async def clear(interaction: discord.Interaction, amount: int) -> None:
        await interaction.response.defer(ephemeral=True)

        # guild_permissions is only available on Member, not User.
        if not isinstance(interaction.user, discord.Member):
            await interaction.followup.send(
                "❌ This command can only be used inside a server.", ephemeral=True
            )
            return

        if not interaction.user.guild_permissions.manage_messages:
            await interaction.followup.send(
                "❌ You don't have permission to manage messages.", ephemeral=True
            )
            return

        # purge() is only available on text-based guild channels.
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.followup.send(
                "❌ This command can only be used in a text channel.", ephemeral=True
            )
            return

        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(
            f"✅ Deleted **{len(deleted)}** message(s).", ephemeral=True
        )

    # ------------------------------------------------------------------ #
    # Live announcement task                                               #
    # ------------------------------------------------------------------ #

    def _build_embed() -> discord.Embed:
        """Build the live-status embed."""
        now = datetime.now(IST)
        uptime = now - bot.start_time
        total_seconds = int(uptime.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        uptime_text = (
            f"{days}d {hours}h {minutes}m" if days else f"{hours}h {minutes}m"
        )
        bot_ping = round(bot.latency * 1000)

        embed = discord.Embed(
            title="LureBan",
            description="**I am Watching you!** 🎮",
            color=discord.Color.orange(),
        )
        embed.add_field(
            name="⚠️ DO NOT SEND MESSAGES IN THIS CHANNEL",
            value=(
                "This channel is used to catch spam bots. "
                "Any messages sent here will result in a **softban**."
            ),
            inline=False,
        )
        embed.add_field(name="Ping 📡", value=f"`{bot_ping} ms`", inline=True)
        embed.add_field(name="Uptime", value=f"`{uptime_text}`", inline=True)
        embed.set_footer(
            text=f"Updated every 1 min • {now.strftime('%Y-%m-%d %I:%M %p IST')}"
        )
        return embed

    def _read_message_id() -> int:
        try:
            return json.loads(LIVE_MESSAGE_PATH.read_text()).get("kick_user_message_id", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def _write_message_id(message_id: int) -> None:
        LIVE_MESSAGE_PATH.write_text(
            json.dumps({"kick_user_message_id": message_id}, indent=4)
        )

    @tasks.loop(minutes=1)
    async def live_announcement() -> None:
        raw_channel = bot.get_channel(settings.kick_user_channel_id)

        # fetch_message / send are only available on TextChannel.
        if not isinstance(raw_channel, discord.TextChannel):
            logger.error(
                "kick_user_channel_id (%s) is not a TextChannel — check your .env",
                settings.kick_user_channel_id,
            )
            return

        channel: discord.TextChannel = raw_channel
        embed = _build_embed()

        # Try to reuse the existing pinned message.
        message_id = _read_message_id()
        live_message: discord.Message | None = None

        if message_id:
            try:
                live_message = await channel.fetch_message(message_id)
            except discord.NotFound:
                logger.warning("Saved live message no longer exists — will create a new one")
            except discord.Forbidden:
                logger.error("Missing permission to fetch the live message")
                return

        if live_message is None:
            live_message = await channel.send(
                content="@everyone",
                embed=embed,
                allowed_mentions=discord.AllowedMentions(everyone=True),
            )
            _write_message_id(live_message.id)
            logger.info("Live announcement created (message ID: %s)", live_message.id)
        else:
            await live_message.edit(embed=embed)
            logger.info("Live announcement updated")

    @live_announcement.before_loop
    async def before_live_announcement() -> None:
        await bot.wait_until_ready()

    bot.live_announcement = live_announcement
