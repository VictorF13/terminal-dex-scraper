"""Module to scrape evolution type constants for all evolution types in Red and Blue."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class EvolutionTypeConstants:
    """Model to store the evolution type constants and related information.

    Attributes:
        constants (dict[str, int]): A dictionary mapping evolution type constant names
            to their values.

    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the EvolutionTypeConstants object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._evolution_type_constants_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "constants"
            / "pokemon_data_constants.asm"
        )

        self.constants: dict[str, int] = self._scrape_evolution_type_constants()

    def _scrape_evolution_type_constants(self) -> dict[str, int]:
        """Scrape the evolution type constants for all evolution types in Red and Blue.

        Returns:
            dict[str, int]: A dictionary mapping evolution type constant names to their
                values.

        """
        with self._evolution_type_constants_path.open() as file:
            data = file.read().splitlines()

        relevant_data = [
            line.strip().replace("\t", "") for line in data if line.strip() not in [""]
        ]

        while relevant_data[0].strip() != "; Evolution types":
            relevant_data.pop(0)

        evolution_type_constants: dict[str, int] = {}

        constant_value: int = 0
        constant_name: str = ""

        while relevant_data[0].strip() != (
            "; evolution data (see data/pokemon/evos_moves.asm)"
        ):
            line = relevant_data[0].strip()
            if line.startswith(";"):
                relevant_data.pop(0)
                continue

            if line.startswith("const_def"):
                constant_value = int(line.split()[1])
                relevant_data.pop(0)
            elif line.startswith("const"):
                constant_name = line.split()[1]
                evolution_type_constants[constant_name] = constant_value
                relevant_data.pop(0)
                constant_value += 1

        return evolution_type_constants

    def get_evolution_type_name(self, value: int) -> str:
        """Get the evolution type constant name for a given value.

        Args:
            value (int): The evolution type value.

        Returns:
            str: The evolution type constant name.

        Raises:
            ValueError: If the value does not correspond to any evolution type constant.

        """
        for constant_name, constant_value in self.constants.items():
            if constant_value == value:
                return constant_name
        message = f"No evolution type constant found for value: {value}"
        raise ValueError(message)
