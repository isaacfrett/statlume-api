import click


@click.group(no_args_is_help=True, add_help_option=False)
def app() -> None:
    "MLB"
