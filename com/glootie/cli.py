import click

from com.glootie.subcommands.get import get


@click.group(add_help_option=False)
def app() -> None:
    """The statistical analysis tool for sports data and betting odds"""


app.add_command(get)
