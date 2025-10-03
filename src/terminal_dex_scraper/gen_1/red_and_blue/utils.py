"""Utility functions for Pokémon Red and Blue."""

from pathlib import Path

from click import secho
from git import Repo

from terminal_dex_scraper.config.settings import Settings


def clone_red_and_blue_codebase(settings: Settings | None = None) -> None:
    """Clone the Pokémon Red and Blue repository if it is not already cloned.

    This will clone the repository to the default Pokémon Red and Blue disassembly path,
    and will clone from the default Red and Blue disassembly repository, unless
    different settings are passed.

    Args:
        settings (Settings | None, optional): The settings to use. If not provided, the
            default settings will be used. Defaults to None.

    """
    if settings is None:
        settings = Settings()

    # Cloning repository if not already cloned
    secho(
        "Checking if Pokémon Red and Blue disassembly is already cloned...", fg="yellow"
    )
    if not settings.pokemon_red_and_blue_disassembly_path.exists():
        secho(
            (
                "Pokémon Red and Blue disassembly not found, cloning from "
                f"`{settings.pokemon_red_and_blue_disassembly_repo}` to "
                f"`{settings.pokemon_red_and_blue_disassembly_path}`..."
            ),
            fg="yellow",
        )
        _ = Repo.clone_from(
            Settings().pokemon_red_and_blue_disassembly_repo,
            settings.pokemon_red_and_blue_disassembly_path,
        )
        secho(
            (
                "Pokémon Red and Blue disassembly cloned to "
                f"`{settings.pokemon_red_and_blue_disassembly_path}`."
            ),
            fg="green",
        )
    else:
        secho(
            "Pokémon Red and Blue disassembly found, using existing clone...",
            fg="yellow",
        )


def fix_mew_code_entries(settings: Settings | None = None) -> None:
    """Apply local fixes so that Mew is treated as a regular Pokémon entry.

    This is needed because Mew was a last minute addition to the game, and the code was
    not properly integrated into the game code.

    Args:
        settings (Settings | None, optional): The settings to use. If not provided, the
            default settings will be used. Defaults to None.

    """
    if settings is None:
        settings = Settings()

    repo_path = settings.pokemon_red_and_blue_disassembly_path

    secho("Applying local fixes for Mew entries...", fg="yellow")

    base_stats_path = repo_path / "data" / "pokemon" / "base_stats.asm"
    main_path = repo_path / "main.asm"
    home_pokemon_path = repo_path / "home" / "pokemon.asm"
    pics_path = repo_path / "gfx" / "pics.asm"

    _remove_mew_discount(base_stats_path)
    _restore_mew_base_stats_include(base_stats_path)
    _remove_mew_include_from_main(main_path)
    _remove_mew_get_mon_header_branch(home_pokemon_path)
    _ensure_mew_pictures_present(pics_path)

    secho("Finished applying Mew fixes.", fg="green")


# Helpers
def _remove_mew_discount(base_stats_path: Path) -> None:
    target_line = "\tassert_table_length NUM_POKEMON - 1 ; discount Mew"
    _remove_exact_line(base_stats_path, target_line)


def _restore_mew_base_stats_include(base_stats_path: Path) -> None:
    desired_lines = [
        'INCLUDE "data/pokemon/base_stats/mew.asm"',
        "\tassert_table_length NUM_POKEMON",
    ]

    lines = _read_lines(base_stats_path)

    while lines and lines[-1] == "":
        _ = lines.pop()

    while lines and lines[-1] in desired_lines:
        _ = lines.pop()

    lines.extend(desired_lines)

    _write_lines_if_changed(base_stats_path, lines)


def _remove_mew_include_from_main(main_path: Path) -> None:
    target_line = 'INCLUDE "data/pokemon/mew.asm"'
    _remove_exact_line(main_path, target_line)


def _remove_mew_get_mon_header_branch(home_pokemon_path: Path) -> None:
    lines = _read_lines(home_pokemon_path)

    filtered_lines = [
        line for line in lines if line not in {"\tcp MEW", "\tjr z, .mew"}
    ]

    if filtered_lines != lines:
        lines = filtered_lines

    block = [
        "\tjr .done",
        ".mew",
        "\tld hl, MewBaseStats",
        "\tld de, wMonHeader",
        "\tld bc, BASE_DATA_SIZE",
        "\tld a, BANK(MewBaseStats)",
        "\tcall FarCopyData",
    ]

    lines = _remove_block(lines, block)

    _write_lines_if_changed(home_pokemon_path, lines)


def _ensure_mew_pictures_present(pics_path: Path) -> None:
    insert_lines = [
        'MewPicFront:: INCBIN "gfx/pokemon/front/mew.pic"',
        'MewPicBack::  INCBIN "gfx/pokemon/back/mewb.pic"',
    ]

    lines = _read_lines(pics_path)

    if all(line in lines for line in insert_lines):
        return

    anchor = 'VictreebelPicBack::    INCBIN "gfx/pokemon/back/victreebelb.pic"'

    new_lines: list[str] = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if not inserted and line == anchor:
            new_lines.extend(insert_lines)
            inserted = True

    if inserted:
        _write_lines_if_changed(pics_path, new_lines)


def _remove_exact_line(path: Path, target_line: str) -> None:
    lines = _read_lines(path)
    if target_line not in lines:
        return

    new_lines = [line for line in lines if line != target_line]
    _write_lines_if_changed(path, new_lines)


def _remove_block(lines: list[str], block: list[str]) -> list[str]:
    block_length = len(block)
    i = 0
    while i <= len(lines) - block_length:
        if all(lines[i + k].rstrip() == block[k] for k in range(block_length)):
            del lines[i : i + block_length]
            break
        i += 1
    return lines


def _read_lines(path: Path) -> list[str]:
    return path.read_text().splitlines()


def _write_lines_if_changed(path: Path, new_lines: list[str]) -> None:
    existing_lines = path.read_text().splitlines()
    if existing_lines == new_lines:
        return

    _ = path.write_text("\n".join(new_lines) + "\n")
