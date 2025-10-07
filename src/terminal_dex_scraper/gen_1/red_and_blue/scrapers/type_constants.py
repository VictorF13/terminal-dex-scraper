"""Module to scrape the type constants for all types in Red and Blue."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class TypeConstants:
    """Model to store the type constants and related information.

    Attributes:
        constants (list[str | None]): A list of type constants for all types in Red and
            Blue.
        markers (dict[str, int]): A dictionary of markers for the type constants. The
            key is the marker, and the value is the index of the type constant.

    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the TypeConstants object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._type_constants_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "constants"
            / "type_constants.asm"
        )

        type_constants = self._scrape_type_constants()

        self.constants: list[str | None] = type_constants[0]
        self.markers: dict[str, int] = type_constants[1]

    def _scrape_type_constants(self) -> tuple[list[str | None], dict[str, int]]:
        """Scrape the type constants for all types in Red and Blue.

        Returns:
            list[str]: A list of type constants for all types in Red and Blue.

        """
        type_constants: list[str | None] = []
        type_constants_markers: dict[str, int] = {}
        for text_line in self._type_constants_path.read_text().splitlines():
            if text_line.strip().startswith("DEF"):
                type_constants_markers.update(
                    {text_line.strip().split()[1]: len(type_constants)}
                )
            elif text_line.strip().startswith("const "):
                parts = text_line.strip().split()
                type_constants.append(parts[1])
            elif text_line.strip().startswith("const_next"):
                type_constants.extend([None] * (20 - len(type_constants)))

        return (
            type_constants,
            type_constants_markers,
        )
