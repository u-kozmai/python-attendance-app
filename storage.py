import json
import os
from models import Ders

class Storage:
    FILE_NAME = "dersler.json"

    @staticmethod
    def kaydet(ders_listesi):
        with open(Storage.FILE_NAME, "w", encoding="utf-8") as f:
            json.dump([d.to_dict() for d in ders_listesi], f, ensure_ascii=False, indent=4)

    @staticmethod
    def yukle():
        if not os.path.exists(Storage.FILE_NAME):
            return []
        with open(Storage.FILE_NAME, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Ders(**d) for d in data]