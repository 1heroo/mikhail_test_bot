import asyncio
import uuid
import httpx
from src.logger import setup_logger
from traceback import format_exc
from src.api import fetch_jwt_token, fetch_bot_id_and_viewer_payload
logger = setup_logger("viewer")


class Viewer:
    def __init__(
        self,
        session_id,
        bot_id: str,
        proxy: str,
        payload: dict[str, str],
    ) -> None:
        self.session_id = session_id
        self.bot_id = bot_id
        self.headers = {"Authorization": None}
        self.proxy = proxy
        self._models: set[str] = set()
        self.payload = payload
        self.started = False
        self.client = httpx.AsyncClient(proxies=self.proxy)
        self.load = 0  # Track the number of models the bot is handling

        if not payload.get('uniq'):
            self.payload.update({"uniq": str(uuid.uuid4())})

    async def start(self) -> None:
        """Start the viewer loop."""
        self.started = True
        while self.started:
            try:
                if not self._models:
                    await asyncio.sleep(5)
                    continue
                await self._viewer_loop()
            except Exception as e:
                logger.error(f"Error in main viewer loop, but will retry: {e}")
                await asyncio.sleep(5)

    async def _keep_loop_alive(self, model_id: str) -> None:
        for attempt in range(5):
            try:
                await asyncio.sleep(5)
                await self.client.put(  # type: ignore
                    f"https://stripchatgirls.com/api/front/models/{model_id}/viewers/{self.bot_id}",
                    headers=self.headers,
                    json=self.payload,
                    timeout=20,
                )
                break
            except Exception as e:
                logger.warning(
                    f"Error updating viewers for model {model_id}: {e}"
                )
                # logger.error(format_exc())
                await asyncio.sleep(5)

    async def _viewer_loop(self) -> None:
        """Main loop for handling model updates."""
        logger.debug(
            f"Starting viewer loop for user {self.bot_id} with {len(self._models)} models"
        )

        try:
            while self.started:
                if not self.started:
                    break

                self.headers['Authorization'] = await fetch_jwt_token(self.client, self.session_id)
                for model_id in list(self._models):
                    if not self.started:
                        break
                    asyncio.create_task(self._keep_loop_alive(model_id=model_id))
                await asyncio.sleep(15)

        except httpx.CloseError:
            logger.warning(f"Connection closed for user {self.bot_id}.")
        except Exception as e:
            logger.error(f"Error in viewer loop for user {self.bot_id}: {e}")

    async def has_model(self, model_id: str) -> bool:
        """Check if the viewer has a specific model."""
        return model_id in self._models

    async def remove_model(self, model_id: str) -> None:
        """Remove a model from the viewer."""
        logger.debug(f"Removing model {model_id} from viewer {self.bot_id}")
        self._models.discard(model_id)
        self.load -= 1  # Decrement load
        await self.delete_bot(model_id)

    async def add_model(self, model_id: str) -> None:
        """Add a model to the viewer."""
        logger.debug(f"Adding model {model_id} to viewer {self.bot_id}")
        self._models.add(model_id)
        self.load += 1  # Increment load

    async def restart(self) -> None:
        """Restart the viewer with a new unique payload."""
        self.started = False
        await asyncio.sleep(0.1)

        self.payload["uniq"] = str(uuid.uuid4())
        asyncio.create_task(self.start())

    async def delete_bot(self, model_id: str) -> None:
        """Delete the bot associated with a specific model."""
        await self.client.delete(  # type: ignore
            f"https://stripchatgirls.com/api/front/models/{model_id}/viewers/{self.bot_id}",
            headers=self.headers,
            timeout=5,
        )
        logger.debug(f"Viewer stopped for user {self.bot_id} and model {model_id}.")

    async def close_client(self) -> None:
        """Close the HTTP client and clean up models."""
        self.started = False
        await asyncio.sleep(0.1)

        for model_id in list(self._models):
            await self.delete_bot(model_id)

        await asyncio.sleep(10)
        if self.client:
            await self.client.aclose()

    def serialize(self) -> dict:
        """Сериализация объекта Viewer в словарь"""
        return {
            "session_id": self.session_id,
            "bot_id": self.bot_id,
            "headers": self.headers,
            "proxy": self.proxy,
            "models": list(self._models),  # Множество переводим в список
            "payload": self.payload,
            "started": self.started,
            "load": self.load,
        }

    @classmethod
    def deserialize(cls, data: dict):
        """Десериализация объекта Viewer из словаря"""
        viewer = cls(
            session_id=data["session_id"],
            bot_id=data["bot_id"],
            proxy=data["proxy"],
            payload=data["payload"]
        )
        viewer.headers = data.get("headers", {})
        viewer._models = set(data.get("models", []))
        viewer.started = data.get("started", False)
        viewer.load = data.get("load", 0)
        return viewer
