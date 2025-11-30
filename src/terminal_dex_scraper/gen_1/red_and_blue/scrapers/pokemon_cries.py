"""Module to scrape the cries for all Pokémon in Red and Blue."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path

from dataclasses import dataclass


@dataclass
class PokemonCryData:
    """Class representing the values for a single Pokémon cry."""

    sfx_cry_constant: str
    pitch_modifier_value: str
    length_modifier_value: str


class PokemonCries:
    """Model to store the cries for all Pokémon in Red and Blue."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the PokemonCries object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._pokemon_cries_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "data"
            / "pokemon"
            / "cries.asm"
        )

        self.cries: list[PokemonCryData | None] = [None, *self._get_pokemon_cries()]

    def _get_pokemon_cries(self) -> list[str]:
        """Get the cries for all Pokémon in Red and Blue."""
        with self._pokemon_cries_path.open() as file:
            data = file.read().splitlines()

        filtered_data: list[list[str]] = [
            row.strip()
            .replace("\t", "")
            .split(";")[0]
            .strip()
            .replace("mon_cry", "")
            .strip()
            .split(", ")
            for row in data
            if row.strip().startswith("mon_cry")
        ]

        return [
            PokemonCryData(record[0], record[1], record[2]) for record in filtered_data
        ]
