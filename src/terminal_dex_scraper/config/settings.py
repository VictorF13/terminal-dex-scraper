"""Module for settings for the Terminal Dex Scraper."""

from pydantic_settings import BaseSettings

from terminal_dex_scraper.config.constants import (
    POKEMON_RED_AND_BLUE_DISASSEMBLY_REPO_URL,
)


class Settings(BaseSettings):
    """Settings for the Terminal Dex Scraper."""

    pokemon_red_and_blue_disassembly_repo: str = (
        POKEMON_RED_AND_BLUE_DISASSEMBLY_REPO_URL
    )
