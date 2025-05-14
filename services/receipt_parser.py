import requests
import logging
from config import Config

async def parse_receipt_from_qr(qr_image_path: str):
    try:
        with open(qr_image_path, 'rb') as f:
            response = requests.post(
                Config.PROVERKA_CHEKA_API_URL,
                files={'qrfile': f},
                data={'token': Config.PROVERKA_CHEKA_API_KEY},
                timeout=10
            )
        data = response.json()
        if data.get('code') != 1:
            logging.error(f"Receipt parsing failed: {data.get('message')}")
            raise ValueError("Не удалось распознать чек")
        return data['data']['json']
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error: {e}")
        raise ValueError("Ошибка соединения с сервисом чеков")