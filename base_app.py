"""
base_app.py — Bot factory and Docker entry point.

Constructs and configures the bot instance. When run directly
(python base_app.py) it also starts the bot, which is what the
Docker container does via ENTRYPOINT.
"""
from src.bot import LureBanBot
from src.config.config import settings
from src.utils.commands import setup_commands
from src.utils.events import setup_events
from src.utils.utils import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------------ #
# Bot instance                                                         #
# ------------------------------------------------------------------ #
bot = LureBanBot()

# Register commands & events
setup_commands(bot.tree)
setup_events(bot)

# ------------------------------------------------------------------ #
# Entry point (used by Docker ENTRYPOINT and direct local runs)       #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    logger.info("Starting LureBan Bot...")
    bot.run(settings.discord_token, log_handler=None)
