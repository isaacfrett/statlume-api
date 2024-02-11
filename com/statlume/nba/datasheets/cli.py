import click

from com.statlume.nba.subcommands.create import create
from com.statlume.nba.subcommands.delete import delete


@click.group(no_args_is_help=True, add_help_option=False)
def datasheets() -> None:
    "Pictures and xlsx datasheets"


datasheets.add_command(create)
datasheets.add_command(delete)
