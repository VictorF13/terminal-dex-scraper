"""Module to scrape the SGB palette data values."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.sgb_palette_constants import (
    SGBPaletteConstants,
)

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class RGBColor:
    """Class representing a single RGB color value."""

    red: int
    green: int
    blue: int


@dataclass
class SGBPaletteData:
    """Class representing a Super Game Boy palette with 4 colors."""

    sgb_palette_constant_id: int
    color_0: RGBColor
    color_1: RGBColor
    color_2: RGBColor
    color_3: RGBColor
    is_conditional: bool = False
    version: str | None = None  # "RED" or "BLUE" if conditional


class SGBPaletteValues:
    """Model to store the SGB palette data values for Red and Blue."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the SGBPaletteValues object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._sgb_palette_data_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "data"
            / "sgb"
            / "sgb_palettes.asm"
        )
        self._sgb_palette_constants: SGBPaletteConstants = SGBPaletteConstants(
            self._settings
        )

        self.palettes: list[SGBPaletteData] = self._get_sgb_palette_data()

    def _parse_rgb_line(
        self, line: str
    ) -> tuple[list[RGBColor], int] | tuple[None, None]:
        """Parse an RGB line to extract the 4 colors and constant ID.

        Args:
            line (str): The line containing RGB data.

        Returns:
            tuple[list[RGBColor], int] | tuple[None, None]: A tuple containing the
                list of 4 RGB colors and the constant ID, or (None, None) if parsing
                fails.

        """
        if not line.startswith("RGB") or ";" not in line:
            return None, None

        data_part = line.split(";")[0].strip()
        comment_part = line.split(";")[1].strip()
        constant_name = comment_part
        constant_id = self._sgb_palette_constants.get_palette_index(constant_name)

        rgb_data = data_part.replace("RGB", "").strip()
        values = [int(value.strip()) for value in rgb_data.split(",")]

        expected_values = 12
        if len(values) != expected_values:
            return None, None

        colors = [
            RGBColor(values[0], values[1], values[2]),
            RGBColor(values[3], values[4], values[5]),
            RGBColor(values[6], values[7], values[8]),
            RGBColor(values[9], values[10], values[11]),
        ]

        return colors, constant_id

    def _get_sgb_palette_data(self) -> list[SGBPaletteData]:
        """Get the SGB palette data in Red and Blue.

        Returns:
            list[SGBPaletteData]: A list of SGB palette data objects.

        """
        palettes: list[SGBPaletteData] = []
        current_version: str | None = None

        with self._sgb_palette_data_path.open() as file:
            for text_line in file:
                line = text_line.strip()

                if line.startswith("IF DEF(_RED)"):
                    current_version = "RED"
                    continue
                if line.startswith("IF DEF(_BLUE)"):
                    current_version = "BLUE"
                    continue
                if line.startswith("ENDC"):
                    current_version = None
                    continue

                colors, constant_id = self._parse_rgb_line(line)
                if colors and constant_id is not None:
                    palette = SGBPaletteData(
                        sgb_palette_constant_id=constant_id,
                        color_0=colors[0],
                        color_1=colors[1],
                        color_2=colors[2],
                        color_3=colors[3],
                        is_conditional=current_version is not None,
                        version=current_version,
                    )
                    palettes.append(palette)

        return palettes

    def get_palette_by_id(self, palette_constant_id: int) -> SGBPaletteData | None:
        """Get a palette by its constant ID.

        Args:
            palette_constant_id (int): The palette constant ID to search for.

        Returns:
            SGBPaletteData | None: The palette data object, or None if not found.

        """
        for palette in self.palettes:
            if palette.sgb_palette_constant_id == palette_constant_id:
                return palette
        return None

    def get_palettes_by_id(
        self, palette_constant_id: int
    ) -> list[SGBPaletteData] | None:
        """Get all palettes with the given constant ID (including versions).

        Args:
            palette_constant_id (int): The palette constant ID to search for.

        Returns:
            list[SGBPaletteData] | None: A list of palette data objects with the given
                name, or None if not found.

        """
        matching_palettes = [
            palette
            for palette in self.palettes
            if palette.sgb_palette_constant_id == palette_constant_id
        ]
        return matching_palettes if matching_palettes else None
