from os import path
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from src.macro import Macro

VERSION = "0.1.0"


class App(QWidget):
    def __init__(self) -> None:
        super().__init__()
        grid = QGridLayout()
        self.setLayout(grid)

        grid.addWidget(QLabel("비밀번호:"), 0, 0)
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        grid.addWidget(self.pw_input, 0, 1)

        grid.addWidget(QLabel("웹주소:"), 1, 0)
        self.url_input = QLineEdit()
        grid.addWidget(self.url_input, 1, 1)

        opt_r_group = QGroupBox("옵션 여부")
        self.opt_r_1 = QRadioButton("예")
        self.opt_r_2 = QRadioButton("아니오")
        self.opt_r_1.clicked.connect(self.on_valueChanged)
        self.opt_r_2.clicked.connect(self.on_valueChanged)
        self.opt_r_2.setChecked(True)
        opt_r_group_layout = QHBoxLayout()
        opt_r_group.setLayout(opt_r_group_layout)
        opt_r_group_layout.addWidget(self.opt_r_1)
        opt_r_group_layout.addWidget(self.opt_r_2)
        grid.addWidget(opt_r_group, 2, 0, 1, 2)

        grid.addWidget(QLabel("옵션 번호:"), 3, 0)
        self.opt_input = QSpinBox()
        self.opt_input.setRange(-1, 10)
        self.opt_input.setDisabled(True)
        grid.addWidget(self.opt_input, 3, 1)

        self.button = QPushButton("실행", self)
        self.button.clicked.connect(self.on_clicked)
        grid.addWidget(self.button, 4, 0, 1, 2)

        self.log_output = QTextEdit(readOnly=True)
        grid.addWidget(self.log_output, 5, 0, 1, 2)

        self.macro = Macro()
        self.macro.logged.connect(self.on_logged)
        self.macro.finished.connect(self.on_finished)

        self.setWindowTitle(f"nash v{VERSION}")
        self.resize(400, 400)
        self.show()

    def on_clicked(self) -> None:
        self.log_output.clear()
        if self.button.text() == "실행":
            if len(self.pw_input.text()) != 6:
                self.log_output.append("비밀번호를 제대로 입력해주세요.")
                return
            self.macro.pw = self.pw_input.text()
            self.macro.url = self.url_input.text()
            if self.opt_input.isEnabled():
                self.macro.opt = int(self.opt_input.text())
            self.macro.start()
            self.button.setText("중단")
        else:
            self.macro.terminate()
            self.button.setText("실행")

    def on_logged(self, log: str) -> None:
        self.log_output.append(log)

    def on_finished(self) -> None:
        self.button.setText("실행")

    def on_valueChanged(self, value: int) -> None:
        self.opt_input.setDisabled(not self.opt_r_1.isChecked())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
