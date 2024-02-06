import click


@click.group()
def create() -> None:
    """Perform create operations"""


@click.command()
def mismatches() -> None:
    """Create mismatch datasheet and picture"""


@click.command()
def players() -> None:
    """Create players datasheets and pictures"""


@click.command()
def teams() -> None:
    """Create teams datasheets and pictures"""


@click.command()
def threes() -> None:
    """Create threes datasheets and pictures"""


create.add_command(mismatches)
create.add_command(players)
create.add_command(teams)
create.add_command(threes)
