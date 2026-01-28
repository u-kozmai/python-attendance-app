from datetime import date

class Ders:
    def __init__(self, ad, gunler, zorunluluk, devamsiz_tarihler=None):
        self.ad = ad
        self.gunler = gunler
        self.zorunluluk = zorunluluk
        self.devamsiz_tarihler = devamsiz_tarihler if devamsiz_tarihler else []
        self.toplam_hafta = 12

    def toplam_saat(self):
        return sum(self.gunler.values()) * self.toplam_hafta

    def devamsizlik_hakki_saat(self):
        return self.toplam_saat() * (1 - (self.zorunluluk / 100))

    def su_anki_devamsizlik_saati(self):
        toplam = 0
        gun_map = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        for tarih_str in self.devamsiz_tarihler:
            t_obj = date.fromisoformat(tarih_str)
            gun_adi = gun_map[t_obj.weekday()]
            toplam += self.gunler.get(gun_adi, 0)
        return toplam
    
    def devamsizlik_var_mi(self, tarih_str):
        return tarih_str in self.devamsiz_tarihler

    def to_dict(self):
        return {
            "ad": self.ad, "gunler": self.gunler, 
            "zorunluluk": self.zorunluluk, "devamsiz_tarihler": self.devamsiz_tarihler
        }