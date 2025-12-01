"""Module to scrape the icon constants."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class IconConstants:
    """Model to store the icon constants for the Pokémon in Red and Blue."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the IconConstants object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._icon_constants_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "constants"
            / "icon_constants.asm"
        )

        self.constants = self._get_icon_constants()

    def _get_icon_constants(self) -> list[str | None]:
        """Get the icon constants in Red and Blue."""
        with self._icon_constants_path.open() as file:
            data = file.read().splitlines()

        data = [
            line.strip().split(";")[0].strip()
            for line in data
            if not line.strip().startswith(";")
        ]

        filtered_data: list[str | None] = []
        for line in data:
            if line.startswith("const_skip "):
                skip_count = int(line.split()[1])
                filtered_data.extend([None] * skip_count)
            elif line.startswith("const "):
                filtered_data.append(line.split()[1])

        return filtered_data
