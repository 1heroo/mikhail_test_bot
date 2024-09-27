import aioconsole
import asyncio
from bot_manager import BotManager


async def viewers(cookies: list, proxies: list):
    viewers = await BotManager.launch_bots(cookies, proxies)
    print(viewers)
    print(len(viewers))

    while True:
        nicks_input = (await aioconsole.ainput("Введите ники моделей и кол-во ботов для каждой через запятую(<ник> <кол-во ботов): ")).lower()
        
        nicks = {}
        for nick in nicks_input.split(", "):
            nick, count = nick.split(" ")
            nicks[nick] = int(count)

        await BotManager.update_models(viewers, nicks)


if __name__ == "__main__":
    with open("cookies.txt") as f:
        cookies = f.read().splitlines()
    with open("proxies.txt") as f:
        proxies = f.read().splitlines()
    asyncio.run(viewers(cookies, proxies))
