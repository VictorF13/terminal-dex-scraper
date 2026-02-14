"""Module to scrape the Pokédex entries' text from Red and Blue."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class PokedexEntryPageData:
    """Class representing a single page of text for a Pokédex entry.

    Attributes:
        text_1 (str): The text for the first line of the page.
        text_2 (str): The text for the second line of the page.
        text_3 (str): The text for the third line of the page.

    """

    text_1: str
    text_2: str
    text_3: str


@dataclass
class PokedexEntryTextData:
    """Class representing the pages of text for a single Pokédex entry.

    Attributes:
        dex_text_id (str): The unique identifier for the Pokédex entry text.
        pages (list[PokedexEntryPageData]): A list of pages for the Pokédex entry.

    """

    dex_text_id: str
    pages: list[PokedexEntryPageData]


class PokedexEntryTexts:
    """Model to store the Pokédex entry texts for Red and Blue.

    Attributes:
        entry_texts (list[PokedexEntryTextData]): A list of Pokédex entry text data in
            internal order. Each entry corresponds to a unique `dex_text_id` that is
            used to relate to the Pokédex entries in `PokedexEntries`.

    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the PokedexEntryTexts object.

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
            / "dex_text.asm"
        )

        self.entry_texts: list[PokedexEntryTextData] = (
            self._scrape_pokedex_entry_texts()
        )

    def _scrape_pokedex_entry_texts(self) -> list[PokedexEntryTextData]:
        """Scrape the Pokédex entry texts from the dex_test.asm file.

        Returns:
            list[PokedexEntryTextData]: A list of Pokédex entry text data.

        """
        with self._pokedex_entries_path.open() as file:
            lines = [line.strip() for line in file]

        raw_text_per_entry = self._split_per_entry(lines)
        raw_entries = [self._split_per_page(entry) for entry in raw_text_per_entry]

        return [self._parse_entry_data(raw_entry) for raw_entry in raw_entries]

    def _split_per_entry(self, lines: list[str]) -> list[list[str]]:
        """Split the lines from the file into separate lists for each entry.

        Args:
            lines (list[str]): The lines from the file.

        Returns:
            list[list[str]]: A list of lists, where each inner list contains the lines
                for a single entry.

        """
        groups = []
        current = []
        inside_group = False

        for line in lines:
            if line.startswith("_") and line.endswith("::"):
                if current:
                    groups.append(current)
                current = [line]
                inside_group = True
                continue

            if inside_group:
                current.append(line)

                if line.endswith("dex"):
                    groups.append(current)
                    current = []
                    inside_group = False

        return groups

    def _split_per_page(self, lines: list[str]) -> tuple[str, list[list[str]]]:
        """Split the separated raw entries into separate lists for each entry.

        Args:
            lines (list[str]): The lines per entry.

        Returns:
            tuple[str, list[list[str]]]: A tuple where the first item is the
                `dex_text_id`, and the second item is a list of lists, where each inner
                list contains the lines for a single page of the entry.

        """
        dex_text_id = lines.pop(0).rstrip(":")
        lines.pop(-1)  # Remove the final "dex" line.

        groups = []
        current = []

        for line in lines:
            if not line:
                continue
            if line.startswith("page"):
                groups.append(current)
                current = []
            if '"' in line:
                content = line.split('"')[1]
                current.append(content)

        if current:
            groups.append(current)

        return dex_text_id, groups

    def _parse_entry_data(
        self, raw_entry: tuple[str, list[list[str]]]
    ) -> PokedexEntryTextData:
        """Parse the raw entry data into a PokedexEntryTextData object.

        Args:
            raw_entry (tuple[str, list[list[str]]]): The raw entry data, where the first
                item is the `dex_text_id`, and the second item is a list of lists, where
                each inner list contains the lines for a single page of the entry.

        Returns:
            PokedexEntryTextData: The parsed entry text data.

        """
        dex_text_id, raw_pages = raw_entry
        pages = [PokedexEntryPageData(*page) for page in raw_pages]
        return PokedexEntryTextData(dex_text_id=dex_text_id, pages=pages)
