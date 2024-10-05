import requests

cookies = open("cookies.txt").read().splitlines()
proxies = open("proxies.txt").read().splitlines()

# requests.post(
#     "http://127.0.0.1:8000/api/launch_bots",
#     json={"cookies": cookies, "proxies": proxies},
# )


print("Обновление моделей...")
requests.post(
    "http://127.0.0.1:8000/api/update_models", json={"models": {
        "Mia_komio": 0,
    }}
)

print("Всё!")
