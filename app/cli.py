import click
import asyncio
import sys

from app.host.controllers.main import MainWindowController

@click.group()
def cli():
    pass

@cli.command()
def web():
    """Run Quart + Hypercorn server"""
    # asyncio.run(run_server())
    pass

@cli.command()
def desktop():
    """Run Qt desktop app"""
    main_controller = MainWindowController()
    return main_controller.run()


@cli.command()
@click.argument("name")
def greet(name):
    """Test shared logic"""
    from myapp.core.logic import greet
    click.echo(greet(name))
