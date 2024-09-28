import httpx
import asyncio
import time

# Функция для проверки JWT токена
async def fetch_jwt_token(client: httpx.AsyncClient, session_id: str) -> bool:
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
                return True  # Кука валидна
        except Exception as e:
            print(f"Ошибка при запросе к {domain}: {e}")

    return False  # Кука невалидна, если токен не получен

# Функция для чтения куков из файла
def read_cookies(file_path: str) -> list:
    with open(file_path, 'r') as file:
        cookies = file.readlines()
    return [cookie.strip() for cookie in cookies]

# Функция для записи валидных куков обратно в файл
def write_valid_cookies(file_path: str, valid_cookies: list):
    with open(file_path, 'w') as file:
        for cookie in valid_cookies:
            file.write(f"{cookie}\n")

# Основная функция
async def main():
    cookies_file = "../cookies.txt"

    # Читаем куки из файла
    cookies = read_cookies(cookies_file)

    valid_cookies = []

    # Проверяем каждую куку
    async with httpx.AsyncClient() as client:
        for cookie in cookies:
            is_valid = await fetch_jwt_token(client, cookie)
            if is_valid:
                valid_cookies.append(cookie)
            else:
                print(f"Невалидная кука: {cookie}")

    # Записываем только валидные куки обратно в файл
    write_valid_cookies(cookies_file, valid_cookies)
    print(f"Обновленный список куков сохранен. Всего валидных куков: {len(valid_cookies)}")

# Запуск
asyncio.run(main())
