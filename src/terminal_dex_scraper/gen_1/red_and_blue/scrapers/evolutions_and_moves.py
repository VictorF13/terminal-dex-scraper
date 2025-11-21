"""Module to scrape the level-up moves and evolutions for all Pokémon."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.evolution_type_constants import (
    EvolutionTypeConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.item_constants import (
    ItemConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.move_constants import (
    MoveConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.pokemon_constants import (
    PokemonConstants,
)

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class LevelEvolutionData:
    """Level evolution data for a single Pokémon."""

    evolution_type: int
    level: int
    species: int


@dataclass
class ItemEvolutionData:
    """Item evolution data for a single Pokémon."""

    evolution_type: int
    item: int
    min_level: int
    species: int


@dataclass
class TradeEvolutionData:
    """Trade evolution data for a single Pokémon."""

    evolution_type: int
    min_level: int
    species: int


@dataclass
class LevelUpMoveData:
    """Level-up move data for a single move for a single Pokémon."""

    level: int
    move: int


EvolutionData = LevelEvolutionData | ItemEvolutionData | TradeEvolutionData


@dataclass
class EvolutionAndMoveData:
    """Evolution and move data for a single Pokémon."""

    evolutions: list[EvolutionData]
    moves: list[LevelUpMoveData]


class EvolutionAndMoves:
    """Model to store the level-up moves and evolutions for all Pokémon."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the EvolutionAndMoves object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._evolution_and_moves_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "data"
            / "pokemon"
            / "evos_moves.asm"
        )

        self._evolution_type_constants_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "constants"
            / "pokemon_data_constants.asm"
        )

        self._pokemon_constants: PokemonConstants = PokemonConstants(self._settings)

        self._move_constants: MoveConstants = MoveConstants(self._settings)

        self._item_constants: ItemConstants = ItemConstants(self._settings)

        self._evolution_type_constants: EvolutionTypeConstants = EvolutionTypeConstants(
            self._settings
        )

        self.index_table, self.evolution_and_move_data = (
            self._get_evolution_and_move_data()
        )

    def _get_evolution_and_move_data(
        self,
    ) -> tuple[list[str], dict[str, EvolutionAndMoveData]]:
        with self._evolution_and_moves_path.open() as file:
            data = file.read().splitlines()

            relevant_data = [
                line.strip().replace("\t", "")
                for line in data
                if line.strip() not in [""] and not line.strip().startswith(";")
            ]

            index_table: list[str] = ["NoMonEvosMoves"]

            relevant_data.pop(0)
            relevant_data.pop(0)

            while relevant_data[0].strip() != "assert_table_length NUM_POKEMON_INDEXES":
                index_data = relevant_data.pop(0).strip().split()[1]
                index_table.append(index_data)
            relevant_data.pop(0)

            processed_evolution_and_move_data_dict = self._process_evolution_raw_list(
                relevant_data
            )

            return index_table, processed_evolution_and_move_data_dict

    def _process_evolution_raw_list(
        self, evolution_raw_list: list[str]
    ) -> dict[str, EvolutionAndMoveData]:
        raw_data_per_record = self._split_raw_data_into_records(evolution_raw_list)
        evolution_and_move_raw_data_dict = self._parse_records_into_raw_data_dict(
            raw_data_per_record
        )
        return self._process_raw_data_into_structured_data(
            evolution_and_move_raw_data_dict
        )

    def _split_raw_data_into_records(
        self, evolution_raw_list: list[str]
    ) -> list[list[str]]:
        """Split raw data list into individual record lists.

        Args:
            evolution_raw_list: The raw list of evolution and move data lines.

        Returns:
            A list of record lists, where each record list contains the raw data
            for a single Pokémon.

        """
        _number_of_sections: int = 2
        raw_data_per_record: list[list[str]] = []
        break_point_count: int = 0
        current_record_raw_data: list[str] = []
        for line in evolution_raw_list:
            current_record_raw_data.append(line)
            if line == "db 0":
                break_point_count += 1
                if break_point_count == _number_of_sections:
                    raw_data_per_record.append(current_record_raw_data)
                    current_record_raw_data = []
                    break_point_count = 0
        return raw_data_per_record

    def _parse_records_into_raw_data_dict(
        self, raw_data_per_record: list[list[str]]
    ) -> dict[str, dict[str, list[str]]]:
        """Parse record lists into a dictionary of evolution and move raw data.

        Args:
            raw_data_per_record: List of record lists containing raw data.

        Returns:
            Dictionary mapping record names to their evolution and move raw data.

        """
        evolution_and_move_raw_data_dict: dict[str, dict[str, list[str]]] = {}
        for record_list in raw_data_per_record:
            record_name = record_list[0].split(":")[0]
            full_list: list[list[str]] = []
            raw_list: list[str] = []
            for line in record_list[1:]:
                if line != "db 0":
                    raw_list.append(line.replace("db ", ""))
                else:
                    full_list.append(raw_list)
                    raw_list = []

            evolution_and_move_raw_data_dict[record_name] = {
                "evolution_raw_data": full_list[0],
                "move_raw_data": full_list[1],
            }
        return evolution_and_move_raw_data_dict

    def _process_raw_data_into_structured_data(
        self,
        evolution_and_move_raw_data_dict: dict[str, dict[str, list[str]]],
    ) -> dict[str, EvolutionAndMoveData]:
        """Process raw evolution and move data into structured objects.

        Args:
            evolution_and_move_raw_data_dict: Dictionary mapping record names to
                their raw evolution and move data.

        Returns:
            Dictionary mapping record names to their structured evolution and
            move data.

        """
        processed_evolution_and_move_data_dict: dict[str, EvolutionAndMoveData] = {}
        for record_name, record_data in evolution_and_move_raw_data_dict.items():
            evolutions = self._process_evolution_data(record_data["evolution_raw_data"])
            moves = self._process_move_data(record_data["move_raw_data"])
            evolution_and_move_data = EvolutionAndMoveData(evolutions, moves)
            processed_evolution_and_move_data_dict[record_name] = (
                evolution_and_move_data
            )
        return processed_evolution_and_move_data_dict

    def _process_evolution_data(
        self, evolution_raw_data: list[str]
    ) -> list[EvolutionData]:
        """Process raw evolution data into structured evolution objects.

        Args:
            evolution_raw_data: List of raw evolution data strings.

        Returns:
            List of structured evolution data objects.

        """
        evolutions: list[EvolutionData] = []
        for item in evolution_raw_data:
            evolution_info = item.split(", ")
            evolution_type = self._evolution_type_constants.constants[evolution_info[0]]

            if evolution_type == 1:
                min_level = int(evolution_info[1])
                species = self._pokemon_constants.get_pokemon_index(evolution_info[2])
                evolution_data = LevelEvolutionData(evolution_type, min_level, species)
                evolutions.append(evolution_data)
            elif evolution_type == 2:  # noqa: PLR2004
                evolution_item = self._item_constants.get_item_index(evolution_info[1])
                min_level = int(evolution_info[2])
                species = self._pokemon_constants.get_pokemon_index(evolution_info[3])
                evolution_data = ItemEvolutionData(
                    evolution_type, evolution_item, min_level, species
                )
                evolutions.append(evolution_data)
            elif evolution_type == 3:  # noqa: PLR2004
                min_level = int(evolution_info[1])
                species = self._pokemon_constants.get_pokemon_index(evolution_info[2])
                evolution_data = TradeEvolutionData(evolution_type, min_level, species)
                evolutions.append(evolution_data)
        return evolutions

    def _process_move_data(self, move_raw_data: list[str]) -> list[LevelUpMoveData]:
        """Process raw move data into structured move objects.

        Args:
            move_raw_data: List of raw move data strings.

        Returns:
            List of structured level-up move data objects.

        """
        moves: list[LevelUpMoveData] = []
        for move_line in move_raw_data:
            move_info = move_line.split(", ")
            level = int(move_info[0])
            move = self._move_constants.get_move_index(move_info[1])
            move_data = LevelUpMoveData(level, move)
            moves.append(move_data)
        return moves
