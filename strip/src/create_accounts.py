import asyncio
import string
import httpx
from random import choices, randint


async def create_account():

    cookies = {
        "__cf_bm": "UiCGBqEFwFzkW_.qM53UAsQc_Hd58_L0Wa028dDxRU8-1723815644-1.0.1.1-p523e0iJkqVslr4qM33yT8rXrXm.dZDgLCD9y5.mqSbqGt55E8L3ieS..rrqq53JPNTLUTBc84CIqobcnss_s2Py8mNRiS4Q38Yo.3xvAWg",
        "_cfuvid": "v4erw_beHIy2.HNpzH4eZbJcvVmmAunvr4qM1ErRV4M-1723815644324-0.0.1.1-604800000",
        "stripchatgirls_com_guestId": "c77837cd7119abd1deb0477c85bf9d1c1549f21c08cd0d220382e8469a67",
        "stripchatgirls_com_firstVisit": "2024-08-16T13%3A40%3A50Z",
        "ABTest_ab_hls_smooth_resolution_change_v2_key": "X_962",
        "isRecommendationDisabled": "false",
        "mab_featured_group": "4",
        "guestFavoriteIds": "",
        "alreadyVisited": "1",
        "c": "%7B%22essential%22%3A%5B%22all%22%5D%2C%22thirdParties%22%3A%5B%22all%22%5D%7D",
        "baseAmpl": "%7B%22platform%22%3A%22Web%22%2C%22device_id%22%3A%227tQD5XlelMi1RGoVSklAuk%22%2C%22session_id%22%3A1723815583977%2C%22up%22%3A%7B%22page%22%3A%22view%22%7D%7D",
        "guestWatchHistoryStartDate": "2024-08-16T13%3A43%3A12.576Z",
    }

    characters = string.ascii_letters + string.digits
    json_data = {
        "login": "".join(choices(characters, k=13)),
        "password": "".join(choices(characters, k=13)),
        "referralModelName": None,
        "fingerprint": None,
        "fingerprintV2": "".join(choices(characters, k=20)),
        "modelName": "daniass_lover",
        "isUnThrottled": False,
        "hasActionParam": False,
        "source": "Header",
        "v": 1,
        "isRecommendationDisabled": False,
        "pixelsPassed": randint(1, 10000),
        "clicks": randint(1, 100),
        "timeSpent": randint(1, 1000),
        "ampl": {
            "ep": {
                "pageSection": "",
                "isActivityCategoryPage": False,
                "landingParamsAction": "",
                "tagSource": "index",
                "tag": "related",
                "source": "Header",
                "modelName": "daniass_lover",
                "device": "desktop",
                "hadTranslateButton": False,
                "isTipMenuTranslated": False,
            },
            "device_id": "".join(choices(characters, k=13)),
            "platform": "Web",
            "session_id": int("".join(choices("0123456789", k=13))),
        },
        "timezoneOffset": -180,
        "an": [
            {
                "ek.platformVersion": "ee21f923",
                "ek.tabId": "b8975dfcf67af9e263b604d5e4543948dcc7dd98bcb3893cf94279a867bb",
                "ek.timestampCreated": int("".join(choices("0123456789", k=9))),
                "ek.deviceFlags": "2073600|10001110001000000",
                "ek.httpHost": "stripchatgirls.com",
                "ek.httpPath": "/daniass_lover/profile",
                "ek.isDocumentHidden": 0,
                "ek.isTabFocused": 1,
                "ek.pageClass": "viewcam",
                "g.guestIdUnique": "".join(choices(characters, k=13)),
                "eventName": "sue",
                "ek.contractVersion": "v0.1.118",
                "ek.eventId": "af416ecd-f577-4e6e-98d8-8d208d5d5e0a",
            },
        ],
        "csrfToken": "244e298774805f9dd1d59d9093a35557",
        "csrfTimestamp": "2024-08-16T13:43:11Z",
        "csrfNotifyTimestamp": "2024-08-18T01:43:11Z",
        "uniq": "".join(choices(characters, k=13)),
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "Referer": "https://stripchatgirls.com/daniass_lover/profile",
        "Front-Version": "10.91.8",
        "Origin": "https://stripchatgirls.com",
        "DNT": "1",
        "Sec-GPC": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Connection": "keep-alive",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://stripchatgirls.com/api/front/v6/users",
            cookies=cookies,
            json=json_data,
            headers=headers,
            timeout=5,
        )

        print(response.cookies.get("stripchatgirls_com_sessionId"))
        return response.cookies.get("stripchatgirls_com_sessionId")

async def get_session_ids(count):
    tasks = []
    for _ in range(count):
        tasks.append(create_account())

    return await asyncio.gather(*tasks)
