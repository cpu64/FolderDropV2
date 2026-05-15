import click
import asyncio
import sys
import os
import threading
import socket

from app.host.controllers.main import MainWindowController
from app.web.Controllers.WebController import WebController
from app.host.controllers.FileController import FileController
from app.models.settings import settings_store
from app.models.FileSystemObject import Folder


@click.group()
def cli():
    pass

def validateSettings(settings):
    if not settings.path:
        return "Shared folder path is not set."
    if not settings.port or settings.port < 1 or settings.port > 65535:
        return "Port must be between 1 and 65535."
    return None

def generateLink(settings=None):
    if settings is None:
        settings = settings_store.get_settings()
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip = "127.0.0.1"
    return f"http://{ip}:{settings.port}"

@cli.command()
def web():
    file_controller = FileController()
    settings = settings_store.get_settings()
    error = validateSettings(settings)
    if error:
        print(error)
        return

    try:
        folder_info = file_controller.checkFolderUsable(settings.path)
    except ValueError as e:
        print(e)
        return

    folder_content = file_controller.getFolderContent(settings.path)

    root = Folder(name=os.path.basename(settings.path))
    root.is_root = True
    children = Folder.from_folder_content(folder_content, parent_folder=root)
    root.child_folders = [c for c in children if c.is_dir]
    root.folders_file = [c for c in children if not c.is_dir]
    root.element_count = len(root.child_folders) + len(root.folders_file)
    root._recalc_size()
    dir_cache = root

    file_controller.set_dir_cache(dir_cache, settings.path)

    try:
        web_controller = WebController(dir_cache)

        server_thread = threading.Thread(
            target=web_controller.run, kwargs={"host": "0.0.0.0", "port": settings.port}, daemon=False
        )
        server_thread.start()

    except Exception as e:
        print(f"Failed to start sharing: {e}")
        return

    file_controller.owner_fs.set_file_controller(file_controller)
    file_controller.owner_fs.start_watching(settings.path)

    link = generateLink(settings)
    print(link)

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
