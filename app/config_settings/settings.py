from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigSettings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str

    model_config = SettingsConfigDict(env_file=".env")


# figure our a way by which you can load a specific .env file based on env


def get_config_settings():
    return ConfigSettings()

settings = get_config_settings()



