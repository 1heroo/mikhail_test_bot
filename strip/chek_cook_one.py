import httpx
import asyncio
import time

async def fetch_jwt_token(client: httpx.AsyncClient, session_id: str) -> str:
    domains = {
        "https://stripchat.global": "stripchat_global",
        "https://stripchatgirls.com": "stripchatgirls_com",
    }

    for domain, cookie_name in domains.items():
        try:
            response = await client.get(
                f"{domain}/api/front/v3/config/dynamic?uniq={int(time.time() * 1000)}",
                cookies={f"{cookie_name}_sessionId": session_id},
                timeout=5,
            )
            jwt_token = response.json()["dynamic"].get("jwtToken")
            if jwt_token:
                return f"JWT токен с {domain}: {jwt_token}"
        except Exception as e:
            print(f"Ошибка при запросе к {domain}: {e}")

    return "Не удалось получить JWT токен с обоих доменов."

async def main():
    session_id = "ebe68b08d2a71fb52b08c6c471669813fe2680c0b0670d2819ea9f68f492"

    async with httpx.AsyncClient() as client:
        jwt_token = await fetch_jwt_token(client, session_id)
        print(f"Результат: {jwt_token}")

asyncio.run(main())
