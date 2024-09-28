import asyncio
import httpx
from src.logger import setup_logger
from src.api import fetch_bot_id_and_viewer_payload, fetch_model_ids
from src.viewer import Viewer

logger = setup_logger("bot_manager")


class BotManager:
    @staticmethod
    async def create_bot(session_id: str, proxy: str) -> Viewer | None:
        """Create a bot viewer for the given session ID and proxy."""
        async with httpx.AsyncClient(proxies=proxy) as client:
            try:
                bot_id, payload = await fetch_bot_id_and_viewer_payload(
                    client, session_id
                )
                if bot_id is None:
                    logger.error(f"No user ID found for user: {session_id}")
                    return None

                viewer = Viewer(session_id, bot_id, proxy, payload)
                logger.debug(f"Viewer thread created for user: {bot_id}")
                return viewer
            except Exception as e:
                logger.error(f"Failed to fetch data for user: {session_id}, error: {e}")
                return None

    @staticmethod
    async def launch_bots(
        cookies: list[str], proxies: list[str]
    ) -> list[Viewer | None] | list[Viewer]:
        """Launch multiple bots using the provided cookies and proxies."""
        logger.debug(f"Launching {len(cookies)} bots")
        tasks = [
            BotManager.create_bot(cookies.pop(), proxies.pop())
            for _ in range(len(proxies))
        ]
        viewers = await asyncio.gather(*tasks)
        clean_viewers = [viewer for viewer in viewers if viewer is not None]
        logger.debug(f"Launched {len(clean_viewers)}/{len(cookies) + len(clean_viewers)} bots")
        return clean_viewers

    @staticmethod
    async def stop_bots(viewers: list[Viewer]) -> None:
        """Stop all running viewers."""
        logger.debug(f"Stopping {len(viewers)} viewers")
        tasks = [viewer.close_client() for viewer in viewers]
        await asyncio.gather(*tasks)
        viewers.clear()
        logger.debug("Viewers stopped")

    @staticmethod
    async def update_models(viewers: list[Viewer], models: dict[str, int]) -> None:
        """Update the models for the running viewers."""
        logger.debug(f"Updating models: {models}")
        model_ids = await fetch_model_ids(list(models.keys()))
        model_counts = list(models.values())

        desired_models = dict(zip(model_ids, model_counts))

        # Create a dictionary to track current counts of models in viewers
        current_model_counts = {model_id: 0 for model_id in model_ids}
        for viewer in viewers:
            if viewer is None:
                continue
            for model_id in viewer._models:
                current_model_counts[model_id] = (
                    current_model_counts.get(model_id, 0) + 1
                )

        for model_id in model_ids:
            current_count = current_model_counts.get(model_id, 0)
            desired_count = desired_models.get(model_id, 0)

            models_to_add = []
            models_to_remove = []

            if current_count < desired_count:
                # Prioritize least-loaded bots
                sorted_viewers = sorted(viewers, key=lambda v: v.load)
                for viewer in sorted_viewers:
                    if not await viewer.has_model(model_id):
                        logger.debug(f"Adding model {model_id} to viewer {viewer.bot_id}")
                        models_to_add.append(viewer)
                        current_count += 1
                        if current_count >= desired_count:
                            break

            elif current_count > desired_count:
                # Prioritize least-loaded bots
                sorted_viewers = sorted(viewers, key=lambda v: v.load, reverse=True)
                for viewer in sorted_viewers:
                    if await viewer.has_model(model_id):
                        logger.debug(f"Removing model {model_id} from viewer {viewer.bot_id}")
                        models_to_remove.append(viewer)
                        current_count -= 1
                        if current_count <= desired_count:
                            break

            # Create separate lists to avoid modification during iteration
            all_models_to_update = models_to_add + models_to_remove
            add_tasks = [viewer.add_model(model_id) for viewer in models_to_add]
            remove_tasks = [viewer.remove_model(model_id) for viewer in models_to_remove]
            restart_tasks = [viewer.restart() for viewer in all_models_to_update]

            await asyncio.gather(*add_tasks, *remove_tasks, *restart_tasks)

        logger.debug(f"Models updated: {models}")
