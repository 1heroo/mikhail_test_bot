from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.bot_manager import BotManager
import asyncio

from src.celery_stuff import app as celery_tasks
from src.celery_stuff.app import app as celery_app
from src.viewer import Viewer

app = FastAPI()


class BotsConfig(BaseModel):
    cookies: List[str]
    proxies: List[str]


class ModelsConfig(BaseModel):
    models: Dict[str, int]


# Use Optional to indicate that viewers can be None
viewers: Optional[List[Viewer]] = None
queue = asyncio.Queue()


async def process_queue():

    while True:
        func, args = await queue.get()
        try:
            await func(*args)
        finally:
            queue.task_done()


@app.on_event("startup")
async def startup_event():
    """Start the queue processing task when the application starts."""
    for _ in range(8):
        asyncio.create_task(process_queue())


async def stop_existing_bots():
    """Stop existing bots if they are running."""
    global viewers
    if viewers is not None:
        await BotManager.stop_bots(viewers)
        viewers = None


async def launch_bots(config: BotsConfig):
    """Launch new bots with the provided configuration."""
    await stop_existing_bots()
    global viewers
    viewers = await BotManager.launch_bots(config.cookies, config.proxies)


async def update_models(config: ModelsConfig):
    """Update models for the running bots."""
    if viewers is None:
        raise HTTPException(status_code=400, detail="No bots are currently running.")
    await BotManager.update_models(viewers, config.models)


@app.post("/api/launch_bots")
async def launch_bots_endpoint(config: BotsConfig):
    """Endpoint to launch new bots with the provided configuration."""
    global viewers

    async with celery_app.setup():
        await celery_tasks.launch_bots.delay(config.cookies, proxies=config.proxies)
        viewers = True
    return {"message": "Launch request queued."}


@app.post("/api/update_models")
async def update_models_endpoint(config: ModelsConfig):
    """Endpoint to update models for the running bots."""
    if viewers is None:
        raise HTTPException(status_code=400, detail="No bots are currently running.")

    async with celery_app.setup():
        await celery_tasks.update_models.delay(config.models)
    return {"message": "Update request queued."}


@app.post("/api/stop_bots")
async def stop_bots():
    """Endpoint to stop all running bots."""

    global viewers
    if viewers is None:
        return {'message': 'there\'s not bots to force stop'}

    async with celery_app.setup():
        await celery_tasks.stop_bots.delay()
        viewers = None

    return {"message": "Stop request queued."}


@app.get('/api/get-tasks-size')
async def get_tasks_size():
    global viewers

    viewers = [] if viewers is None else viewers
    return {'message': f'current tasks, current viewers len: {len(viewers)}'}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)
