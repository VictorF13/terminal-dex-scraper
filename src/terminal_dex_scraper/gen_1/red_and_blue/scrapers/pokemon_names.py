"""Module to scrape the names for all Pokémon in Red and Blue."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class PokemonNames:
    """Model to store the names for all Pokémon in Red and Blue."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the PokemonNames object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._pokemon_names_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "data"
            / "pokemon"
            / "names.asm"
        )

        self.names: list[str] = self._get_pokemon_names()

    def _get_pokemon_names(self) -> list[str]:
        """Get the names for all Pokémon in Red and Blue.

        Returns:
            list[str]: A list of names for all Pokémon in Red and Blue.

        """
        with self._pokemon_names_path.open() as file:
            data = file.read().splitlines()

        return ["NOPKMNNAME"] + [
            line.strip().replace("\t", "").split()[1].replace('"', "")
            for line in data
            if line.strip() not in [""]
            and not line.strip().startswith(";")
            and line.strip().startswith("dname")
        ]
