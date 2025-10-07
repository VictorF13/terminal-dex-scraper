"""Module to scrape the growth rate constants for all growth rates in Red and Blue."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class GrowthRateConstants:
    """Model to store the growth rate constants and related information."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the GrowthRateConstants object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._pokemon_data_constants_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "constants"
            / "pokemon_data_constants.asm"
        )

        growth_rate_constants = self._scrape_growth_rate_constants()

        self.constants: list[str] = growth_rate_constants[0]
        self.max_growth_rate_index: int = growth_rate_constants[1]

    def _scrape_growth_rate_constants(self) -> tuple[list[str], int]:
        """Scrape the growth rate constants for all growth rates in Red and Blue.

        Returns:
            list[str]: A list of growth rate constants for all growth rates in Red and
                Blue.

        """
        growth_rate_constants: list[str] = []
        max_growth_rate_index = 0
        for text_line in self._pokemon_data_constants_path.read_text().splitlines():
            line = text_line.strip()
            if line.startswith("const GROWTH_"):
                parts = line.split()
                growth_rate_constants.append(parts[1])
            elif line.startswith("DEF NUM_GROWTH_RATES"):
                max_growth_rate_index = len(growth_rate_constants)
        return growth_rate_constants, max_growth_rate_index

    def get_growth_rate_index(self, growth_rate_constant: str) -> int:
        """Get the index of a growth rate constant.

        Returns:
            int: The index of the growth rate constant.

        """
        return self.constants.index(growth_rate_constant)
