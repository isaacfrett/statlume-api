import click

from com.api_sports.football.stats.cli import stats


@click.group(add_help_option=False)
def football() -> None:
    """NFL and NCAA football"""


football.add_command(stats)
