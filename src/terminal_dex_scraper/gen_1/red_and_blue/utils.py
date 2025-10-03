"""Utility functions for Pokémon Red and Blue."""

from click import secho
from git import Repo

from terminal_dex_scraper.config.settings import Settings


def clone_repository(settings: Settings | None = None) -> Repo:
    """Clone the Pokémon Red and Blue repository if it is not already cloned.

    This will clone the repository to the default Pokémon Red and Blue disassembly path,
    and will clone from the default Red and Blue disassembly repository, unless
    different settings are passed.

    Args:
        settings: The settings to use. If not provided, the default settings will be
            used.

    Returns:
        Repo: The cloned repository.

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
        pokemon_red_and_blue_disassembly = Repo.clone_from(
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
        pokemon_red_and_blue_disassembly = Repo(
            settings.pokemon_red_and_blue_disassembly_path
        )

    return pokemon_red_and_blue_disassembly
