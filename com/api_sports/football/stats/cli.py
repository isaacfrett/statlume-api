import click


@click.group(add_help_option=False)
def stats() -> None:
    """statistical data for NFL and NCAA football"""
