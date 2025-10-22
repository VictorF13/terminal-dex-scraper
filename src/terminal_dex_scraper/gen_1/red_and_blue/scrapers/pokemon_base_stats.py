"""Module to scrape the base stats table for all Pokémon in Red and Blue."""

from pathlib import Path

from PIL import Image

from terminal_dex_scraper.config.settings import Settings
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.growth_rate_constants import (
    GrowthRateConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.move_constants import (
    MoveConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.pokedex_constants import (
    PokedexConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.type_constants import (
    TypeConstants,
)


class SpriteDimensions:
    """Dimensions of a Pokémon sprite."""

    def __init__(self, width: int, height: int) -> None:
        """Initialize the SpriteDimensions object.

        Args:
            width (int): The width of the sprite in pixels.
            height (int): The height of the sprite in pixels.

        """
        self.width: int = width
        self.height: int = height


class PicturePaths:
    """Paths to the front and back pictures of a Pokémon."""

    def __init__(self, front: Path, back: Path) -> None:
        """Initialize the PicturePaths object.

        Args:
            front (Path): The path to the front picture.
            back (Path): The path to the back picture.

        """
        self.front: Path = front
        self.back: Path = back


class BaseStats:
    """Base stats for a single Pokémon."""

    def __init__(
        self, hp: int, attack: int, defense: int, speed: int, special: int
    ) -> None:
        """Initialize the BaseStats object.

        Args:
            hp (int): The HP stat.
            attack (int): The Attack stat.
            defense (int): The Defense stat.
            speed (int): The Speed stat.
            special (int): The Special stat.

        """
        self.hp: int = hp
        self.attack: int = attack
        self.defense: int = defense
        self.speed: int = speed
        self.special: int = special


class PokemonBaseStatsRecord:
    """Record containing parsed base stats for a Pokémon."""

    def __init__(
        self,
        pokedex_index: int,
        base_stats: BaseStats,
        types: list[int],
        catch_rate: int,
        base_experience_yield: int,
        sprite_dimensions: SpriteDimensions,
        picture_paths: PicturePaths,
        level_1_moveset: list[int],
        growth_rate: int,
        machine_learnset: list[int],
    ) -> None:
        """Initialize the PokemonBaseStatsRecord object.

        Args:
            pokedex_index (int): The Pokédex index of the Pokémon.
            base_stats (BaseStats): The base stats of the Pokémon.
            types (list[int]): The type indices of the Pokémon.
            catch_rate (int): The catch rate of the Pokémon.
            base_experience_yield (int): The base experience yield.
            sprite_dimensions (SpriteDimensions): The sprite dimensions.
            picture_paths (PicturePaths): The paths to the pictures.
            level_1_moveset (list[int]): The level 1 moveset indices.
            growth_rate (int): The growth rate index.
            machine_learnset (list[int]): The machine learnset moves indices.

        """
        self.pokedex_index: int = pokedex_index
        self.base_stats: BaseStats = base_stats
        self.types: list[int] = types
        self.catch_rate: int = catch_rate
        self.base_experience_yield: int = base_experience_yield
        self.sprite_dimensions: SpriteDimensions = sprite_dimensions
        self.picture_paths: PicturePaths = picture_paths
        self.level_1_moveset: list[int] = level_1_moveset
        self.growth_rate: int = growth_rate
        self.machine_learnset: list[int] = machine_learnset


class PokemonBaseStats:
    """Model to store the base stats table for all Pokémon in Red and Blue."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the PokemonBaseStats object.

        Args:
            settings (Settings | None, optional): The settings to use. If not provided,
                the default settings will be used. Defaults to None.

        """
        if settings is None:
            settings = Settings()
        self._settings: Settings = settings

        self._pokemon_base_stats_path: Path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / "data"
            / "pokemon"
            / "base_stats.asm"
        )
        self._pokedex_constants: PokedexConstants = PokedexConstants(self._settings)
        self._type_constants: TypeConstants = TypeConstants(self._settings)
        self._move_constants: MoveConstants = MoveConstants(self._settings)
        self._growth_rate_constants: GrowthRateConstants = GrowthRateConstants(
            self._settings
        )

        self.base_stats_files_paths: list[Path] = self._get_list_of_base_stats_files()
        self.base_stats_records: list[PokemonBaseStatsRecord] = [
            self._get_pokemon_base_stats(file_path)
            for file_path in self.base_stats_files_paths
        ]

    def _get_list_of_base_stats_files(self) -> list[Path]:
        """Get the list of base stats files.

        Each path is a file that contains the base stats for a single Pokémon. They are
        Pokédex ordered, strictly.

        Returns:
            list[Path]: A list of base stats files.

        """
        base_stats_files_paths: list[Path] = []
        for text_line in self._pokemon_base_stats_path.read_text().splitlines():
            line = text_line.strip()
            if line.startswith("INCLUDE "):
                parts = line.split()
                base_stats_files_paths.append(
                    self._settings.pokemon_red_and_blue_disassembly_path
                    / Path(parts[1].replace('"', ""))
                )
        return base_stats_files_paths

    def _get_pokemon_base_stats(
        self, pokemon_base_stats_file_path: Path
    ) -> PokemonBaseStatsRecord:
        """Get the base stats for a single Pokémon.

        Args:
            pokemon_base_stats_file_path (Path): The path to the base stats file for a
                single Pokémon.

        Returns:
            PokemonBaseStatsRecord: The parsed base stats for a single Pokémon.

        """
        data_lines = [
            line.split(";")[0].strip()
            for line in pokemon_base_stats_file_path.read_text().splitlines()
            if line.split(";")[0].strip()
        ]

        # Get the Pokédex index
        pokedex_constant_line = data_lines.pop(0)
        pokedex_constant = pokedex_constant_line.split()[1]
        pokedex_index = self._pokedex_constants.get_pokedex_index(pokedex_constant)

        # Get the Base Stats
        base_stats_line = data_lines.pop(0)
        base_stats_data = [
            int(item.strip())
            for item in base_stats_line.split("db")[1].strip().split(",")
        ]
        stats = BaseStats(
            hp=base_stats_data[0],
            attack=base_stats_data[1],
            defense=base_stats_data[2],
            speed=base_stats_data[3],
            special=base_stats_data[4],
        )

        # Get the Types
        types_line = data_lines.pop(0)
        types: list[int] = [
            self._type_constants.get_type_index(item.strip())
            for item in types_line.split("db")[1].strip().split(",")
        ]

        # Get the Catch Rate
        catch_rate_line = data_lines.pop(0)
        catch_rate = int(catch_rate_line.split()[1])

        # Get the Base Experience Yield
        base_experience_yield_line = data_lines.pop(0)
        base_experience_yield = int(base_experience_yield_line.split()[1])

        # Popping the sprite dimensions and pointers
        sprite_path_line = data_lines.pop(0)
        sprite_path = (
            self._settings.pokemon_red_and_blue_disassembly_path
            / sprite_path_line.split()[1].replace('"', "")
        ).with_suffix(".png")
        with Image.open(sprite_path) as image:
            width, height = image.size
            sprite_dimensions = SpriteDimensions(width=width, height=height)

        back_picture_path = sprite_path.with_stem(sprite_path.stem + "b")
        parts = list(back_picture_path.parts)
        parts[-2] = "back"
        back_picture_path = Path(*parts)

        picture_paths = PicturePaths(front=sprite_path, back=back_picture_path)

        _ = data_lines.pop(0)

        # Get Level 1 Moveset
        level_1_moveset_line = data_lines.pop(0)
        level_1_moveset: list[int] = [
            self._move_constants.get_move_index(item.strip())
            for item in level_1_moveset_line.split("db")[1].strip().split(",")
        ]

        # Get Growth Rate
        growth_rate_line = data_lines.pop(0)
        growth_rate = self._growth_rate_constants.get_growth_rate_index(
            growth_rate_line.split()[1]
        )

        # Get Machine Learnset
        machine_learnset: list[int] = []
        machine_learnset_lines = ",".join(
            [
                line.replace("tmhm", "").replace("\\", "").strip()
                for line in data_lines
                if line.strip() not in ["db 0", "UNUSED", "db %11111111"]
            ]
        ).split(",")
        machine_learnset = [
            self._move_constants.get_move_index(item.strip())
            for item in machine_learnset_lines
            if item.strip() != ""
        ]

        # Returning everything
        return PokemonBaseStatsRecord(
            pokedex_index=pokedex_index,
            base_stats=stats,
            types=types,
            catch_rate=catch_rate,
            base_experience_yield=base_experience_yield,
            sprite_dimensions=sprite_dimensions,
            picture_paths=picture_paths,
            level_1_moveset=level_1_moveset,
            growth_rate=growth_rate,
            machine_learnset=machine_learnset,
        )
