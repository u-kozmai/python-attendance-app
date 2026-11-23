from datetime import date, timedelta

GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]


def pazartesi_mi(tarih):
    return tarih.weekday() == 0


def donem_bitis_tarihi(baslangic_tarihi, toplam_hafta):
    return baslangic_tarihi + timedelta(days=(toplam_hafta * 7) - 1)


def aktif_haftayi_hesapla(baslangic_tarihi, toplam_hafta, bugun=None):
    if bugun is None:
        bugun = date.today()
    gun_farki = (bugun - baslangic_tarihi).days
    toplam_gun = toplam_hafta * 7
    if 0 <= gun_farki < toplam_gun:
        return (gun_farki // 7) + 1
    return 1


class Ders:
    def __init__(
        self,
        ad,
        gunler,
        hak_tipi="yuzde",
        hak_degeri=30.0,
        devamsiz_saatler=None,
        toplam_hafta=12,
        # v1.2 geriye dönük uyumluluk için eski alanlar:
        zorunluluk=None,
        devamsiz_tarihler=None,
    ):
        self.ad = ad
        self.gunler = gunler  # Örnek: {"Pazartesi": 2, "Çarşamba": 3}
        self.toplam_hafta = toplam_hafta

        # Eski v1.2 kayıtlarında 'zorunluluk' (örn. %70 devam zorunluluğu) vardı.
        # Yeni v2.0 sisteminde bunu devamsızlık hakkına (%30) dönüştürüyoruz.
        if zorunluluk is not None and hak_degeri == 30.0 and hak_tipi == "yuzde":
            self.hak_tipi = "yuzde"
            self.hak_degeri = float(100 - zorunluluk)
        else:
            self.hak_tipi = hak_tipi  # "yuzde" veya "saat"
            self.hak_degeri = float(hak_degeri)

        # Saat bazlı devamsızlık kayıtları: ["2026-01-12#1", "2026-01-12#2", ...]
        if devamsiz_saatler is not None:
            self.devamsiz_saatler = list(devamsiz_saatler)
        elif devamsiz_tarihler:
            # v1.2'den kalan gün bazlı kayıtları saatlik kutucuklara çevir
            self.devamsiz_saatler = []
            for tarih_str in devamsiz_tarihler:
                tarih_obj = date.fromisoformat(tarih_str)
                gun_adi = GUNLER[tarih_obj.weekday()]
                saat_sayisi = self.gunler.get(gun_adi, 0)
                for saat_no in range(1, saat_sayisi + 1):
                    self.devamsiz_saatler.append(f"{tarih_str}#{saat_no}")
        else:
            self.devamsiz_saatler = []

    def haftalik_saat(self):
        return sum(self.gunler.values())

    def toplam_saat(self):
        return self.haftalik_saat() * self.toplam_hafta

    def devamsizlik_hakki_saat(self):
        if self.hak_tipi == "saat":
            return self.hak_degeri
        return self.toplam_saat() * (self.hak_degeri / 100.0)

    def devamsizlik_hakki_yuzde(self):
        if self.hak_tipi == "yuzde":
            return self.hak_degeri
        toplam = self.toplam_saat()
        if toplam == 0:
            return 0.0
        return (self.hak_degeri / toplam) * 100.0

    def su_anki_devamsizlik_saati(self):
        return len(self.devamsiz_saatler)

    def kalan_hak_saat(self):
        return self.devamsizlik_hakki_saat() - self.su_anki_devamsizlik_saati()

    def saat_anahtari(self, tarih_str, saat_no):
        return f"{tarih_str}#{saat_no}"

    def devamsizlik_var_mi(self, tarih_str, saat_no):
        return self.saat_anahtari(tarih_str, saat_no) in self.devamsiz_saatler

    def devamsizlik_degistir(self, tarih_str, saat_no):
        anahtar = self.saat_anahtari(tarih_str, saat_no)
        if anahtar in self.devamsiz_saatler:
            self.devamsiz_saatler.remove(anahtar)
        else:
            self.devamsiz_saatler.append(anahtar)

    def to_dict(self):
        return {
            "ad": self.ad,
            "gunler": self.gunler,
            "hak_tipi": self.hak_tipi,
            "hak_degeri": self.hak_degeri,
            "devamsiz_saatler": self.devamsiz_saatler,
        }
