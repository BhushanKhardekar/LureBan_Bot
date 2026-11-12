import discord

from src.bot import LureBanBot
from src.config.config import settings
from src.utils.utils import get_logger

logger = get_logger(__name__)


def setup_events(bot: LureBanBot) -> None:
    """Register gateway event handlers on the bot."""

    @bot.event
    async def on_ready() -> None:
        try:
            synced = await bot.tree.sync()
            logger.info("Synced %d slash command(s)", len(synced))
        except Exception as exc:
            logger.error("Failed to sync slash commands: %s", exc)

        bot.live_announcement.start()
        if bot.user:
            logger.info("Bot is ready — logged in as %s (ID: %s)", bot.user.name, bot.user.id)

    @bot.event
    async def on_message(message: discord.Message) -> None:
        # Ignore our own messages.
        if message.author == bot.user:
            return

        if message.channel.id == settings.kick_user_channel_id:
            member = message.author
            if not isinstance(member, discord.Member):
                return

            # create_invite is only available on TextChannel.
            channel = message.channel
            if not isinstance(channel, discord.TextChannel):
                logger.warning(
                    "kick_user_channel_id points to a non-text channel — cannot create invite"
                )
                return

            try:
                # Resolve rejoin invite.
                invite_url = settings.invite_link or None
                if not invite_url:
                    invite = await channel.create_invite(
                        max_age=300,
                        max_uses=1,
                        unique=True,
                        reason="Temporary rejoin invite for kicked user",
                    )
                    invite_url = invite.url
                    logger.info("Temporary invite created: %s", invite_url)

                # DM the user before kicking so they can still receive messages.
                guild = message.guild
                guild_name = guild.name if guild else "the server"
                try:
                    await member.send(
                        f"🚨 You have been kicked from **{guild_name}** "
                        f"for posting in the restricted security channel.\n\n"
                        f"🔗 Rejoin here: {invite_url}\n\n"
                        f"⚠️ Please do not post in that channel again."
                    )
                except discord.Forbidden:
                    logger.warning("Could not DM %s — DMs may be disabled", member)

                await message.delete()
                await member.kick(reason="Posted in restricted security channel")
                logger.info("Kicked %s (%s)", member, member.id)

            except discord.Forbidden:
                logger.error(
                    "Missing permissions to kick/delete/invite — check bot role permissions"
                )
            except Exception as exc:
                logger.error("Unexpected error in on_message: %s", exc)
            return

        await bot.process_commands(message)
