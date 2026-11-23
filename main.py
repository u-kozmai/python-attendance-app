import os
import sys
import locale
from datetime import date, timedelta

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QWidget,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QTabWidget,
    QScrollArea,
    QFrame,
    QLabel,
    QSpinBox,
    QDateEdit,
    QGroupBox,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QDate

from models import (
    Ders,
    GUNLER,
    pazartesi_mi,
    donem_bitis_tarihi,
    aktif_haftayi_hesapla,
)
from storage import Storage, BASE_DIR
from dialogs import DersEkleDialog


class DevamsizlikApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ders Takip & Devamsızlık Ajandası v2.0")
        self.resize(1250, 780)

        # Kayıtlı dönem ayarlarını ve dersleri yükle
        self.baslangic_tarihi, self.toplam_hafta = Storage.ayarlari_yukle()
        self.dersler = Storage.yukle(toplam_hafta=self.toplam_hafta)

        # Tema dosyasını (style.qss) güvenli yoldan yükle
        stil_yolu = os.path.join(BASE_DIR, "style.qss")
        if os.path.exists(stil_yolu):
            with open(stil_yolu, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

        # Ana Sekme Yapısı
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Sekme Widgetları
        self.takvim_tab = QWidget()
        self.ozet_tab = QWidget()
        self.ayarlar_tab = QWidget()

        self.tabs.addTab(self.takvim_tab, "📅 Haftalık Program")
        self.tabs.addTab(self.ozet_tab, "📊 Genel Özet")
        self.tabs.addTab(self.ayarlar_tab, "⚙️ Ayarlar")

        # Sekme arayüzlerini oluştur
        self.takvim_arayuzunu_kur()
        self.ozet_arayuzunu_kur()
        self.ayarlar_arayuzunu_kur()

        # Bugünün tarihine göre başlangıç haftasını ayarla ve ekranı çiz
        self.hafta_seciciyi_senkronize_et()
        self.arayuzu_tazele()

    def takvim_arayuzunu_kur(self):
        layout = QVBoxLayout(self.takvim_tab)

        # Üst Panel: Hafta Seçimi, Dönem Bilgisi ve Ders Ekle Butonu
        ust_panel = QHBoxLayout()

        self.hafta_secici = QSpinBox()
        self.hafta_secici.setRange(1, self.toplam_hafta)
        self.hafta_secici.setPrefix("Dönem Haftası: ")
        self.hafta_secici.setStyleSheet("font-size: 16px; padding: 6px;")
        self.hafta_secici.valueChanged.connect(self.arayuzu_tazele)
        ust_panel.addWidget(self.hafta_secici)

        self.donem_bilgi_label = QLabel()
        self.donem_bilgi_label.setObjectName("DonemBilgiEtiketi")
        ust_panel.addWidget(self.donem_bilgi_label)

        ust_panel.addStretch()

        self.ekle_btn = QPushButton("+ Yeni Ders Ekle")
        self.ekle_btn.setObjectName("PrimaryButon")
        self.ekle_btn.setCursor(Qt.PointingHandCursor)
        self.ekle_btn.clicked.connect(self.ders_ekle)
        ust_panel.addWidget(self.ekle_btn)

        layout.addLayout(ust_panel)

        # Haftalık Günler (Scroll Area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.gunler_container = QWidget()
        self.gunler_layout = QHBoxLayout(self.gunler_container)

        self.gun_column_widgets = {}
        for gun in GUNLER:
            gun_v_layout = QVBoxLayout()

            # Gün Başlığı
            baslik = QLabel(f"<b>{gun}</b>")
            baslik.setAlignment(Qt.AlignCenter)
            baslik.setStyleSheet("font-size: 15px; color: #64b5f6; padding: 2px;")
            gun_v_layout.addWidget(baslik)

            # Tarih Etiketi
            tarih_label = QLabel("--")
            tarih_label.setAlignment(Qt.AlignCenter)
            gun_v_layout.addWidget(tarih_label)

            # Ders kutucuklarının listeleneceği dikey kutu
            ders_list_frame = QFrame()
            ders_list_frame.setFrameShape(QFrame.StyledPanel)
            ders_list_frame.setMinimumWidth(155)
            inner_layout = QVBoxLayout(ders_list_frame)
            inner_layout.setSpacing(8)
            inner_layout.addStretch()

            gun_v_layout.addWidget(ders_list_frame)
            self.gunler_layout.addLayout(gun_v_layout)

            self.gun_column_widgets[gun] = {
                "layout": inner_layout,
                "tarih_label": tarih_label,
            }

        scroll.setWidget(self.gunler_container)
        layout.addWidget(scroll)

    def ozet_arayuzunu_kur(self):
        layout = QVBoxLayout(self.ozet_tab)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels([
            "Ders Adı",
            "Toplam Ders (S)",
            "Devamsızlık Hakkı",
            "Gidilmeyen (S)",
            "Kalan Hak (S)",
            "Durum",
            "İşlem",
        ])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.tablo.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tablo)

    def ayarlar_arayuzunu_kur(self):
        ana_layout = QVBoxLayout(self.ayarlar_tab)
        ana_layout.setContentsMargins(30, 30, 30, 30)

        ayar_grubu = QGroupBox("Dönem Oluşturma ve Ayarları")
        ayar_grubu.setMaximumWidth(600)
        grup_layout = QVBoxLayout(ayar_grubu)
        grup_layout.setSpacing(14)

        aciklama = QLabel(
            "Üniversitenizin dönem başlangıç tarihini ve toplam hafta sayısını aşağıdan "
            "ayarlayabilirsiniz. Dönem başlangıç tarihi mutlaka bir <b>Pazartesi</b> günü olmalıdır."
        )
        aciklama.setWordWrap(True)
        grup_layout.addWidget(aciklama)

        form = QFormLayout()
        form.setSpacing(12)

        # Dönem Başlangıç Tarihi Seçici
        self.baslangic_date_edit = QDateEdit()
        self.baslangic_date_edit.setCalendarPopup(True)
        self.baslangic_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.baslangic_date_edit.setDate(
            QDate(
                self.baslangic_tarihi.year,
                self.baslangic_tarihi.month,
                self.baslangic_tarihi.day,
            )
        )
        self.baslangic_date_edit.dateChanged.connect(self.ayar_onizleme_guncelle)
        form.addRow("Dönem Başlangıç Tarihi:", self.baslangic_date_edit)

        # Seçilen Günün Pazartesi Olup Olmadığını Gösteren Canlı Etiket
        self.secilen_gun_label = QLabel()
        form.addRow("Seçilen Gün:", self.secilen_gun_label)

        # Dönemdeki Hafta Sayısı
        self.hafta_sayisi_input = QSpinBox()
        self.hafta_sayisi_input.setRange(1, 52)
        self.hafta_sayisi_input.setSuffix(" Hafta")
        self.hafta_sayisi_input.setValue(self.toplam_hafta)
        self.hafta_sayisi_input.valueChanged.connect(self.ayar_onizleme_guncelle)
        form.addRow("Dönemdeki Hafta Sayısı:", self.hafta_sayisi_input)

        grup_layout.addLayout(form)

        # Hesaplanan Dönem Aralığı Önizlemesi
        self.donem_ozet_label = QLabel()
        self.donem_ozet_label.setObjectName("BilgiEtiketi")
        self.donem_ozet_label.setWordWrap(True)
        grup_layout.addWidget(self.donem_ozet_label)

        # Kaydet Butonu
        self.ayarlari_kaydet_btn = QPushButton("Dönem Ayarlarını Kaydet")
        self.ayarlari_kaydet_btn.setObjectName("PrimaryButon")
        self.ayarlari_kaydet_btn.setCursor(Qt.PointingHandCursor)
        self.ayarlari_kaydet_btn.clicked.connect(self.ayarlari_kaydet)
        grup_layout.addWidget(self.ayarlari_kaydet_btn)

        ana_layout.addWidget(ayar_grubu, alignment=Qt.AlignTop | Qt.AlignHCenter)
        ana_layout.addStretch()

        self.ayar_onizleme_guncelle()

    def ayar_onizleme_guncelle(self):
        qdate = self.baslangic_date_edit.date()
        secilen_tarih = date(qdate.year(), qdate.month(), qdate.day())
        gun_adi = GUNLER[secilen_tarih.weekday()]
        hafta_sayisi = self.hafta_sayisi_input.value()

        if pazartesi_mi(secilen_tarih):
            self.secilen_gun_label.setText(f"{gun_adi} (Uygun)")
            self.secilen_gun_label.setStyleSheet("color: #66bb6a; font-weight: bold;")
        else:
            self.secilen_gun_label.setText(f"{gun_adi} — Pazartesi günü seçmelisiniz!")
            self.secilen_gun_label.setStyleSheet("color: #ff5252; font-weight: bold;")

        bitis = donem_bitis_tarihi(secilen_tarih, hafta_sayisi)
        bugun = date.today()
        acilis_haftasi = aktif_haftayi_hesapla(secilen_tarih, hafta_sayisi, bugun)

        if secilen_tarih <= bugun <= bitis:
            durum_metni = f"Bugün ({bugun.strftime('%d.%m.%Y')}) bu dönemin {acilis_haftasi}. haftasına denk geliyor."
        else:
            durum_metni = (
                f"Bugün ({bugun.strftime('%d.%m.%Y')}) bu dönem aralığında değil; "
                f"açılışta 1. hafta gösterilecek."
            )

        self.donem_ozet_label.setText(
            f"Dönem Aralığı: {secilen_tarih.strftime('%d.%m.%Y')} - {bitis.strftime('%d.%m.%Y')} "
            f"({hafta_sayisi} Hafta)\n{durum_metni}"
        )

    def ayarlari_kaydet(self):
        qdate = self.baslangic_date_edit.date()
        yeni_baslangic = date(qdate.year(), qdate.month(), qdate.day())
        yeni_hafta_sayisi = self.hafta_sayisi_input.value()

        # Pazartesi kontrolü
        if not pazartesi_mi(yeni_baslangic):
            secilen_gun = GUNLER[yeni_baslangic.weekday()]
            QMessageBox.warning(
                self,
                "Geçersiz Başlangıç Tarihi",
                f"Seçtiğiniz tarih ({yeni_baslangic.strftime('%d.%m.%Y')}) {secilen_gun} gününe denk geliyor.\n\n"
                "Dönem başlangıç tarihi mutlaka bir Pazartesi günü olmalıdır.\n"
                "Lütfen bir Pazartesi günü seçerek tekrar deneyin.",
            )
            self.baslangic_date_edit.setFocus()
            return

        # Ayarları güncelle ve kaydet
        self.baslangic_tarihi = yeni_baslangic
        self.toplam_hafta = yeni_hafta_sayisi
        Storage.ayarlari_kaydet(self.baslangic_tarihi, self.toplam_hafta)

        # Mevcut tüm derslerin toplam hafta sayısını güncelle
        for ders in self.dersler:
            ders.toplam_hafta = self.toplam_hafta

        self.hafta_seciciyi_senkronize_et()
        self.arayuzu_tazele()

        bitis = donem_bitis_tarihi(self.baslangic_tarihi, self.toplam_hafta)
        aktif_hafta = self.hafta_secici.value()
        QMessageBox.information(
            self,
            "Dönem Kaydedildi",
            f"Yeni dönem başarıyla kaydedildi!\n\n"
            f"Dönem: {self.baslangic_tarihi.strftime('%d.%m.%Y')} - {bitis.strftime('%d.%m.%Y')} "
            f"({self.toplam_hafta} Hafta)\n"
            f"Aktif gösterilen hafta: {aktif_hafta}. Hafta",
        )

    def hafta_seciciyi_senkronize_et(self):
        aktif_hafta = aktif_haftayi_hesapla(self.baslangic_tarihi, self.toplam_hafta)
        self.hafta_secici.blockSignals(True)
        self.hafta_secici.setRange(1, self.toplam_hafta)
        self.hafta_secici.setValue(aktif_hafta)
        self.hafta_secici.blockSignals(False)

    def arayuzu_tazele(self):
        # Dönem bilgi etiketini güncelle
        bitis = donem_bitis_tarihi(self.baslangic_tarihi, self.toplam_hafta)
        self.donem_bilgi_label.setText(
            f"Aktif Dönem: {self.baslangic_tarihi.strftime('%d.%m.%Y')} - "
            f"{bitis.strftime('%d.%m.%Y')} ({self.toplam_hafta} Hafta)"
        )

        # 1. Özet Tablosunu Güncelle
        self.tablo.setRowCount(0)
        for d in self.dersler:
            row = self.tablo.rowCount()
            self.tablo.insertRow(row)

            su_an = d.su_anki_devamsizlik_saati()
            hak_saat = d.devamsizlik_hakki_saat()
            hak_yuzde = d.devamsizlik_hakki_yuzde()
            kalan = d.kalan_hak_saat()
            durum = "GEÇTİ" if su_an <= hak_saat else "KALDI"

            self.tablo.setItem(row, 0, QTableWidgetItem(d.ad))
            self.tablo.setItem(row, 1, QTableWidgetItem(str(d.toplam_saat())))
            self.tablo.setItem(
                row,
                2,
                QTableWidgetItem(f"{hak_saat:.1f} Saat (%{hak_yuzde:.1f})"),
            )
            self.tablo.setItem(row, 3, QTableWidgetItem(str(su_an)))

            kalan_item = QTableWidgetItem(f"{kalan:.1f}")
            if kalan < 0:
                kalan_item.setForeground(QColor("#ff5252"))
            elif kalan == 0:
                kalan_item.setForeground(QColor("#ffb74d"))
            else:
                kalan_item.setForeground(QColor("#66bb6a"))
            self.tablo.setItem(row, 4, kalan_item)

            durum_item = QTableWidgetItem(durum)
            if durum == "KALDI":
                durum_item.setForeground(QColor("#ff5252"))
            else:
                durum_item.setForeground(QColor("#66bb6a"))
            self.tablo.setItem(row, 5, durum_item)

            sil_btn = QPushButton("Sil")
            sil_btn.setObjectName("SilButonu")
            sil_btn.setCursor(Qt.PointingHandCursor)
            sil_btn.clicked.connect(lambda checked=False, ders=d: self.ders_sil(ders))
            self.tablo.setCellWidget(row, 6, sil_btn)

        # 2. Takvim Görünümünü Güncelle
        secili_hafta = self.hafta_secici.value()
        bugun = date.today()

        for gun_adi, refs in self.gun_column_widgets.items():
            # Eski kutucukları temizle (en sondaki stretch hariç)
            while refs["layout"].count() > 1:
                child = refs["layout"].takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Günün tarihini hesapla ve yaz
            gun_idx = GUNLER.index(gun_adi)
            tarih_obj = self.baslangic_tarihi + timedelta(
                days=((secili_hafta - 1) * 7 + gun_idx)
            )
            tarih_str = tarih_obj.isoformat()

            if tarih_obj == bugun:
                refs["tarih_label"].setText(f"{tarih_obj.strftime('%d %b')} (Bugün)")
                refs["tarih_label"].setStyleSheet("color: #ffd54f; font-weight: bold;")
            else:
                refs["tarih_label"].setText(tarih_obj.strftime("%d %b"))
                refs["tarih_label"].setStyleSheet("color: #b0b0b0;")

            # O güne ait her ders için saat sayısı kadar 1'er saatlik kutucuk ekle
            for ders in self.dersler:
                if gun_adi in ders.gunler:
                    saat_sayisi = ders.gunler[gun_adi]
                    for saat_no in range(1, saat_sayisi + 1):
                        btn = QPushButton(f"{ders.ad}\n{saat_no}. Saat (1s)")
                        btn.setObjectName("DersButonu")
                        btn.setMinimumHeight(52)
                        btn.setCursor(Qt.PointingHandCursor)

                        if ders.devamsizlik_var_mi(tarih_str, saat_no):
                            btn.setStyleSheet(
                                "background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                                "stop:0 #ff5252, stop:1 #b71c1c);"
                            )
                            btn.setToolTip("Devamsız işaretli — Geri almak için tıklayın")
                        else:
                            btn.setStyleSheet(
                                "background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                                "stop:0 #66bb6a, stop:1 #2e7d32);"
                            )
                            btn.setToolTip("Katılındı — Devamsızlık eklemek için tıklayın")

                        btn.clicked.connect(
                            lambda checked=False, d=ders, t=tarih_str, s=saat_no: self.devamsizlik_toggle(d, t, s)
                        )
                        refs["layout"].insertWidget(refs["layout"].count() - 1, btn)

    def devamsizlik_toggle(self, ders, tarih_str, saat_no):
        ders.devamsizlik_degistir(tarih_str, saat_no)
        Storage.kaydet(self.dersler)
        self.arayuzu_tazele()

    def ders_ekle(self):
        dialog = DersEkleDialog(toplam_hafta=self.toplam_hafta, parent=self)
        if dialog.exec():
            v = dialog.verileri_al()
            yeni_ders = Ders(
                ad=v["ad"],
                gunler=v["gunler"],
                hak_tipi=v["hak_tipi"],
                hak_degeri=v["hak_degeri"],
                toplam_hafta=self.toplam_hafta,
            )
            self.dersler.append(yeni_ders)
            Storage.kaydet(self.dersler)
            self.arayuzu_tazele()

    def ders_sil(self, ders):
        cevap = QMessageBox.question(
            self,
            "Dersi Sil",
            f"'{ders.ad}' dersini ve tüm devamsızlık kayıtlarını silmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if cevap == QMessageBox.Yes:
            self.dersler.remove(ders)
            Storage.kaydet(self.dersler)
            self.arayuzu_tazele()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        pass

    win = DevamsizlikApp()
    win.show()
    sys.exit(app.exec())
