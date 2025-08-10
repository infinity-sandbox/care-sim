from typing import Optional
import click
from app.core.config import settings
logger = settings.get_logger(__name__)
from app.services.weaviate_service import (
                                            WeaviateService, 
                                            SimpleWeaviateQueryEngine, 
                                            AdvancedWeaviateQueryEngine
                                        )


@click.group()
def cli():
    """Main command group for tenxbot."""
    pass


@cli.command()
@click.option(
    "--model",
    default=settings.MODEL,
    help="OpenAI Model name to initialize.",
)
def init(model):
    """
    -- Initialize schemas
    """
    WeaviateService.init_schema(model=model)
    click.echo(f"Initialized schema for {model}")