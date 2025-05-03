# -*- coding: utf-8 -*-
"""
Mapulator - Drop Prediction & Time Estimation Tool
© 2025 vasana12
Email: wodud6349@gmail.com
GitHub: https://github.com/vasana12
"""
__version__ = "1.0.0"  # ← 여기에 버전 번호

import sys
import json
import math
from pathlib import Path
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QGroupBox, QFormLayout, QVBoxLayout,
    QLineEdit, QLabel, QPushButton, QHBoxLayout, QComboBox, QPlainTextEdit,
    QMessageBox, QGridLayout, QSpinBox
)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMenuBar, QAction

CONFIG_FILE = Path.home() / ".mapulator" / "drop_configs.json"
CONFIG_FILE.parent.mkdir(exist_ok=True)
# Z-scores for various target probabilities
ZS = {0.5: 0.0, 0.6: 0.2533, 0.7: 0.5244, 0.8: 0.8416, 0.9: 1.2816, 0.99: 2.3263}

class DropTimeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'🎲 Mapulator v{__version__}')
        self.is_measuring = False    # ≤ 측정 상태 플래그
        self.setGeometry(100, 100, 720, 650)
        self.setStyleSheet("""
            QWidget { background: #eef2f5; font-family: 'Segoe UI'; }
            QTabWidget::pane { border: none; }
            QGroupBox { font-weight: bold; border: 1px solid #ccc; border-radius: 5px; margin-top: 10px; background: white; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
            QLabel { font-size: 13px; color: #333; }
            
            QLineEdit, QSpinBox { padding: 6px; font-size: 14px; border: 1px solid #aaa; border-radius: 4px;background: white;}
            QComboBox { padding: 6px; font-size: 14px; border: 1px solid #aaa; border-radius: 4px; background: none; }
            QPushButton { padding: 8px 12px; background: #007bff; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background: #0056b3; }
            QPlainTextEdit { background: white; border: 1px solid #aaa; border-radius: 4px; padding: 6px; font-family: 'Consolas'; font-size: 12px; }
        """
        )
        self.configs = []
        self.load_configs()
        self.initUI()

    def initUI(self):
        tabs = QTabWidget()
        footer = QLabel("© 2025 vasana12  |  📫 wodud6349@gmail.com  |  GitHub: vasana12")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #888; font-size: 11px; margin-top: 10px;")
        tabs.addTab(self.create_save_tab(), '1. 설정 저장')
        tabs.addTab(self.create_kill_tab(), '2. 드랍 예측')
        tabs.addTab(self.create_time_tab(), '3. 시간 측정')

        # 메뉴바 추가
        menubar = QMenuBar(self)
        about_menu = menubar.addMenu("ℹ️ About")
        info_action = QAction("About Mapulator", self)
        info_action.triggered.connect(self.show_about_dialog)
        about_menu.addAction(info_action)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(tabs)
        main_layout.setMenuBar(menubar)
        main_layout.addWidget(footer)
        self.pk_count.setValidator(QIntValidator(1, 9999999, self))
        self.pt_count.setValidator(QIntValidator(1, 9999999, self))

    def show_about_dialog(self):
        QMessageBox.information(self, f"About Mapulator v{__version__}",
            f"Mapulator v{__version__}\n\n"
            "© 2025 vasana12\n"
            "📫 wodud6349@gmail.com\n"
            "🔗 GitHub: https://github.com/vasana12\n\n"
            "Built with ❤️ using Python + PyQt5"
        )

    def create_save_tab(self):
        box = QGroupBox('설정 저장')
        vbox = QVBoxLayout()
        instr = QLabel('몬스터 & 아이템 & 드랍 확률 & 경험치/킬을 입력 후 저장하세요. (Enter 입력 시 저장)')
        form = QFormLayout()
        self.sc_monster = QLineEdit(); self.sc_monster.setPlaceholderText('예: 마티안')
        self.sc_item = QLineEdit(); self.sc_item.setPlaceholderText('예: 촉수')
        self.sc_rate = QLineEdit(); self.sc_rate.setPlaceholderText('예: 50% 또는 0.5')
        self.sc_exp = QLineEdit(); self.sc_exp.setPlaceholderText('예: 120')
        self.sc_exp.returnPressed.connect(self.save_config)
        form.addRow('몬스터 이름:', self.sc_monster)
        form.addRow('아이템 이름:', self.sc_item)
        form.addRow('드랍 확률:', self.sc_rate)
        form.addRow('경험치/킬:', self.sc_exp)
        btn = QPushButton('💾 저장'); btn.clicked.connect(self.save_config)
        hbox = QHBoxLayout(); hbox.addStretch(); hbox.addWidget(btn)
        vbox.addWidget(instr); vbox.addLayout(form); vbox.addLayout(hbox)
        box.setLayout(vbox)
        return box

    def create_kill_tab(self):
        box = QGroupBox('드랍 예측')
        vbox = QVBoxLayout()
        instr = QLabel('설정과 목표 개수를 선택 후 예측 버튼을 클릭하세요.\n 몇 마리 필요할지 계산합니다.')
        instr.setWordWrap(True)

        grid = QGridLayout()
        self.pk_config = QComboBox()
        self.pk_config.addItems([f"{c['monster']} - {c['item']}" for c in self.configs])

        self.pk_count = QLineEdit()
        self.pk_count.setPlaceholderText('예: 300')

        #Enter 키를 누르면 predict_kills() 호출
        self.pk_count.returnPressed.connect(self.predict_kills)
        btn = QPushButton('🔍 예측'); btn.clicked.connect(self.predict_kills)
        self.pk_result = QPlainTextEdit(); self.pk_result.setReadOnly(True)

        grid.addWidget(QLabel('설정 선택:'), 0, 0)
        grid.addWidget(self.pk_config,      0, 1, 1, 2)
        grid.addWidget(QLabel('목표 개수:'), 1, 0)
        grid.addWidget(self.pk_count,       1, 1)
        grid.addWidget(btn,                 1, 2)  # ← 버튼을 같은 행, 오른쪽에
        grid.addWidget(self.pk_result,      2, 0, 1, 3)
        vbox.addWidget(instr)
        vbox.addLayout(grid)
        box.setLayout(vbox)
        return box

    def create_time_tab(self):
        container = QWidget()
        vbox = QVBoxLayout(container)
        top_instr = QLabel('1) 목표를 설정하세요.\n'
                           '2) 시작 경험치 입력 후 [측정 시작] 클릭\n'
                           '3) 측정 종료 후 끝 경험치 입력\n'
                           '4) 예측 실행')
        top_instr.setWordWrap(True)
        vbox.addWidget(top_instr)

        # 1) 설정 확인
        cfg_box = QGroupBox('1) 설정 확인')
        cfg_form = QFormLayout()
        self.pt_config = QComboBox(); self.pt_config.addItems([f"{c['monster']} - {c['item']}" for c in self.configs])
        self.pt_count = QLineEdit(); self.pt_count.setPlaceholderText('예: 300')
        cfg_form.addRow('설정 선택:', self.pt_config)
        cfg_form.addRow('목표 개수:', self.pt_count)
        cfg_box.setLayout(cfg_form); vbox.addWidget(cfg_box)

        meas_box = QGroupBox('2) 측정 설정')
        grid = QGridLayout()

        # 0행: 시작 경험치, 측정 시간, 측정 시작 버튼
        grid.addWidget(QLabel('시작 경험치:'), 0, 0)
        self.pt_start = QLineEdit();
        self.pt_start.setPlaceholderText('시작 경험치')
        grid.addWidget(self.pt_start, 0, 1)
        grid.addWidget(QLabel('측정 시간(분):'), 0, 2)
        self.pt_duration = QSpinBox();
        self.pt_duration.setRange(1, 120);
        self.pt_duration.setValue(5)
        grid.addWidget(self.pt_duration, 0, 3)
        self.pt_button = QPushButton('▶ 측정 시작');
        self.pt_button.clicked.connect(self.toggle_timer)
        grid.addWidget(self.pt_button, 0, 4)

        # 1행: 남은 시간 (더 크게 표시)
        grid.addWidget(QLabel('남은 시간:'), 1, 0)
        self.timer_display = QLabel('00:00')
        self.timer_display.setFont(QFont('Consolas', 24, QFont.Bold))  # 글자 크게
        self.timer_display.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.timer_display, 1, 1, 1, 4)

        # 2행: 시작 시간 (별도 행)
        grid.addWidget(QLabel('시작 시간:'), 2, 0)
        self.start_label = QLabel('--:--:--')
        grid.addWidget(self.start_label, 2, 1, 1, 4)

        # 3행: 종료 시간 (별도 행)
        grid.addWidget(QLabel('종료 시간:'), 3, 0)
        self.end_label = QLabel('--:--:--')
        grid.addWidget(self.end_label, 3, 1, 1, 4)

        # 4행: 끝 경험치 입력
        grid.addWidget(QLabel('끝 경험치:'), 4, 0)
        self.pt_end = QLineEdit();
        self.pt_end.setPlaceholderText('끝 경험치');
        self.pt_end.setEnabled(False)
        grid.addWidget(self.pt_end, 4, 1, 1, 4)

        meas_box.setLayout(grid)
        vbox.addWidget(meas_box)
        # 3) 시간 예측
        pred_box = QGroupBox('3) 시간 예측')
        p_layout = QVBoxLayout()
        btn_pred = QPushButton('⏳ 예측 실행'); btn_pred.clicked.connect(self.predict_time)
        self.pt_result = QPlainTextEdit(); self.pt_result.setReadOnly(True)
        p_layout.addWidget(btn_pred); p_layout.addWidget(self.pt_result)
        pred_box.setLayout(p_layout); vbox.addWidget(pred_box)
        self.timer = QTimer(self);
        self.timer.timeout.connect(self.update_countdown)
        return container

    def toggle_timer(self):
        if not self.is_measuring:
            self._start_measurement()
        else:
            self._stop_measurement(manual=True)

    def _start_measurement(self):
        # 입력 검증
        try:
            duration = self.pt_duration.value()
            _ = int(self.pt_start.text().strip())
        except:
            QMessageBox.warning(self, '오류', '측정 시간과 시작 경험치를 확인하세요.')
            return

        now = datetime.now()
        self.start_time = now
        self.end_time = now + timedelta(minutes=duration)
        self.start_label.setText(f'시작 시간: {now.strftime("%H:%M:%S")}')
        self.end_label.setText(f'종료 시간: {self.end_time.strftime("%H:%M:%S")}')

        self.remaining = duration * 60
        self.timer_display.setText(f'{duration:02d}:00')
        self.timer.start(1000)

        self.is_measuring = True
        self.pt_button.setText('■ 측정 중지')
        self.pt_end.setEnabled(False)

    def _stop_measurement(self, manual: bool = False):
        self.timer.stop()
        self.is_measuring = False
        self.pt_button.setText('▶ 측정 시작')
        self.pt_end.setEnabled(True)
        self.pt_end.setFocus()

        if manual:
            now = datetime.now()
            self.end_label.setText(f'종료 시간: {now.strftime("%H:%M:%S")}')
            QMessageBox.information(self, '측정 중지', '측정이 중지되었습니다. 끝 경험치를 입력하세요.')
        else:
            QMessageBox.information(self, '완료', '측정 시간이 종료되었습니다. 끝 경험치를 입력하세요.')

    def load_configs(self):
        if CONFIG_FILE.exists():
            try: self.configs = json.loads(CONFIG_FILE.read_text())
            except: self.configs = []
        else: self.configs = []


    def save_config(self):
        try:
            mon = self.sc_monster.text().strip(); itm = self.sc_item.text().strip()
            rate_txt = self.sc_rate.text().strip()
            rate = float(rate_txt.rstrip('%'))/100 if rate_txt.endswith('%') else float(rate_txt)
            exp = int(self.sc_exp.text().strip())
            assert mon and itm and 0 < rate < 1
            self.configs.append({'monster': mon, 'item': itm, 'rate': rate, 'exp': exp})
            CONFIG_FILE.write_text(json.dumps(self.configs, ensure_ascii=False, indent=2))
            self.load_configs()
            self.pk_config.clear(); self.pk_config.addItems([f"{c['monster']} - {c['item']}" for c in self.configs])
            self.pt_config.clear(); self.pt_config.addItems([f"{c['monster']} - {c['item']}" for c in self.configs])
            QMessageBox.information(self, '완료', '설정이 저장되었습니다.')
        except Exception as e:
            QMessageBox.warning(self, '오류', f'입력 오류: {e}')

    def predict_kills(self):
        # 입력 유효성 검사
        if not self.pk_count.text().strip():
            QMessageBox.warning(self, '입력 오류', '목표 개수를 입력해주세요.')
            return

        try:
            idx = self.pk_config.currentIndex()
            cfg = self.configs[idx]
            M = int(self.pk_count.text().strip())
            p = cfg['rate']
            results = []
            for P, z in ZS.items():
                a = p*p; b = -2*M*p - z*z*p*(1-p); c = M*M
                disc = b*b - 4*a*c
                n = math.ceil((-b + math.sqrt(disc)) / (2*a))
                results.append(f"{int(P*100)}% 확률: {n} 마리")
            self.pk_result.setPlainText("\n".join(results))
        except Exception as e:
            QMessageBox.warning(self, '예측 오류', f'값을 확인하세요: {e}')

    def start_timer(self):
        try:
            duration = self.pt_duration.value(); _ = int(self.pt_start.text().strip())
        except Exception as e:
            QMessageBox.warning(self, '오류', f'입력 오류: {e}')
            return
        self.start_time = datetime.now(); self.end_time = self.start_time + timedelta(minutes=duration)
        self.start_label.setText(f'시작 시간: {self.start_time.strftime("%H:%M:%S")}')
        self.end_label.setText(f'종료 시간: {self.end_time.strftime("%H:%M:%S")}')
        self.remaining = duration * 60
        self.update_countdown(); self.timer.start(1000)
        self.pt_button.setEnabled(False); self.pt_end.setEnabled(True)

    def update_countdown(self):
        mins, secs = divmod(self.remaining, 60)
        self.timer_display.setText(f'{mins:02d}:{secs:02d}')

        if self.remaining <= 0:
            # 자동으로 종료 처리
            self._stop_measurement(manual=False)

        self.remaining -= 1

    def predict_time(self):
        # 1) 목표 개수 처리 (빈 값일 땐 기본 1개, 비정수면 경고)
        cnt_text = self.pt_count.text().strip()
        if not cnt_text:
            M = 1
        else:
            try:
                M = int(cnt_text)
            except ValueError:
                QMessageBox.warning(self, '입력 오류', '목표 개수는 정수만 입력 가능합니다.')
                return

        # 2) 시작/끝 경험치 유효성 검사
        start_txt = self.pt_start.text().strip()
        end_txt   = self.pt_end.text().strip()
        if not start_txt or not end_txt:
            QMessageBox.warning(self, '입력 오류', '시작·끝 경험치를 모두 입력해주세요.')
            return

        try:
            start_exp = int(start_txt)
            end_exp   = int(end_txt)
        except ValueError:
            QMessageBox.warning(self, '입력 오류', '경험치는 정수만 입력 가능합니다.')
            return

        # 3) 설정 불러오기
        idx      = self.pt_config.currentIndex()
        cfg      = self.configs[idx]
        p, exp_per = cfg['rate'], cfg['exp']

        # 4) 90% 기준 필요 킬 수 계산 (이차방정식 풀이)
        z     = ZS[0.9]
        a     = p * p
        b     = -2 * M * p - z*z * p * (1 - p)
        c     = M * M
        disc  = b*b - 4*a*c
        n_kills = math.ceil((-b + math.sqrt(disc)) / (2*a))

        # 5) 실제 킬 수 계산 (실수)
        delta_exp = end_exp - start_exp
        if delta_exp <= 0:
            QMessageBox.warning(self, '입력 오류', '끝 경험치는 시작 경험치보다 커야 합니다.')
            return
        actual_kills = delta_exp / exp_per

        # 6) 사냥 속도(킬/분) 및 예상 소요 시간 계산
        duration    = self.pt_duration.value()  # 분 단위
        rate        = actual_kills / duration
        time_needed = n_kills / rate

        # 7) 시간 포맷팅 (60분 이상은 시:분)
        if time_needed >= 60:
            hrs     = int(time_needed // 60)
            mins_rem= int(time_needed % 60)
            time_str= f"{hrs}시간 {mins_rem}분"
        else:
            time_str= f"{time_needed:.1f}분"

        # 8) 결과 출력
        self.pt_result.setPlainText(
            f"필요 킬 수(90%): {n_kills} 마리\n"
            f"킬 속도: {rate:.2f} 마리/분\n"
            f"예상 소요 시간: {time_str}"
        )
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')    # ← macOS 기본이 아닌 Fusion 스타일
    window = DropTimeApp()
    window.show()
    sys.exit(app.exec_())
