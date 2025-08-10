from apscheduler.schedulers.background import BackgroundScheduler
from utils.vapor.engine.cleanup import cleanup_workspace_and_docker, fetch_data
import time, logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

async def async_cleanup_workspace_and_docker():
    """Wrap cleanup_workspace_and_docker in an async function."""
    await asyncio.to_thread(cleanup_workspace_and_docker)
    
async def start_scheduler():
    """
    Starts the scheduler to run the cleanup task at regular intervals.
    """
    flag = await asyncio.to_thread(fetch_data)
    if flag == 'true':
        scheduler = AsyncIOScheduler()
        scheduler.add_job(async_cleanup_workspace_and_docker, 'interval', seconds=60)  # Cleanup every 60 seconds
        scheduler.start()

        # To keep the script running
        try:
            while True:
                await asyncio.sleep(1)  # Use async sleep
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
    else:
        pass