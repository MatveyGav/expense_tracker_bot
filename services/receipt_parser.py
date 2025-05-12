import requests
from config import Config


async def parse_receipt_from_qr(qr_image_path: str):
    url = "https://proverkacheka.com/api/v1/check/get"

    with open(qr_image_path, 'rb') as f:
        response = requests.post(
            url,
            files={'qrfile': f},
            data={'token': Config.PROVERKA_CHEKA_API_KEY}
        )

    data = response.json()

    if data.get('code') != 1:
        raise ValueError("Failed to parse receipt")

    return data['data']['json']