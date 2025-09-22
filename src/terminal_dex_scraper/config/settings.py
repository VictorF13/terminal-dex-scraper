"""Module for settings for the Terminal Dex Scraper."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the Terminal Dex Scraper."""

    pokered_disassembly_repo: str = "git@github.com:pret/pokered.git"
