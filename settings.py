import os


class Settings:
    APP_ID = os.environ.get("APP_ID")
    APP_SECRET = os.environ.get("APP_SECRET")
    CHANNEL_NAME = os.environ.get("CHANNEL_NAME")
    MUTED = os.environ.get("MUTED", default="false")
