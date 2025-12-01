"""Module to scrape all of the Menu Icons for all Pokémon."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class PokemonMenuIcons:
    """Model to store the Menu Icons for the Pokémon in Red and Blue."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the PokemonMenuIcon object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._pokemon_menu_icons_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "data"
            / "pokemon"
            / "menu_icons.asm"
        )

        self.menu_icons = ["NO_MON_ICON", *self._get_pokemon_menu_icons()]

    def _get_pokemon_menu_icons(self) -> list:
        """Get the menu icons for all the Pokémon in Red and Blue."""
        with self._pokemon_menu_icons_path.open() as file:
            data = file.read().splitlines()

        data = [
            line.strip().split(";")[0].strip()
            for line in data
            if not line.strip().startswith(";")
        ]

        return [line.split()[1] for line in data if line.startswith("nybble ")]
