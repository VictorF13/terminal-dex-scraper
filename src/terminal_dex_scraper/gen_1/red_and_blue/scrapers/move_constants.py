"""Module to scrape the move constants for all moves in Red and Blue."""

from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


class MoveConstants:
    """Model to store the move constants and related information."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the MoveConstants object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            self._settings: Settings = Settings()
        else:
            self._settings = settings

        self._move_constants_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "constants"
            / "move_constants.asm"
        )

        move_constants = self._scrape_move_constants()

        self.constants: list[str | None] = move_constants[0]
        self.max_move_index: int | None = move_constants[1]
        self.cannot_move_index: int | None = move_constants[2]
        self.max_animation_index: int | None = move_constants[3]

    def _scrape_move_constants(
        self,
    ) -> tuple[list[str | None], int | None, int | None, int | None]:
        """Scrape the move constants for all moves in Red and Blue.

        Returns:
            list[str | None]: A list of move constants for all moves in Red and Blue.

        """
        move_constants: list[str | None] = []
        max_move_index: int | None = None
        cannot_move_index: int | None = None
        max_animation_index: int | None = None
        for text_line in self._move_constants_path.read_text().splitlines():
            line = text_line.split(";")[0].strip()
            if line.startswith("const "):
                parts = line.split()
                move_constants.append(parts[1])
            elif line.startswith("DEF NUM_ATTACKS"):
                max_move_index = len(move_constants) - 1
            elif line.strip().startswith("DEF CANNOT_MOVE"):
                cannot_move_index = 255
            elif line.strip().startswith("DEF NUM_ATTACK_ANIMS"):
                max_animation_index = len(move_constants) - 1

        return (
            move_constants,
            max_move_index,
            cannot_move_index,
            max_animation_index,
        )

    def get_move_index(self, move_constant: str) -> int:
        """Get the index of a move constant.

        Returns:
            int: The index of the move constant.

        """
        return self.constants.index(move_constant)
