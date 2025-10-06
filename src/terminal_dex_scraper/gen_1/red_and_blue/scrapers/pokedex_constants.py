"""Module to scrape the constants for the Pokédex in Red and Blue."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class PokedexConstants:
    """Model to store the Pokédex constants and related information.

    Attributes:
        constants (list[str]): A list of constant names for all Pokédex constants.
        max_pokedex_index (int): The maximum Pokedéx index. This is also the number of
            Pokédex entries. This is set in the codebase, which is why it's set here.

    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the PokedexConstants object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._pokedex_constants_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "constants"
            / "pokedex_constants.asm"
        )

        self.constants: list[str | None] = self._scrape_pokedex_constants()
        self.max_pokedex_index: int = len(self.constants) - 1

    def _scrape_pokedex_constants(self) -> list[str | None]:
        """Scrape the constant names for all Pokédex constants in Red and Blue.

        Returns:
            list[str | None]: A list of constant names for all Pokédex constants in Red
                and Blue. None represents an index with no corresponding Pokédex entry.

        """
        pokedex_constants: list[str | None] = []
        for text_line in self._pokedex_constants_path.read_text().splitlines():
            line = text_line.strip()
            if line.startswith("const_def"):
                pokedex_constants.append(None)
            elif line.startswith("const"):
                parts = line.split()
                pokedex_constants.append(parts[1])
        return pokedex_constants
