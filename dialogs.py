from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QRadioButton,
    QLabel,
    QGroupBox,
    QDialogButtonBox,
    QMessageBox,
)
from models import GUNLER


class DersEkleDialog(QDialog):
    def __init__(self, toplam_hafta=12, parent=None):
        super().__init__(parent)
        self.toplam_hafta = toplam_hafta
        self.setWindowTitle("Yeni Ders Ekle")
        self.setMinimumWidth(440)

        ana_layout = QVBoxLayout(self)

        # 1. Ders Adı
        ad_form = QFormLayout()
        self.ad_input = QLineEdit()
        self.ad_input.setPlaceholderText("Örn: MAT101, Fizik 1, Algoritmalar...")
        ad_form.addRow("Ders Adı:", self.ad_input)
        ana_layout.addLayout(ad_form)

        # 2. Ders Günleri ve Günlük Saatler
        gunler_grubu = QGroupBox("Haftalık Ders Programı (Her Saat 1 Kutucuk Oluşturur)")
        gunler_layout = QVBoxLayout(gunler_grubu)

        self.gun_inputlar = {}
        for gun in GUNLER:
            satir = QHBoxLayout()
            cb = QCheckBox(gun)
            cb.setMinimumWidth(110)

            sb = QSpinBox()
            sb.setRange(1, 12)
            sb.setValue(1)
            sb.setSuffix(" saat")
            sb.setEnabled(False)

            cb.toggled.connect(lambda secili, s=sb: self.gun_secimi_degisti(secili, s))
            sb.valueChanged.connect(self.saat_bilgisini_guncelle)

            satir.addWidget(cb)
            satir.addStretch()
            satir.addWidget(sb)
            gunler_layout.addLayout(satir)

            self.gun_inputlar[gun] = (cb, sb)

        self.toplam_saat_label = QLabel()
        self.toplam_saat_label.setObjectName("BilgiEtiketi")
        gunler_layout.addWidget(self.toplam_saat_label)
        ana_layout.addWidget(gunler_grubu)

        # 3. Devamsızlık Hakkı (Birbiriyle Orantılı Yüzde / Saat Seçenekleri)
        hak_grubu = QGroupBox("Devamsızlık Hakkı (Yüzde ve Saat Birbiriyle Orantılıdır)")
        hak_layout = QVBoxLayout(hak_grubu)

        # Seçenek 1: Yüzde (%)
        yuzde_satir = QHBoxLayout()
        self.yuzde_radio = QRadioButton("Yüzde (%) olarak hak:")
        self.yuzde_radio.setChecked(True)
        self.yuzde_input = QDoubleSpinBox()
        self.yuzde_input.setRange(0.0, 100.0)
        self.yuzde_input.setDecimals(1)
        self.yuzde_input.setSingleStep(5.0)
        self.yuzde_input.setValue(30.0)
        self.yuzde_input.setSuffix(" %")
        yuzde_satir.addWidget(self.yuzde_radio)
        yuzde_satir.addStretch()
        yuzde_satir.addWidget(self.yuzde_input)
        hak_layout.addLayout(yuzde_satir)

        # Seçenek 2: Saat
        saat_satir = QHBoxLayout()
        self.saat_radio = QRadioButton("Saat olarak hak:")
        self.saat_input = QDoubleSpinBox()
        self.saat_input.setRange(0.0, 0.0)
        self.saat_input.setDecimals(1)
        self.saat_input.setSingleStep(1.0)
        self.saat_input.setValue(0.0)
        self.saat_input.setSuffix(" saat")
        self.saat_input.setEnabled(False)
        saat_satir.addWidget(self.saat_radio)
        saat_satir.addStretch()
        saat_satir.addWidget(self.saat_input)
        hak_layout.addLayout(saat_satir)

        self.hak_ozet_label = QLabel()
        self.hak_ozet_label.setObjectName("BilgiEtiketi")
        self.hak_ozet_label.setWordWrap(True)
        hak_layout.addWidget(self.hak_ozet_label)
        ana_layout.addWidget(hak_grubu)

        # Sinyalleri bağla
        self.yuzde_radio.toggled.connect(self.hak_modu_degisti)
        self.yuzde_input.valueChanged.connect(self.yuzdeden_saate_guncelle)
        self.saat_input.valueChanged.connect(self.saatten_yuzdeye_guncelle)

        # 4. Kaydet / İptal Butonları
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setText("Dersi Ekle")
        self.buttons.button(QDialogButtonBox.Cancel).setText("İptal")
        self.buttons.accepted.connect(self.onayla)
        self.buttons.rejected.connect(self.reject)
        ana_layout.addWidget(self.buttons)

        # İlk açılışta etiketleri hesapla
        self.saat_bilgisini_guncelle()

    def gun_secimi_degisti(self, secili, spinbox):
        spinbox.setEnabled(secili)
        self.saat_bilgisini_guncelle()

    def haftalik_toplam_saat(self):
        return sum(sb.value() for cb, sb in self.gun_inputlar.values() if cb.isChecked())

    def donem_toplam_saati(self):
        return self.haftalik_toplam_saat() * self.toplam_hafta

    def hak_modu_degisti(self):
        yuzde_secili = self.yuzde_radio.isChecked()
        self.yuzde_input.setEnabled(yuzde_secili)
        self.saat_input.setEnabled(not yuzde_secili)
        self.saat_bilgisini_guncelle()

    def saat_bilgisini_guncelle(self):
        haftalik = self.haftalik_toplam_saat()
        toplam = self.donem_toplam_saati()

        self.toplam_saat_label.setText(
            f"Haftalık: {haftalik} saat  |  Dönem Toplamı ({self.toplam_hafta} Hafta): {toplam} saat"
        )

        # Saat girişinin üst sınırını dönem toplam saatine eşitle
        self.saat_input.blockSignals(True)
        self.saat_input.setMaximum(float(toplam))
        self.saat_input.blockSignals(False)

        if self.yuzde_radio.isChecked():
            self.yuzdeden_saate_guncelle()
        else:
            self.saatten_yuzdeye_guncelle()

    def yuzdeden_saate_guncelle(self):
        toplam = self.donem_toplam_saati()
        yuzde = self.yuzde_input.value()
        saat_hakki = toplam * (yuzde / 100.0)

        self.saat_input.blockSignals(True)
        self.saat_input.setValue(saat_hakki)
        self.saat_input.blockSignals(False)

        self.hak_ozetini_yazdir(toplam, yuzde, saat_hakki)

    def saatten_yuzdeye_guncelle(self):
        toplam = self.donem_toplam_saati()
        saat_hakki = self.saat_input.value()
        yuzde = (saat_hakki / toplam) * 100.0 if toplam > 0 else 0.0

        self.yuzde_input.blockSignals(True)
        self.yuzde_input.setValue(yuzde)
        self.yuzde_input.blockSignals(False)

        self.hak_ozetini_yazdir(toplam, yuzde, saat_hakki)

    def hak_ozetini_yazdir(self, toplam, yuzde, saat_hakki):
        if toplam == 0:
            self.hak_ozet_label.setText("Orantılı hesaplama için yukarıdan en az bir ders günü seçiniz.")
        else:
            devam_yuzdesi = max(0.0, 100.0 - yuzde)
            self.hak_ozet_label.setText(
                f"Toplam {toplam} saat derste en fazla {saat_hakki:.1f} saat (%{yuzde:.1f}) "
                f"devamsızlık hakkı (%{devam_yuzdesi:.1f} devam zorunluluğu)."
            )

    def onayla(self):
        if not self.ad_input.text().strip():
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen bir ders adı girin.")
            self.ad_input.setFocus()
            return

        if self.haftalik_toplam_saat() == 0:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen en az bir ders günü seçin.")
            return

        self.accept()

    def verileri_al(self):
        secili_gunler = {
            gun: sb.value()
            for gun, (cb, sb) in self.gun_inputlar.items()
            if cb.isChecked()
        }
        if self.yuzde_radio.isChecked():
            hak_tipi = "yuzde"
            hak_degeri = self.yuzde_input.value()
        else:
            hak_tipi = "saat"
            hak_degeri = self.saat_input.value()

        return {
            "ad": self.ad_input.text().strip(),
            "gunler": secili_gunler,
            "hak_tipi": hak_tipi,
            "hak_degeri": hak_degeri,
        }
