import sys
import serial
import serial.tools.list_ports
import subprocess
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QSlider, QLabel, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt

def get_resource_path(relative_path):
    """ 处理打包后的文件路径获取 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- 核心配置路径 ---
# 修改后的路径获取逻辑
def get_prog_path():
    # 优先寻找打包在内部的工具，如果没有则寻找同级目录下的 bin 文件夹
    internal_path = get_resource_path("bin/STM32_Programmer_CLI.exe")
    if os.path.exists(internal_path):
        return internal_path
    return os.path.join(os.path.abspath("."), "bin", "STM32_Programmer_CLI.exe")

CLI_PATH = get_prog_path()

class ServoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.ser = None
        self.hex_file = get_resource_path("servo_detection.hex")
        self.initUI()

    def initUI(self):
        self.setWindowTitle("STM32 舵机一键测试工具")
        self.setFixedWidth(400)
        layout = QVBoxLayout()

        # 1. 串口选择
        layout.addWidget(QLabel("1. 选择串口 (USB转TTL):"))
        self.port_combo = QComboBox()
        self.refresh_ports()
        layout.addWidget(self.port_combo)

        # 2. 烧录功能
        self.btn_burn = QPushButton("2. 一键烧录程序")
        self.btn_burn.setStyleSheet("background-color: #27ae60; color: white; height: 40px; font-weight: bold;")
        self.btn_burn.clicked.connect(self.burn_logic)
        layout.addWidget(self.btn_burn)

        layout.addWidget(QLabel("-" * 50))

        # 3. 控制功能
        self.btn_connect = QPushButton("3. 连接串口并开始控制")
        self.btn_connect.clicked.connect(self.toggle_serial)
        layout.addWidget(self.btn_connect)

        self.angle_label = QLabel("当前角度: 90°")
        self.angle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.angle_label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 180)
        self.slider.setValue(90)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.send_angle)
        layout.addWidget(self.slider)

        self.setLayout(layout)

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.port_combo.addItem(p.device)

    def burn_logic(self):
        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "错误", "请先选择串口")
            return

        if not os.path.exists(self.hex_file):
            QMessageBox.critical(self, "错误", f"找不到固件文件: {self.hex_file}")
            return

        # 构造烧录命令 (UART ISP模式)
        # 注意：烧录时 BOOT0 需要接 3.3V
        cmd = [CLI_PATH, "-c", f"port={port}", "br=115200", "-w", self.hex_file, "-v", "-rst"]

        try:
            QMessageBox.information(self, "操作指南", "请确保 BOOT0 已接 3.3V，并按一下 Reset 键，然后点击确定开始。")
            self.btn_burn.setText("正在烧录...")
            QApplication.processEvents()

            result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk',errors='ignore')

            if "File download complete" in result.stdout:
                QMessageBox.information(self, "成功", "烧录成功！\n请将 BOOT0 拨回 GND 并重新插拔电源，然后点击'连接'。")
            else:
                QMessageBox.critical(self, "失败", f"烧录输出:\n{result.stdout}\n错误信息:\n{result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
        finally:
            self.btn_burn.setText("2. 一键烧录程序")
            self.btn_burn.setEnabled(True)

    def toggle_serial(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.btn_connect.setText("3. 连接串口并开始控制")
            self.slider.setEnabled(False)
        else:
            try:
                self.ser = serial.Serial(self.port_combo.currentText(), 115200)
                self.btn_connect.setText("断开连接")
                self.slider.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开串口: {e}")

    def send_angle(self):
        angle = self.slider.value()
        self.angle_label.setText(f"当前角度: {angle}°")
        if self.ser and self.ser.is_open:
            self.ser.write(bytes([angle]))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServoApp()
    window.show()
    sys.exit(app.exec())