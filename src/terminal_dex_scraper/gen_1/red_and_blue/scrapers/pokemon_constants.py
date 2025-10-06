"""Module to scrape the constant for all Pokémon in Red and Blue."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class PokemonConstants:
    """Model to store the Pokémon constants and related information.

    Attributes:
        constants (list[str | None]): A list of constant names for all Pokémon constants
            in Red and Blue. None represents something with an index but no constant
            name.
        aliases (dict[str, str]): A dictionary of constant aliases for all Pokémon
            constants in Red and Blue. The key is the alias, and the value is the
            constant name that can be referenced to the respective Pokémon constant.
        max_pokemon_index (int): The maximum Pokémon index. This alias is set in the
            codebase to the last Pokémon index, which is why it's set here.

    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the PokemonConstants object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()

        self._pokemon_constants_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "constants"
            / "pokemon_constants.asm"
        )

        self.constants: list[str | None] = self._scrape_pokemon_constants()
        self.aliases: dict[str, str] = self._scrape_pokemon_constants_aliases()
        self.max_pokemon_index: int = len(self.constants) - 1

    def _scrape_pokemon_constants(self) -> list[str | None]:
        """Scrape the constant names for all Pokémon in Red and Blue.

        This will scrape the constant names for all Pokémon and store them in a list
        where each position/index represents the constant value for the Pokémon, and the
        value represents the constant name.

        Not everything present in the constants is a Pokémon. For example, the ghost
        from Lavender Town and the Fossil Aerodactyl are present here.

        Returns:
            list[str | None]: A list of constant names for all Pokémon in Red and Blue.
                None represents something with an index but no constant name.

        """
        pokemon_constants: list[str | None] = []
        for text_line in self._pokemon_constants_path.read_text().splitlines():
            line = text_line.strip()
            if line.startswith("const "):
                parts = line.split()
                pokemon_constants.append(parts[1])
            elif line.startswith("const_skip"):
                pokemon_constants.append(None)

        return pokemon_constants

    def _scrape_pokemon_constants_aliases(
        self,
    ) -> dict[str, str]:
        """Scrape all Pokémon constants aliases.

        Some Pokémon have aliases in the codebase, for example, `STARTER1` is an alias
        for `CHARMANDER`. This will scrape all such aliases.

        Returns:
            dict[str, str]: A dictionary of constant aliases for all Pokémon in Red and
                Blue. The key is the alias, and the value is the constant name that can
                be referenced to the respective Pokémon constant.

        """
        cnt_parts_aliases = 4

        pokemon_constants_aliases: dict[str, str] = {}
        for text_line in self._pokemon_constants_path.read_text().splitlines():
            line = text_line.strip()
            parts = line.split()
            if len(parts) == cnt_parts_aliases and parts[0] == "DEF":
                pokemon_constants_aliases.update({parts[1]: parts[3]})
        return pokemon_constants_aliases
