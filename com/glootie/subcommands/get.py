import click

from com.api_sports.football.cli import football


@click.group(add_help_option=False)
def get() -> None:
    """retrieve stats or betting data"""


get.add_command(football)
