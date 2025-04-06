import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QComboBox, QPushButton,
                             QTextEdit, QWidget, QPlainTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
import center

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.num = 0
        self.result = "初始结果"
        self.initUI()

    def initUI(self):
        # 设置主窗口属性
        self.setWindowTitle('有聊ai Utalk')
        self.setGeometry(0, 0, 1000, 800)

        # 设置背景颜色
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 250))
        self.setPalette(palette)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 输入框部分
        input_layout = QHBoxLayout()
        input_label = QLabel("输入内容:")
        input_label.setFont(QFont('华文仿宋', 12))

        self.input_box = QPlainTextEdit()
        self.input_box.setPlaceholderText("请输入文本...")
        self.input_box.setFont(QFont('华文仿宋', 12))
        self.input_box.setMaximumHeight(80)
        self.input_box.setStyleSheet("""
            QPlainTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_box)
        input_layout.addStretch()

        # 选择框部分
        combo_layout = QHBoxLayout()
        combo_label = QLabel("选择选项:")
        combo_label.setFont(QFont('华文仿宋', 12))

        self.combo_box = QComboBox()
        self.combo_box.addItems(["文心一言", "文生图", "文生视频", "高质量视频*"])
        self.combo_box.setFont(QFont('华文仿宋', 12))
        self.combo_box.setMaximumWidth(200)

        combo_layout.addWidget(combo_label)
        combo_layout.addWidget(self.combo_box)
        combo_layout.addStretch()

        # 按钮部分
        button_layout = QHBoxLayout()
        self.process_button = QPushButton("Go")
        self.process_button.setFont(QFont('Arial Black', 12, QFont.Bold))
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #6600cc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.process_button.clicked.connect(self.on_button_click)

        button_layout.addWidget(self.process_button)
        button_layout.addStretch()

        # 结果显示部分
        result_layout = QVBoxLayout()
        result_label = QLabel("结果:")
        result_label.setFont(QFont('华文仿宋', 12))

        self.result_display = QTextEdit()
        self.result_display.setFont(QFont('华文仿宋', 12))
        self.result_display.setReadOnly(True)
        self.result_display.setText(self.result)
        self.result_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)

        result_layout.addWidget(result_label)
        result_layout.addWidget(self.result_display)

        # 将所有部分添加到主布局
        main_layout.addLayout(input_layout)
        main_layout.addLayout(combo_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(result_layout)
        main_layout.addStretch()

        # 设置间距
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

    def on_button_click(self):
        In = self.input_box.text()
        option = self.combo_box.currentText()
        if option == "文生图":
            center.调用(1, In)
        elif option == "文生视频":
            center.调用(2, In)
        else:pass

        # 更新结果显示
        self.result_display.setText(
            f"数字: ")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle('Fusion')

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
