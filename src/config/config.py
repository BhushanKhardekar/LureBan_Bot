import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    discord_token: str
    i_am_live_channel_id: int
    kick_user_channel_id: int
    commands_channel_id: int
    invite_link: str

    @classmethod
    def from_env(cls) -> "Config":
        discord_token = os.getenv("DISCORD_TOKEN", "")
        kick_user_channel_id = int(os.getenv("kick_user_channel_id", "0") or 0)

        if not discord_token:
            raise RuntimeError(
                "DISCORD_TOKEN environment variable is not set. "
                "Add it to your .env file."
            )
        if not kick_user_channel_id:
            raise RuntimeError(
                "kick_user_channel_id environment variable is not set or is 0. "
                "Add it to your .env file."
            )

        return cls(
            discord_token=discord_token,
            i_am_live_channel_id=int(os.getenv("i_am_live_channel_id", "0") or 0),
            kick_user_channel_id=kick_user_channel_id,
            commands_channel_id=int(os.getenv("commands_channel_id", "0") or 0),
            invite_link=os.getenv("invite_link", ""),
        )


settings = Config.from_env()
