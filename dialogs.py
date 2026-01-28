from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QSpinBox, 
                             QCheckBox, QHBoxLayout, QDialogButtonBox)

class DersEkleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Ders Ekle")
        self.setMinimumWidth(350)
        self.layout = QFormLayout(self)

        self.ad_input = QLineEdit()
        self.layout.addRow("Ders Adı:", self.ad_input)

        self.zorunluluk_input = QSpinBox()
        self.zorunluluk_input.setRange(0, 100)
        self.zorunluluk_input.setValue(70)
        self.layout.addRow("Devam Zorunluluğu (%):", self.zorunluluk_input)

        self.gun_inputlar = {}
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        
        for gun in gunler:
            h_layout = QHBoxLayout()
            cb = QCheckBox(gun)
            sb = QSpinBox()
            sb.setRange(1, 12)
            sb.setEnabled(False)
            cb.stateChanged.connect(lambda state, s=sb: s.setEnabled(state == 2))
            h_layout.addWidget(cb)
            h_layout.addWidget(sb)
            self.layout.addRow(h_layout)
            self.gun_inputlar[gun] = (cb, sb)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addRow(self.buttons)

    def verileri_al(self):
        secili_gunler = {gun: sb.value() for gun, (cb, sb) in self.gun_inputlar.items() if cb.isChecked()}
        return {
            "ad": self.ad_input.text(),
            "gunler": secili_gunler,
            "zorunluluk": self.zorunluluk_input.value()
        }