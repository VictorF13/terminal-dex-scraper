"""Module to scrape the SGB palette constants."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

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

    constant_name: str
    color_0: RGBColor
    color_1: RGBColor
    color_2: RGBColor
    color_3: RGBColor
    is_conditional: bool = False
    version: str | None = None  # "RED" or "BLUE" if conditional


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

        self.palettes = self._get_sgb_palette_data()
        self.constants = [palette.constant_name for palette in self.palettes]

    def _parse_rgb_line(
        self, line: str
    ) -> tuple[list[RGBColor], str] | tuple[None, None]:
        """Parse an RGB line to extract the 4 colors and constant name.

        Args:
            line (str): The line containing RGB data.

        Returns:
            tuple[list[RGBColor], str] | tuple[None, None]: A tuple containing the
                list of 4 RGB colors and the constant name, or (None, None) if parsing
                fails.

        """
        if not line.startswith("RGB") or ";" not in line:
            return None, None

        # Split the line into data and comment
        data_part = line.split(";")[0].strip()
        comment_part = line.split(";")[1].strip()

        # Extract the constant name from the comment
        constant_name = comment_part

        # Parse the RGB values: RGB 31,29,31, 21,28,11, 20,26,31, 03,02,02
        # Remove "RGB " prefix and split by comma
        rgb_data = data_part.replace("RGB", "").strip()
        values = [int(v.strip()) for v in rgb_data.split(",")]

        # Should have 12 values (4 colors x 3 channels each)
        expected_values = 12  # 4 colors x 3 RGB channels
        if len(values) != expected_values:
            return None, None

        colors = [
            RGBColor(values[0], values[1], values[2]),  # Color 0
            RGBColor(values[3], values[4], values[5]),  # Color 1
            RGBColor(values[6], values[7], values[8]),  # Color 2
            RGBColor(values[9], values[10], values[11]),  # Color 3
        ]

        return colors, constant_name

    def _get_sgb_palette_data(self) -> list[SGBPaletteData]:
        """Get the SGB palette data in Red and Blue.

        Returns:
            list[SGBPaletteData]: A list of SGB palette data objects.

        """
        palettes: list[SGBPaletteData] = []
        current_version: str | None = None

        with self._sgb_palette_constants_path.open() as file:
            for text_line in file:
                line = text_line.strip()

                # Check for version-specific conditionals
                if line.startswith("IF DEF(_RED)"):
                    current_version = "RED"
                    continue
                if line.startswith("IF DEF(_BLUE)"):
                    current_version = "BLUE"
                    continue
                if line.startswith("ENDC"):
                    current_version = None
                    continue

                # Parse RGB line
                colors, constant_name = self._parse_rgb_line(line)
                if colors and constant_name:
                    palette = SGBPaletteData(
                        constant_name=constant_name,
                        color_0=colors[0],
                        color_1=colors[1],
                        color_2=colors[2],
                        color_3=colors[3],
                        is_conditional=current_version is not None,
                        version=current_version,
                    )
                    palettes.append(palette)

        return palettes

    def get_palette_index(self, palette_constant: str) -> int:
        """Get the index of a palette constant.

        Args:
            palette_constant (str): The palette constant to get the index for.

        Returns:
            int: The index of the palette constant.

        """
        return self.constants.index(palette_constant)

    def get_palette_by_name(self, palette_constant: str) -> SGBPaletteData | None:
        """Get a palette by its constant name.

        Args:
            palette_constant (str): The palette constant to search for.

        Returns:
            SGBPaletteData | None: The palette data object, or None if not found.

        """
        for palette in self.palettes:
            if palette.constant_name == palette_constant:
                return palette
        return None

    def get_palettes_by_name(
        self, palette_constant: str
    ) -> list[SGBPaletteData] | None:
        """Get all palettes with the given constant name (including versions).

        Args:
            palette_constant (str): The palette constant to search for.

        Returns:
            list[SGBPaletteData] | None: A list of palette data objects with the given
                name, or None if not found.

        """
        matching_palettes = [
            palette
            for palette in self.palettes
            if palette.constant_name == palette_constant
        ]
        return matching_palettes if matching_palettes else None
