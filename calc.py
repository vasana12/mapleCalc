import sys
import json
import math
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QLabel, QLineEdit, QPushButton,
    QFormLayout, QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox,
    QPlainTextEdit, QMessageBox, QGridLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer

CONFIG_FILE = Path("drop_configs.json")

class DropTimeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('🎲 드랍 설정 & 예측 계산기')
        self.setGeometry(100, 100, 640, 520)
        self.setStyleSheet("""
            QWidget { background-color: #fafafa; font-family: 'Segoe UI', sans-serif; }
            QTabWidget::pane { border: none; }
            QGroupBox { font-weight: bold; border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; }
            QGroupBox:title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
            QLabel { font-size: 13px; }
            QLineEdit, QComboBox { padding: 5px; font-size: 13px; border: 1px solid #ccc; border-radius: 4px; }
            QPushButton { padding: 6px 12px; background-color: #0066cc; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #005bb5; }
            QPlainTextEdit { background-color: #fff; border: 1px solid #ccc; border-radius: 4px; padding: 6px; font-family: Consolas, monospace; font-size: 12px; }
        """
        )
        self.configs = []
        self.initUI()
        self.load_configs()

    def initUI(self):
        tabs = QTabWidget()
        tabs.addTab(self.create_save_tab(), "1. 설정 저장")
        tabs.addTab(self.create_kill_tab(), "2. 킬 예측")
        tabs.addTab(self.create_time_tab(), "3. 시간 예측")

        layout = QVBoxLayout(self)
        layout.addWidget(tabs)

    def create_save_tab(self):
        group = QGroupBox('설정 저장')
        layout = QFormLayout()
        self.sc_monster = QLineEdit(); self.sc_monster.setPlaceholderText("예) 커즈아이")
        self.sc_item = QLineEdit(); self.sc_item.setPlaceholderText("예) 땅문서")
        self.sc_rate = QLineEdit(); self.sc_rate.setPlaceholderText("예) 1/12500 or 0.5% or 0.005")
        self.sc_exp = QLineEdit(); self.sc_exp.setPlaceholderText("정수 입력")
        layout.addRow('몬스터:', self.sc_monster)
        layout.addRow('아이템:', self.sc_item)
        layout.addRow('드랍 확률:', self.sc_rate)
        layout.addRow('경험치/킬:', self.sc_exp)
        btn = QPushButton('저장'); btn.clicked.connect(self.save_config)
        btn_layout = QHBoxLayout(); btn_layout.addStretch(); btn_layout.addWidget(btn)
        vbox = QVBoxLayout(); vbox.addLayout(layout); vbox.addLayout(btn_layout)
        group.setLayout(vbox)
        return group

    def create_kill_tab(self):
        group = QGroupBox('킬 예측')
        layout = QGridLayout()
        self.pk_config = QComboBox()
        self.pk_target = QComboBox()
        self.pk_target.addItems(["50%", "60%", "90%", "99%", "커스텀"])
        self.pk_custom = QLineEdit(); self.pk_custom.setPlaceholderText("예) 95% 입력"); self.pk_custom.setEnabled(False)
        self.pk_target.currentTextChanged.connect(
            lambda txt: self.pk_custom.setEnabled(txt == "커스텀")
        )
        layout.addWidget(QLabel('설정:'), 0, 0)
        layout.addWidget(self.pk_config, 0, 1)
        layout.addWidget(QLabel('목표 확률:'), 1, 0)
        layout.addWidget(self.pk_target, 1, 1)
        layout.addWidget(self.pk_custom, 1, 2)
        btn = QPushButton('예측'); btn.clicked.connect(self.predict_kills)
        layout.addWidget(btn, 2, 2)
        self.pk_result = QPlainTextEdit(); self.pk_result.setReadOnly(True)
        layout.addWidget(self.pk_result, 3, 0, 1, 3)
        group.setLayout(layout)
        return group

    def create_time_tab(self):
        group = QGroupBox('시간 예측')
        layout = QGridLayout()
        self.pt_config = QComboBox()
        self.pt_start = QLineEdit(); self.pt_start.setPlaceholderText("시작 경험치")
        self.pt_end = QLineEdit(); self.pt_end.setPlaceholderText("5분 후 경험치"); self.pt_end.setEnabled(False)
        self.pt_button = QPushButton('측정 시작'); self.pt_button.clicked.connect(self.start_timer)
        layout.addWidget(QLabel('설정:'), 0, 0)
        layout.addWidget(self.pt_config, 0, 1)
        layout.addWidget(QLabel('시작 경험치:'), 1, 0)
        layout.addWidget(self.pt_start, 1, 1)
        layout.addWidget(self.pt_button, 1, 2)
        layout.addWidget(QLabel('5분 후 경험치:'), 2, 0)
        layout.addWidget(self.pt_end, 2, 1)
        btn = QPushButton('예측'); btn.clicked.connect(self.predict_time)
        layout.addWidget(btn, 3, 2)
        self.pt_result = QPlainTextEdit(); self.pt_result.setReadOnly(True)
        layout.addWidget(self.pt_result, 4, 0, 1, 3)
        group.setLayout(layout)
        return group

    def load_configs(self):
        try:
            self.configs = json.loads(CONFIG_FILE.read_text()) if CONFIG_FILE.exists() else []
        except:
            self.configs = []
        items = [f"{c['monster']} - {c['item']}" for c in self.configs]
        for combo in (self.pk_config, self.pt_config):
            combo.clear(); combo.addItems(items)

    def save_config(self):
        try:
            mon = self.sc_monster.text().strip(); itm = self.sc_item.text().strip()
            txt = self.sc_rate.text().strip()
            rate = (lambda x: int(x.split('/')[0])/int(x.split('/')[1]) if '/' in x else float(x.rstrip('%'))/100 if x.endswith('%') else float(x))(txt)
            exp = int(self.sc_exp.text().strip())
            assert mon and itm and 0 < rate < 1
            self.configs.append({'monster':mon,'item':itm,'rate':rate,'exp':exp})
            CONFIG_FILE.write_text(json.dumps(self.configs))
            self.load_configs()
            QMessageBox.information(self, '완료', '설정이 저장되었습니다.')
        except:
            QMessageBox.warning(self, '오류', '입력을 확인해주세요.')

    def predict_kills(self):
        try:
            cfg = self.configs[self.pk_config.currentIndex()]
            txt = self.pk_target.currentText()
            p = float(self.pk_custom.text())/100 if txt == '커스텀' else float(txt.rstrip('%'))/100
            fr = 1 - cfg['rate']
            n = math.ceil(math.log10(1 - p) / math.log10(fr))
            self.pk_result.setPlainText(f"목표 {p*100:.1f}% 달성 → {n} 마리 필요")
        except:
            self.pk_result.setPlainText('예측 오류: 설정과 확률을 확인하세요.')

    def start_timer(self):
        try:
            int(self.pt_start.text())
            self.pt_button.setEnabled(False); self.pt_end.setEnabled(True)
            QTimer.singleShot(5*60*1000, lambda: QMessageBox.information(self, '완료', '5분 경과! 경험치 입력하세요.'))
        except:
            QMessageBox.warning(self, '오류', '시작 경험치를 확인하세요.')

    def predict_time(self):
        try:
            cfg = self.configs[self.pt_config.currentIndex()]
            start, end = int(self.pt_start.text()), int(self.pt_end.text())
            kills = (end - start) // cfg['exp']
            rate = kills / 5
            time_min = (1 / cfg['rate']) / rate
            self.pt_result.setPlainText(f"킬 속도: {rate:.2f}마리/분\n예상 드랍 시간: {time_min:.1f}분")
        except:
            self.pt_result.setPlainText('예측 오류: 설정과 경험치를 확인하세요.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DropTimeApp(); window.show()
    sys.exit(app.exec_())
