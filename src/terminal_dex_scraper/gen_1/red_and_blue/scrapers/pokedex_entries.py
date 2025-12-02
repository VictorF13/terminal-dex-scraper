"""Module to scrape the Pokédex entries from Red and Blue."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class PokedexEntryData:
    """Class representing a single Pokédex entry.

    Attributes:
        species (str): The species category name (e.g., "DRILL", "PARENT").
        height_feet (int): The height in feet.
        height_inches (int): The height in inches.
        weight (int): The weight in tenths of a pound.

    """

    species: str
    height_feet: int
    height_inches: int
    weight: int


class PokedexEntries:
    """Model to store the Pokédex entries for Red and Blue.

    Attributes:
        entries (list[PokedexEntryData | None]): A list of Pokédex entry data in
            internal index order. Index 0 is None for MISSINGNO, and subsequent
            indices correspond to the internal Pokémon index values.

    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the PokedexEntries object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._pokedex_entries_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "data"
            / "pokemon"
            / "dex_entries.asm"
        )

        self.entries: list[PokedexEntryData | None] = [
            None,
            *self._scrape_pokedex_entries(),
        ]

    def _scrape_pokedex_entries(self) -> list[PokedexEntryData]:
        """Scrape the Pokédex entries from the dex_entries.asm file.

        Returns:
            list[PokedexEntryData]: A list of Pokédex entry data.

        """
        with self._pokedex_entries_path.open() as file:
            lines = file.read().splitlines()

        pointers = self._collect_pointers(lines)
        entry_data = self._parse_entry_definitions(lines)
        return self._build_ordered_entries(pointers, entry_data)

    def _collect_pointers(self, lines: list[str]) -> list[str]:
        """Collect pointer names in order from the file.

        Args:
            lines (list[str]): The lines from the dex_entries.asm file.

        Returns:
            list[str]: A list of pointer names in order.

        """
        pointers: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("dw ") and stripped.endswith("DexEntry"):
                pointer_name = stripped[3:].strip()
                pointers.append(pointer_name)
            elif stripped == "assert_table_length NUM_POKEMON_INDEXES":
                break
        return pointers

    def _parse_entry_definitions(self, lines: list[str]) -> dict[str, PokedexEntryData]:
        """Parse entry definitions from the file.

        Args:
            lines (list[str]): The lines from the dex_entries.asm file.

        Returns:
            dict[str, PokedexEntryData]: A dictionary mapping entry names to data.

        """
        entry_data: dict[str, PokedexEntryData] = {}
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.endswith("DexEntry:"):
                entry_name = line.rstrip(":")
                entry = self._parse_single_entry(lines, i + 1)
                if entry:
                    entry_data[entry_name] = entry
            i += 1
        return entry_data

    def _parse_single_entry(
        self, lines: list[str], start_index: int
    ) -> PokedexEntryData | None:
        """Parse a single Pokédex entry starting at the given index.

        Args:
            lines (list[str]): The lines from the dex_entries.asm file.
            start_index (int): The index to start parsing from.

        Returns:
            PokedexEntryData | None: The parsed entry data, or None if parsing fails.

        """
        # Validate we have enough lines
        if start_index + 2 >= len(lines):
            return None

        # Get the three lines we need
        species_line = lines[start_index].strip()
        height_line = lines[start_index + 1].strip()
        weight_line = lines[start_index + 2].strip()

        # Validate format
        if (
            not species_line.startswith("db ")
            or not height_line.startswith("db ")
            or not weight_line.startswith("dw ")
        ):
            return None

        # Parse species name
        species = species_line[3:].split("@")[0].strip().strip('"')

        # Parse height
        height_parts = height_line[3:].split(";")[0].split(",")
        height_feet = int(height_parts[0].strip())
        height_inches = int(height_parts[1].strip()) if len(height_parts) > 1 else 0

        # Parse weight
        weight = int(weight_line[3:].split(";")[0].strip())

        return PokedexEntryData(
            species=species,
            height_feet=height_feet,
            height_inches=height_inches,
            weight=weight,
        )

    def _build_ordered_entries(
        self, pointers: list[str], entry_data: dict[str, PokedexEntryData]
    ) -> list[PokedexEntryData]:
        """Build the final ordered list of entries.

        Args:
            pointers (list[str]): The list of pointer names in order.
            entry_data (dict[str, PokedexEntryData]): The parsed entry data.

        Returns:
            list[PokedexEntryData]: The ordered list of entries.

        """
        entries: list[PokedexEntryData] = []
        for pointer in pointers:
            if pointer in entry_data:
                entries.append(entry_data[pointer])
            else:
                # MissingNoDexEntry or other missing entries
                entries.append(entry_data.get("MissingNoDexEntry"))
        return entries
