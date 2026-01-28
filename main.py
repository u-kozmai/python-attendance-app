import sys
from datetime import date, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QTabWidget, QScrollArea, 
                             QFrame, QLabel, QSpinBox)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

from models import Ders
from storage import Storage
from dialogs import DersEkleDialog

class DevamsizlikApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ders Takip & Ajanda 2026")
        self.resize(1200, 750)
        self.dersler = Storage.yukle()
        self.baslangic_tarihi = date(2026, 1, 12)
        with open("style.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        # Ana Sekme Yapısı
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Sekme Widgetları
        self.takvim_tab = QWidget()
        self.ozet_tab = QWidget()

        self.tabs.addTab(self.takvim_tab, "📅 Haftalık Program")
        self.tabs.addTab(self.ozet_tab, "📊 Genel Özet")

        self.takvim_arayuzunu_kur()
        self.ozet_arayuzunu_kur()
        self.arayuzu_tazele()

    def takvim_arayuzunu_kur(self):
        layout = QVBoxLayout(self.takvim_tab)

        # Üst Panel: Hafta Seçimi
        ust_panel = QHBoxLayout()
        self.hafta_secici = QSpinBox()
        self.hafta_secici.setRange(1, 12)
        self.hafta_secici.setPrefix("Dönem Haftası: ")
        self.hafta_secici.setStyleSheet("font-size: 16px; padding: 5px;")
        self.hafta_secici.valueChanged.connect(self.arayuzu_tazele)
        
        # Bugünün haftasına otomatik git
        gun_farki = (date.today() - self.baslangic_tarihi).days
        mevcut_hafta = max(1, min(12, (gun_farki // 7) + 1))
        self.hafta_secici.setValue(mevcut_hafta)

        ust_panel.addWidget(self.hafta_secici)
        ust_panel.addStretch()
        
        self.ekle_btn = QPushButton("+ Yeni Ders Ekle")
        self.ekle_btn.clicked.connect(self.ders_ekle)
        ust_panel.addWidget(self.ekle_btn)
        
        layout.addLayout(ust_panel)

        # Haftalık Günler (Scroll Area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        self.gunler_container = QWidget()
        self.gunler_layout = QHBoxLayout(self.gunler_container)
        
        self.gun_column_widgets = {} # Gün panellerini saklayacağız
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        
        for gun in gunler:
            gun_v_layout = QVBoxLayout()
            
            # Gün Başlığı
            baslik = QLabel(f"<b>{gun}</b>")
            baslik.setAlignment(Qt.AlignCenter)
            baslik.setStyleSheet("font-size: 14px; color: #2c3e50;")
            gun_v_layout.addWidget(baslik)
            
            # Tarih Etiketi
            tarih_label = QLabel("--")
            tarih_label.setAlignment(Qt.AlignCenter)
            gun_v_layout.addWidget(tarih_label)

            # Derslerin listeleneceği dikey kutu
            ders_list_frame = QFrame()
            ders_list_frame.setFrameShape(QFrame.StyledPanel)
            ders_list_frame.setMinimumWidth(150)
            inner_layout = QVBoxLayout(ders_list_frame)
            inner_layout.addStretch()
            
            gun_v_layout.addWidget(ders_list_frame)
            self.gunler_layout.addLayout(gun_v_layout)
            
            # Referansları sakla
            self.gun_column_widgets[gun] = {
                "layout": inner_layout,
                "tarih_label": tarih_label
            }

        scroll.setWidget(self.gunler_container)
        layout.addWidget(scroll)

    def ozet_arayuzunu_kur(self):
        layout = QVBoxLayout(self.ozet_tab)
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["Ders Adı", "Toplam Ders (S)", "D. Hakkı (S)", "Gidilmeyen (S)", "Durum"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tablo)

    def arayuzu_tazele(self):
        # 1. Özet Tablosunu Güncelle
        self.tablo.setRowCount(0)
        for d in self.dersler:
            row = self.tablo.rowCount()
            self.tablo.insertRow(row)
            su_an = d.su_anki_devamsizlik_saati()
            hak = d.devamsizlik_hakki_saat()
            durum = "GEÇTİ" if su_an <= hak else "KALDI"
            
            self.tablo.setItem(row, 0, QTableWidgetItem(d.ad))
            self.tablo.setItem(row, 1, QTableWidgetItem(str(d.toplam_saat())))
            self.tablo.setItem(row, 2, QTableWidgetItem(f"{hak:.1f}"))
            self.tablo.setItem(row, 3, QTableWidgetItem(str(su_an)))
            
            durum_item = QTableWidgetItem(durum)
            if durum == "KALDI": durum_item.setForeground(QColor("red"))
            self.tablo.setItem(row, 4, durum_item)

        # 2. Takvim Görünümünü Güncelle
        secili_hafta = self.hafta_secici.value()
        gun_map = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        
        for gun_adi, refs in self.gun_column_widgets.items():
            # Eski butonları temizle
            while refs["layout"].count() > 1:
                child = refs["layout"].takeAt(0)
                if child.widget(): child.widget().deleteLater()
            
            # Tarihi hesapla ve yaz
            gun_idx = gun_map.index(gun_adi)
            tarih_obj = self.baslangic_tarihi + timedelta(days=((secili_hafta-1)*7 + gun_idx))
            tarih_str = tarih_obj.isoformat()
            refs["tarih_label"].setText(tarih_obj.strftime("%d %b"))

            # O güne ait dersleri bul ve buton ekle
            for ders in self.dersler:
                if gun_adi in ders.gunler:
                    btn = QPushButton(f"{ders.ad}\n({ders.gunler[gun_adi]} Saat)")
                    btn.setObjectName("DersButonu")
                    btn.setMinimumHeight(60)
                    
                    # Duruma göre renk ayarla
                    if ders.devamsizlik_var_mi(tarih_str):
                        # Pastel/Neon Kırmızı Gradient
                        btn.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff5252, stop:1 #b71c1c);")
                    else:
                        # Pastel/Neon Yeşil Gradient
                        btn.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #66bb6a, stop:1 #2e7d32);")          
                    # Tıklama olayını bağla (Closure kullanarak)
                    btn.clicked.connect(lambda checked=False, d=ders, t=tarih_str: self.devamsizlik_toggle(d, t))
                    refs["layout"].insertWidget(refs["layout"].count()-1, btn)

    def devamsizlik_toggle(self, ders, tarih_str):
        if tarih_str in ders.devamsiz_tarihler:
            ders.devamsiz_tarihler.remove(tarih_str)
        else:
            ders.devamsiz_tarihler.append(tarih_str)
        
        Storage.kaydet(self.dersler)
        self.arayuzu_tazele()

    def ders_ekle(self):
        dialog = DersEkleDialog(self)
        if dialog.exec():
            v = dialog.verileri_al()
            if v["ad"]:
                self.dersler.append(Ders(v["ad"], v["gunler"], v["zorunluluk"]))
                Storage.kaydet(self.dersler)
                self.arayuzu_tazele()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Türkçe tarih formatı için sistem dilini kullanabilirsin
    import locale
    locale.setlocale(locale.LC_ALL, '') 
    
    win = DevamsizlikApp()
    win.show()
    sys.exit(app.exec())