import json
import os
from datetime import date
from models import Ders

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Storage:
    DERSLER_FILE = os.path.join(BASE_DIR, "dersler.json")
    AYARLAR_FILE = os.path.join(BASE_DIR, "ayarlar.json")

    VARSAYILAN_AYARLAR = {
        "baslangic_tarihi": "2026-01-12",  # Pazartesi
        "toplam_hafta": 12,
    }

    @staticmethod
    def ayarlari_kaydet(baslangic_tarihi, toplam_hafta):
        veri = {
            "baslangic_tarihi": baslangic_tarihi.isoformat(),
            "toplam_hafta": int(toplam_hafta),
        }
        with open(Storage.AYARLAR_FILE, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=4)

    @staticmethod
    def ayarlari_yukle():
        if not os.path.exists(Storage.AYARLAR_FILE):
            return (
                date.fromisoformat(Storage.VARSAYILAN_AYARLAR["baslangic_tarihi"]),
                Storage.VARSAYILAN_AYARLAR["toplam_hafta"],
            )
        with open(Storage.AYARLAR_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            baslangic = date.fromisoformat(
                data.get("baslangic_tarihi", Storage.VARSAYILAN_AYARLAR["baslangic_tarihi"])
            )
            toplam_hafta = int(
                data.get("toplam_hafta", Storage.VARSAYILAN_AYARLAR["toplam_hafta"])
            )
            return baslangic, toplam_hafta

    @staticmethod
    def kaydet(ders_listesi):
        with open(Storage.DERSLER_FILE, "w", encoding="utf-8") as f:
            json.dump(
                [d.to_dict() for d in ders_listesi],
                f,
                ensure_ascii=False,
                indent=4,
            )

    @staticmethod
    def yukle(toplam_hafta=12):
        if not os.path.exists(Storage.DERSLER_FILE):
            return []
        with open(Storage.DERSLER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Ders(**d, toplam_hafta=toplam_hafta) for d in data]
