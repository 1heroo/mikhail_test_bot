import asyncio
import os
from typing import Optional

from aio_celery import Celery
from aio_celery.config import DefaultConfig

from src.bot_manager import BotManager
from src.viewer import Viewer

app = Celery('tasks')
app.conf.update(
    broker_url=os.getenv('RABBITMQ_URL')
)


bot_manager = BotManager()


viewers: Optional[list] = None


@app.task
async def launch_bots(cookies, proxies):
    global viewers

    if viewers is not None:
        await stop_bots()
    viewers = await bot_manager.launch_bots(cookies=cookies, proxies=proxies)


@app.task
async def stop_bots() -> None:
    global viewers

    if viewers is not None:
        await bot_manager.stop_bots(viewers)
        viewers = None


@app.task
async def update_models(models) -> None:
    # viewers = list(map(lambda item: Viewer.deserialize(item), serialized_viewers))
    await bot_manager.update_models(viewers=viewers, models=models)


