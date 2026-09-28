import os

from pydantic_settings import BaseSettings, SettingsConfigDict

env = os.getenv("env","dev")

env_file = f".env.{env}"

print(env_file)




class ConfigSettings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str
    JWT_SECRET: str
    MAILTRAP_TOKEN: str

    model_config = SettingsConfigDict(env_file=env_file)


# figure our a way by which you can load a specific .env file based on env


def get_config_settings():
    return ConfigSettings()

settings = get_config_settings()



