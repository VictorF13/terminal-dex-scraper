"""Module to scrape the item constants for Pokémon Red and Blue."""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from terminal_dex_scraper.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class _ItemConstantsParser:
    """Parser for the Red and Blue `item_constants.asm` file."""

    lines: Sequence[str]
    constants: list[str | None] = field(default_factory=list)
    value_to_name: dict[int, str] = field(default_factory=dict)
    aliases: dict[str, str] = field(default_factory=dict)
    pending_aliases: list[tuple[str, int]] = field(default_factory=list)
    machine_move_map: dict[str, str] = field(default_factory=dict)
    machine_map: dict[str, str] = field(default_factory=dict)
    tmnum_by_value: dict[int, str] = field(default_factory=dict)
    special_values: dict[str, int] = field(default_factory=dict)
    numeric_defines: dict[str, int] = field(default_factory=dict)
    const_value: int | None = None
    inside_macro: bool = False

    def parse(
        self,
    ) -> tuple[
        list[str | None],
        dict[str, str],
        dict[str, str],
        list[str | None],
        dict[str, str],
        dict[str, int],
    ]:
        """Parse all relevant lines and return the collected structures."""
        for raw_line in self.lines:
            line = self._strip_comments(raw_line)
            if not line:
                continue
            if self._handle_macro_tokens(line):
                continue
            if self.inside_macro:
                continue
            self._dispatch_line(line)

        self._resolve_pending_aliases()
        self._inject_unused_tmnum()
        tmnum_constants = self._build_tmnum_constants()

        return (
            self.constants,
            self.aliases,
            self.machine_move_map,
            tmnum_constants,
            self.machine_map,
            self.special_values,
        )

    @staticmethod
    def _strip_comments(line: str) -> str:
        return line.split(";", maxsplit=1)[0].strip()

    def _handle_macro_tokens(self, line: str) -> bool:
        if line.startswith("MACRO"):
            self.inside_macro = True
            return True
        if line.startswith("ENDM"):
            self.inside_macro = False
            return True
        return False

    def _dispatch_line(self, line: str) -> None:
        if line == "const_def":
            self._handle_const_def()
        elif line.startswith("const_next"):
            self._handle_const_next(line)
        elif line.startswith("const "):
            self._handle_const(line)
        elif line.startswith("add_hm"):
            self._handle_add_hm(line)
        elif line.startswith("add_tm"):
            self._handle_add_tm(line)
        elif line.startswith("ASSERT"):
            return
        elif line.startswith("DEF "):
            self._handle_def(line)

    def _handle_const_def(self) -> None:
        self._set_const_value(0)
        self._ensure_length(0)

    def _handle_const_next(self, line: str) -> None:
        _, value_str = line.split(maxsplit=1)
        next_value = self._evaluate_expression(value_str)
        self._ensure_length(next_value)
        self._set_const_value(next_value)

    def _handle_const(self, line: str) -> None:
        parts = line.split()
        name = parts[1]
        if self.const_value is None:
            message = "const_def must appear before const declarations."
            raise ValueError(message)
        self._ensure_length(self.const_value)
        self.constants[self.const_value] = name
        self.value_to_name[self.const_value] = name
        self._set_numeric_define(name, self.const_value)
        self._set_const_value(self.const_value + 1)
        self._resolve_pending_aliases()

    def _handle_add_hm(self, line: str) -> None:
        move_name = line.split()[1]
        hm_item_name = f"HM_{move_name}"
        if self.const_value is None:
            message = "const_value is not initialized before add_hm."
            raise ValueError(message)
        self._ensure_length(self.const_value)
        self.constants[self.const_value] = hm_item_name
        self.value_to_name[self.const_value] = hm_item_name
        self._set_numeric_define(hm_item_name, self.const_value)
        self._set_const_value(self.const_value + 1)
        self._resolve_pending_aliases()

        num_tms = self.numeric_defines["NUM_TMS"]
        tmhm_value = self.numeric_defines["__tmhm_value__"]
        hm_index = tmhm_value - num_tms
        self._set_numeric_define("HM_VALUE", hm_index, track_special=True)

        machine_move_name = f"HM{hm_index:02d}_MOVE"
        self.machine_move_map[machine_move_name] = move_name
        self.machine_map[hm_item_name] = machine_move_name

        tmnum_name = f"{move_name}_TMNUM"
        tmnum_value = tmhm_value
        self._set_numeric_define(tmnum_name, tmnum_value)
        self.tmnum_by_value[tmnum_value] = tmnum_name
        self._set_numeric_define("__tmhm_value__", tmhm_value + 1, track_special=True)

    def _handle_add_tm(self, line: str) -> None:
        move_name = line.split()[1]
        tm_item_name = f"TM_{move_name}"
        if self.const_value is None:
            message = "const_value is not initialized before add_tm."
            raise ValueError(message)
        self._ensure_length(self.const_value)
        self.constants[self.const_value] = tm_item_name
        self.value_to_name[self.const_value] = tm_item_name
        self._set_numeric_define(tm_item_name, self.const_value)
        self._set_const_value(self.const_value + 1)
        self._resolve_pending_aliases()

        tmhm_value = self.numeric_defines["__tmhm_value__"]
        machine_move_name = f"TM{tmhm_value:02d}_MOVE"
        self.machine_move_map[machine_move_name] = move_name
        self.machine_map[tm_item_name] = machine_move_name

        tmnum_name = f"{move_name}_TMNUM"
        self._set_numeric_define(tmnum_name, tmhm_value)
        self.tmnum_by_value[tmhm_value] = tmnum_name
        self._set_numeric_define("__tmhm_value__", tmhm_value + 1, track_special=True)

    def _handle_def(self, line: str) -> None:
        parts = line.split()
        name = parts[1]

        if "+=" in parts:
            increment = self._evaluate_expression(parts[-1])
            updated_value = self.numeric_defines[name] + increment
            self._set_numeric_define(name, updated_value, track_special=True)
            return

        if "=" in parts:
            expression = " ".join(parts[3:])
            value = self._evaluate_expression(expression)
            self._set_numeric_define(name, value, track_special=True)
            if name == "UNUSED_TMNUM":
                self.tmnum_by_value[value] = name
            return

        if "EQU" in parts:
            expression = " ".join(parts[3:])
            value = self._evaluate_expression(expression)
            tokens = expression.split()
            is_single_token = len(tokens) == 1
            canonical = self.value_to_name.get(value)
            if is_single_token and canonical is not None and canonical == tokens[0]:
                self._register_alias(name, value)
            else:
                self._set_numeric_define(name, value, track_special=True)
                if name == "UNUSED_TMNUM":
                    self.tmnum_by_value[value] = name

    def _set_const_value(self, value: int) -> None:
        self.const_value = value
        self.numeric_defines["const_value"] = value

    def _ensure_length(self, index: int) -> None:
        if index >= len(self.constants):
            padding = index + 1 - len(self.constants)
            self.constants.extend([None] * padding)

    def _set_numeric_define(
        self, name: str, value: int, *, track_special: bool = False
    ) -> None:
        self.numeric_defines[name] = value
        if track_special and not name.endswith("_TMNUM"):
            self.special_values[name] = value

    def _register_alias(self, name: str, value: int) -> None:
        self._set_numeric_define(name, value)
        canonical = self.value_to_name.get(value)
        if canonical is not None:
            self.aliases[name] = canonical
        else:
            self.pending_aliases.append((name, value))

    def _resolve_pending_aliases(self) -> None:
        if not self.pending_aliases:
            return
        remaining: list[tuple[str, int]] = []
        for alias_name, alias_value in self.pending_aliases:
            canonical = self.value_to_name.get(alias_value)
            if canonical is None:
                remaining.append((alias_name, alias_value))
            else:
                self.aliases[alias_name] = canonical
        self.pending_aliases = remaining

    def _evaluate_expression(self, expression: str) -> int:
        tokens = expression.replace("+", " + ").replace("-", " - ").split()
        total = 0
        operator = "+"
        for token in tokens:
            if token in {"+", "-"}:
                operator = token
                continue
            value = self._token_to_value(token, expression)
            total = total + value if operator == "+" else total - value
        return total

    def _token_to_value(self, token: str, expression: str) -> int:
        if token.startswith("$"):
            return int(token[1:], 16)
        if token.isdigit():
            return int(token, 10)
        if token in self.numeric_defines:
            return self.numeric_defines[token]
        message = f"Unknown token '{token}' in expression '{expression}'."
        raise ValueError(message)

    def _inject_unused_tmnum(self) -> None:
        if "UNUSED_TMNUM" in self.numeric_defines:
            value = self.numeric_defines["UNUSED_TMNUM"]
            previous = self.tmnum_by_value.setdefault(value, "UNUSED_TMNUM")
            _ = previous

    def _build_tmnum_constants(self) -> list[str | None]:
        max_index = max(self.tmnum_by_value) if self.tmnum_by_value else 0
        tmnum_constants: list[str | None] = [None] * (max_index + 1)
        for index, tmnum_name in sorted(self.tmnum_by_value.items()):
            tmnum_constants[index] = tmnum_name
        return tmnum_constants


class ItemConstants:
    """Model to store the item constants and related information."""

    constants: list[str | None]
    aliases: dict[str, str]
    machine_move_map: dict[str, str]
    tmnum_constants: list[str | None]
    machine_map: dict[str, str]
    special_values: dict[str, int]

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the ItemConstants object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        self._settings: Settings = settings if settings is not None else Settings()
        self._item_constants_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "constants"
            / "item_constants.asm"
        )

        (
            self.constants,
            self.aliases,
            self.machine_move_map,
            self.tmnum_constants,
            self.machine_map,
            self.special_values,
        ) = self._scrape_item_constants()

    def _scrape_item_constants(
        self,
    ) -> tuple[
        list[str | None],
        dict[str, str],
        dict[str, str],
        list[str | None],
        dict[str, str],
        dict[str, int],
    ]:
        """Scrape the item constants for an assembler constants file."""
        lines = self._item_constants_path.read_text().splitlines()
        parser = _ItemConstantsParser(lines)
        return parser.parse()
