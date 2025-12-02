"""Module to scrape the Pokédex order from Red and Blue."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class PokedexOrder:
    """Model to store the Pokédex order for Red and Blue.

    Attributes:
        order (list[str]): A list of Pokédex constants in the order they appear in the
            game's internal indexing. Index 0 is MISSINGNO, and subsequent indices
            correspond to the internal Pokémon index values.

    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the PokedexOrder object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._pokedex_order_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "data"
            / "pokemon"
            / "dex_order.asm"
        )

        self.order: list[str] = self._scrape_pokedex_order()

    def _scrape_pokedex_order(self) -> list[str]:
        """Scrape the Pokédex order from the dex_order.asm file.

        Returns:
            list[str]: A list of Pokédex constants in internal index order. Index 0 is
                MISSINGNO, followed by all entries from the file.

        """
        pokedex_order: list[str] = ["0"]

        for text_line in self._pokedex_order_path.read_text().splitlines():
            line = text_line.strip()
            if line.startswith("db "):
                # Extract the value after "db " and before any comment
                value = line[3:].split(";")[0].strip()
                pokedex_order.append(value)

        return pokedex_order
