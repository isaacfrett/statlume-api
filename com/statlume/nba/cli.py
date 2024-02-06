import click

from com.statlume.nba.datasheets.cli import datasheets


@click.group(no_args_is_help=True, add_help_option=False)
def app() -> None:
    "NBA - Basketball"


app.add_command(datasheets)
