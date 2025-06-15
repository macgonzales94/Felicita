import requests
from decouple import config

class ApisPeru:
    BASE_URL = "https://api.apis.net.pe/v1"
    TOKEN = config("APISPERU_TOKEN")

    @classmethod
    def consultar_dni(cls, dni: str) -> dict:
        url = f"{cls.BASE_URL}/dni?numero={dni}"
        headers = {"Authorization": f"Bearer {cls.TOKEN}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    @classmethod
    def consultar_ruc(cls, ruc: str) -> dict:
        url = f"{cls.BASE_URL}/ruc?numero={ruc}"
        headers = {"Authorization": f"Bearer {cls.TOKEN}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
