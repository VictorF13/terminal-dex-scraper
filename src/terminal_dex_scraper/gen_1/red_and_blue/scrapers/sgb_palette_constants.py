"""Module to scrape the SGB palette constants."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class SGBPaletteConstants:
    """Model to store the SGB palette constants for Red and Blue.

    Attributes:
        constants (list[str]): A list of constant names for all SGB palettes.
        max_sgb_palette_index (int): The maximum SGB palette index.

    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the SGBPaletteConstants object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._sgb_palette_constants_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "constants"
            / "palette_constants.asm"
        )

        self.constants: list[str] = self._scrape_sgb_palette_constants()
        self.max_sgb_palette_index: int = len(self.constants) - 1

    def _scrape_sgb_palette_constants(self) -> list[str]:
        """Scrape the SGB palette constants from palette_constants.asm.

        Returns:
            list[str]: A list of constant names for all SGB palettes.

        """
        in_sgb_palette_section = False
        sgb_palette_constants: list[str] = []

        for text_line in self._sgb_palette_constants_path.read_text().splitlines():
            line = text_line.strip()

            if line == "; sgb palettes":
                in_sgb_palette_section = True
                continue

            if not in_sgb_palette_section:
                continue

            if line.startswith("DEF NUM_SGB_PALS"):
                break

            if line.startswith("const "):
                sgb_palette_constants.append(line.split()[1])

        return sgb_palette_constants

    def get_palette_index(self, palette_constant: str) -> int:
        """Get the index of a palette constant.

        Args:
            palette_constant (str): The palette constant to get the index for.

        Returns:
            int: The index of the palette constant.

        """
        return self.constants.index(palette_constant)

    def serialize_records(self) -> list[dict[str, int | str]]:
        """Build JSON-ready records for SGB palette constants.

        Returns:
            list[dict[str, int | str]]: A list of records where each record contains
                the constant index and name.

        """
        return [
            {
                "sgb_palette_constant_id": constant_index,
                "sgb_palette_constant_name": constant_name,
            }
            for constant_index, constant_name in enumerate(self.constants)
        ]
