import click


@click.group()
def delete() -> None:
    """Perform delete operations"""


@click.command()
def mismatches() -> None:
    """Delete mismatch datasheet and picture"""


@click.command()
def players() -> None:
    """Delete players datasheets and pictures"""


@click.command()
def teams() -> None:
    """Delete teams datasheets and pictures"""


@click.command()
def threes() -> None:
    """Delete threes datasheets and pictures"""


@click.command()
def all() -> None:
    """Delete all datasheets and pictures"""


delete.add_command(mismatches)
delete.add_command(players)
delete.add_command(teams)
delete.add_command(threes)
delete.add_command(all)
