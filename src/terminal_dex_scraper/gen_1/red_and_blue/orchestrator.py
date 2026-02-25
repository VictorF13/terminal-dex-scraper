"""Module that orchestrates the scraping of all of the data from Red and Blue.

This will initialize the individual scrapers for each type of data, call their methods
to scrape and store everything in files.
"""

from terminal_dex_scraper.gen_1.red_and_blue.scrapers.evolution_type_constants import (
    EvolutionTypeConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.growth_rate_constants import (
    GrowthRateConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.icon_constants import (
    IconConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.item_constants import (
    ItemConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.move_constants import (
    MoveConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.pokedex_constants import (
    PokedexConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.pokedex_order import PokedexOrder
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.pokemon_constants import (
    PokemonConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.sgb_palette_constants import (
    SGBPaletteConstants,
)
from terminal_dex_scraper.gen_1.red_and_blue.scrapers.type_constants import (
    TypeConstants,
)

# Getting constants
evolution_type_constants = EvolutionTypeConstants().serialize_records()
growth_rate_constants = GrowthRateConstants().serialize_records()
icon_constants = IconConstants().serialize_records()
move_constants = MoveConstants().serialize_records()
pokedex_constants = PokedexConstants().serialize_records()
pokemon_constants = PokemonConstants().serialize_records()
pokemon_constants_aliases = PokemonConstants().serialize_alias_records()
sgb_palette_constants = SGBPaletteConstants().serialize_records()
type_constants = TypeConstants().serialize_records()
item_constants = ItemConstants().serialize_records()
item_constants_aliases = ItemConstants().serialize_alias_records()
tmnum_constants = ItemConstants().serialize_tmnum_records()
machine_map_records = ItemConstants().serialize_machine_map_records()

# Getting data
pokedex_order_data = PokedexOrder().serialize_records()

# Missing data:
# evolutions and moves
# pokedex entries
# pokedex text
# pokemon base stats
# pokemon cries
# pokemon menu icons
# pokemon names
# pokemno palettes
# sgb palette data
