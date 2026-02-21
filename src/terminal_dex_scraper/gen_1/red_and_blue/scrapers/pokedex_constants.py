"""Module to scrape the constants for the Pokédex in Red and Blue."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class PokedexConstants:
    """Model to store the Pokédex constants and related information.

    Attributes:
        constants (dict[int, str]): A mapping of Pokédex constant IDs to names.
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

        self.constants: dict[int, str] = self._scrape_pokedex_constants()
        self.max_pokedex_index: int = max(self.constants) if self.constants else 0

    def _scrape_pokedex_constants(self) -> dict[int, str]:
        """Scrape the constant names for all Pokédex constants in Red and Blue.

        Returns:
            dict[int, str]: A mapping of Pokédex constant IDs to names.

        """
        pokedex_constants: dict[int, str] = {}
        next_constant_value = 0
        for text_line in self._pokedex_constants_path.read_text().splitlines():
            line = text_line.strip()
            if line.startswith("const_def"):
                parts = line.split()
                next_constant_value = int(parts[1]) if len(parts) > 1 else 0
            elif line.startswith("const"):
                parts = line.split()
                pokedex_constants[next_constant_value] = parts[1]
                next_constant_value += 1
        return pokedex_constants

    def get_pokedex_index(self, pokedex_constant: str) -> int:
        """Get the index of a Pokédex constant.

        Returns:
            int: The index of the Pokédex constant.

        """
        for pokedex_index, constant_name in self.constants.items():
            if constant_name == pokedex_constant:
                return pokedex_index
        message = f"No Pokédex constant found for name: {pokedex_constant}"
        raise ValueError(message)

    def serialize_records(self) -> list[dict[str, int | str]]:
        """Build JSON-ready records for Pokédex constants.

        Returns:
            list[dict[str, int | str]]: A list of records where each record contains
                the constant index and name.

        """
        return [
            {
                "pokedex_constant_id": constant_index,
                "pokedex_constant_name": constant_name,
            }
            for constant_index, constant_name in sorted(self.constants.items())
        ]
