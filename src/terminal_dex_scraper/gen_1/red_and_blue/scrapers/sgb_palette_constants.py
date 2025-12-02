"""Module to scrape the SGB palette constants."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class SGBPaletteConstants:
    """Model to store the SGB palette constants for Red and Blue."""

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
            / "data"
            / "sgb"
            / "sgb_palettes.asm"
        )

        self.constants = self._get_sgb_palette_constants()

    def _get_sgb_palette_constants(self) -> list[str]:
        """Get the SGB palette constants in Red and Blue.

        Returns:
            list[str]: A list of SGB palette constants.

        """
        sgb_palette_constants: list[str] = []
        with self._sgb_palette_constants_path.open() as file:
            for text_line in file:
                line = text_line.strip()
                if line.startswith("RGB") and ";" in line:
                    comment_part = line.split(";")[1].strip()
                    sgb_palette_constants.append(comment_part)

        return sgb_palette_constants

    def get_palette_index(self, palette_constant: str) -> int:
        """Get the index of a palette constant.

        Args:
            palette_constant (str): The palette constant to get the index for.

        Returns:
            int: The index of the palette constant.

        """
        return self.constants.index(palette_constant)
