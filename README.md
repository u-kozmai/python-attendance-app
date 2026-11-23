# 📅 Attendance Tracker Pro (v2.0)

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg?logo=python&logoColor=white)](https://www.python.org)
[![PySide6](https://img.shields.io/badge/UI-PySide6-green.svg?logo=qt&logoColor=white)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Üniversite devamsızlıklarınızı saat bazında ve kendi dönem takviminize göre yönetebileceğiniz modern karanlık temalı masaüstü uygulaması.

---

## ✨ v2.0 Yenilikleri
- **⚙️ Dinamik Dönem Ayarları:** Artık tek bir üniversite veya döneme sabit değil! **Ayarlar** sekmesinden dönem başlangıç tarihini (otomatik Pazartesi kontrolü ile) ve toplam hafta sayısını belirleyerek kendi döneminizi oluşturabilirsiniz.
- **📆 Akıllı Hafta Açılışı:** Bugünün tarihi oluşturduğunuz dönem aralığına denk geliyorsa doğrudan içinde bulunduğunuz hafta açılır; dönem dışında ise 1. hafta görüntülenir.
- **🧩 Saatlik Ders Kutucukları:** Bir günde 2 saat dersiniz varsa 2 adet 1'er saatlik bağımsız kutucuk oluşur. Sadece girmediğiniz saati tek tıkla işaretleyebilirsiniz.
- **⚖️ Birbiriyle Orantılı Devamsızlık Hakkı:** Ders eklerken devamsızlık hakkınızı ister **yüzde (%)** ister **saat** cinsinden belirleyebilirsiniz; iki alan birbirini anlık olarak orantılı şekilde günceller.
- **📊 Gelişmiş Genel Özet:** Kalan devamsızlık hakkı, yüzde/saat karşılığı ve ders silme işlemi eklendi.

---

## 🚀 Kurulum

```bash
# Depoyu klonlayın
git clone "https://github.com/u-kozmai/python-attendance-app.git"
cd python-attendance-app

# Bağımlılıkları kurun (Venv aktifken)
pip install -r requirements.txt

# Uygulamayı çalıştırın
python main.py
```
