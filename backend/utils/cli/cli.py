import os
import click
import uvicorn
from utils.docker.util import is_docker
from app.core.config import logger_settings
logger = logger_settings.get_logger(__name__)

@click.group()
@click.version_option(version="0.0.1")  # Specify the version of your application here
def cli():
    """
    Main command group for applicare ai.
    """
    pass

@cli.command()
@click.option(
    "--uvreload",
    default=not is_docker(),
    help="Enable or disable uvicorn reloading (default: enabled if not in Docker)."
)

def start(uvreload: bool):
    """
    Run the application.
    """
    if uvreload:
        logger.warning(f"uvicorn reloading: {uvreload}")
    else:
        logger.warning(f"uvicorn reloading: {uvreload}")   
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000)
