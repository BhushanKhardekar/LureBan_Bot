"""
main.py — Local development entry point.

Delegates to base_app so all bot construction stays in one place.
Run with: python main.py
"""
from base_app import bot, settings

if __name__ == "__main__":
    bot.run(settings.discord_token, log_handler=None)
