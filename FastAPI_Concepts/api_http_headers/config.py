import os

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    A settings class for the project defining all the necessary parameters within the
    app through an object.
    """
    DATABASE_USER: str | None = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD: str | None = os.getenv("DATABASE_PASSWORD")
    DATABASE_HOST: str | None = os.getenv("DATABASE_HOST")
    DATABASE_PORT: str | None = os.getenv("DATABASE_PORT")
    DATABASE_NAME: str | None = os.getenv("DATABASE_NAME")
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")


    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_url(cls, val, values) -> str:
        """
        Create a Database URL from the settings provided in the .env file.
        """
        if isinstance(val, str):
            return val

        database_user = values.data.get("DATABASE_USER")
        database_password = values.data.get("DATABASE_PASSWORD")
        database_host = values.data.get("DATABASE_HOST")
        database_port = values.data.get("DATABASE_PORT").replace('"', "")
        database_name = values.data.get("DATABASE_NAME")

        if not all(
            [
                database_user,
                database_password,
                database_host,
                database_port,
                database_name,
            ]
        ):
            raise ValueError("Incomplete database connection information")

        return (
            f"postgresql+asyncpg://"
            f"{database_user}:{database_password}@{database_host}:{database_port}/{database_name}"
        )


settings = Settings()