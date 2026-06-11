import httpx
from app.core.config import (
    WORKLY_BASE_URL,
    WORKLY_CLIENT_ID,
    WORKLY_CLIENT_SECRET,
    WORKLY_USERNAME,
    WORKLY_PASSWORD,
    WORKLY_ACCESS_TOKEN,
    WORKLY_REFRESH_TOKEN,
)


# async def request_workly_token(data: dict[str, str]) -> str:
#     url = f"{WORKLY_BASE_URL}"

#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, data=data, timeout=60)

#     response.raise_for_status()
#     token_data = response.json()
#     return token_data["access_token"]

async def request_workly_token(data: dict[str, str]) -> str:
    url = "https://api.workly.io/v1/oauth/token"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, timeout=60)

    response.raise_for_status()
    token_data = response.json()
    return token_data["access_token"]


async def get_workly_token():
    if WORKLY_ACCESS_TOKEN:
        return WORKLY_ACCESS_TOKEN

    if WORKLY_REFRESH_TOKEN:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": WORKLY_REFRESH_TOKEN,
        }
        if WORKLY_CLIENT_ID:
            data["client_id"] = WORKLY_CLIENT_ID
        if WORKLY_CLIENT_SECRET:
            data["client_secret"] = WORKLY_CLIENT_SECRET
        return await request_workly_token(data)

    if WORKLY_USERNAME and WORKLY_PASSWORD:
        data = {
            "grant_type": "password",
            "username": WORKLY_USERNAME,
            "password": WORKLY_PASSWORD,
        }
        if WORKLY_CLIENT_ID:
            data["client_id"] = WORKLY_CLIENT_ID
        if WORKLY_CLIENT_SECRET:
            data["client_secret"] = WORKLY_CLIENT_SECRET
        return await request_workly_token(data)

    data = {
        "grant_type": "client_credentials",
        "client_id": WORKLY_CLIENT_ID,
        "client_secret": WORKLY_CLIENT_SECRET,
    }
    return await request_workly_token(data)




async def get_workly_employees():
    token = await get_workly_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    all_employees = []
    page = 1

    async with httpx.AsyncClient() as client:

        while True:

            url = f"{WORKLY_BASE_URL}/v1/employees?page={page}"

            # print("REQUEST:", url)

            response = await client.get(
                url,
                headers=headers,
                timeout=60,
            )

            response.raise_for_status()

            data = response.json()

            # print("DATA TYPE:", type(data))
            # print("DATA:", data)

            # CASE 1 -> {"items": [...]}
            if isinstance(data, dict):
                employees = data.get("items", [])

            # CASE 2 -> [...]
            elif isinstance(data, list):
                employees = data

            else:
                employees = []

            # print(f"PAGE {page}: {len(employees)} employees")

            if not employees:
                break

            all_employees.extend(employees)

            # oxirgi page
            if len(employees) < 50:
                break

            page += 1

    print("TOTAL:", len(all_employees))

    return all_employees