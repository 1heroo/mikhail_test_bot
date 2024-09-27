import httpx
import time
import asyncio
from logger import setup_logger
from traceback import format_exc

logger = setup_logger("api")


async def fetch_jwt_token(client: httpx.AsyncClient, session_id: str) -> str:
    domains = {
        "https://stripchatgirls.com": "stripchatgirls_com",
        "https://stripchat.global": "stripchat_global",
    }

    for domain, cookie_name in domains.items():
        try:
            for attempt in range(5):  # до 5 попыток
                try:
                    await asyncio.sleep(2)  # Задержка перед каждым запросом для уменьшения нагрузки
                    response = await client.get(
                        f"{domain}/api/front/v3/config/dynamic?uniq={int(time.time() * 1000)}",
                        cookies={f"{cookie_name}_sessionId": session_id},
                        timeout=20,  # увеличенный тайм-аут
                    )
                    response.raise_for_status()  # Вызвать исключение для статусов 4xx/5xx
                except httpx.HTTPStatusError as e:
                    logger.error(f"HTTP статус ошибка с {domain} на попытке {attempt + 1}: {e}")
                    if response.status_code == 429:
                        logger.warning("Получен статус 429, ожидание перед повтором...")
                        await asyncio.sleep(2 ** attempt + 5)  # Экспоненциальная задержка + 5 сек
                except httpx.RequestError as e:
                    logger.error(f"Ошибка запроса с {domain} на попытке {attempt + 1}: {e}")
                except Exception as e:
                    logger.error(f"Неизвестная ошибка при запросе к {domain} на попытке {attempt + 1}")
                    logger.error(format_exc())
                    await asyncio.sleep(2 ** attempt)
                    continue

                if response.status_code == 200:
                    jwtToken = response.json().get("dynamic", {}).get("jwtToken")
                    if jwtToken:
                        return jwtToken
                else:
                    logger.warning(f"Неожиданный статус-код: {response.status_code} с {domain}")

        except Exception as e:
            logger.error(f"Ошибка в работе с доменом {domain}: {e}")

    logger.error(f"Не удалось получить JWT токен для session_id: {session_id}")
    return None


async def fetch_bot_id_and_viewer_payload(
    client: httpx.AsyncClient, session_id: str
) -> tuple:
    domains = {
        "https://stripchatgirls.com": "stripchatgirls_com",
        "https://stripchat.global": "stripchat_global",
    }

    for domain, cookie_name in domains.items():
            for attempt in range(3):
                try:
                    response = await client.get(
                        f"{domain}/api/front/v3/config/initial",
                        cookies={f"{cookie_name}_sessionId": session_id},
                        timeout=20,
                    )
                except:
                    logger.error(format_exc())
                    continue
                json = response.json()["initial"]["client"]
                if json["user"]:
                    return json["user"]["id"], {
                        "csrfToken": json["csrfToken"],
                        "csrfTimestamp": json["csrfTimestamp"],
                        "csrfNotifyTimestamp": json["csrfNotifyTimestamp"],
                        "tabId": json["tabId"],
                    }



async def fetch_model_ids(nicks: list) -> list:
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get(
                f"https://stripchatgirls.com/api/front/v2/users/username/{nick}",
                timeout=20,
            )
            for nick in nicks
        ]
        responses = await asyncio.gather(*tasks)
        return [response.json()["item"]["id"] for response in responses]
