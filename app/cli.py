import click
import asyncio

from app.server import run as run_server
from app
@click.group()
def cli():
    pass

@cli.command()
def web():
    """Run Quart + Hypercorn server"""
    asyncio.run(run_server())

@cli.command()
def desktop():
    """Run Qt desktop app"""
    run_desktop()

@cli.command()
@click.argument("name")
def greet(name):
    """Test shared logic"""
    from myapp.core.logic import greet
    click.echo(greet(name))
