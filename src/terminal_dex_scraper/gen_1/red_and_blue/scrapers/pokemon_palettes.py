"""Module to scrape all of the Palettes for all Pokémon."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class PokemonPalettes:
    """Model to store the Palettes for the Pokémon in Red and Blue."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the PokemonPalettes object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._pokemon_palettes_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "data"
            / "pokemon"
            / "palettes.asm"
        )

        self.palettes = self._get_pokemon_palettes()

    def _get_pokemon_palettes(self) -> list:
        """Get the palettes for all the Pokémon in Red and Blue.

        Returns:
            list: List of palette constant names for each Pokémon.

        """
        with self._pokemon_palettes_path.open() as file:
            data = file.read().splitlines()

        data = [
            line.strip().split(";")[0].strip()
            for line in data
            if not line.strip().startswith(";")
        ]

        return [line.split()[1] for line in data if line.startswith("db PAL_")]
