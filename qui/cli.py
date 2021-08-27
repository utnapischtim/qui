import click


@click.group()
@click.version_option()
def qui():
    """Initialize CLI context."""


@qui.command()
def run():
    print("qui run")
