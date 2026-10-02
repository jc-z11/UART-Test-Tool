import sys
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QComboBox, QPushButton, QTextEdit,
                            QLabel)
from PyQt6.QtCore import QThread, pyqtSignal
import csv
from datetime import datetime

# ================= 多线程串口读取（看门狗机制） =================
class SerialWorker(QThread):
    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, port, baud):
        super().__init__()
        self.port = port
        self.baud = baud
        self.is_running = True
        self.ser = None

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
            while self.is_running:
                if self.ser.in_waiting:
                    data = self.ser.read_all().decode('utf-8', errors='ignore')
                    self.data_received.emit(data)
                self.msleep(50)
        except Exception as e:
            self.error_occurred.emit(f"串口错误: {str(e)}")
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()

    def stop(self):
        self.is_running = False
        self.wait()

# ================= 主界面 =================
class UARTMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UART Monitor - 工程化改造版")
        self.setGeometry(100, 100, 800, 600)
        
        self.serial_worker = None
        self.is_logging = False
        self.csv_file = None
        self.csv_writer = None
        
        # 数据缓冲区（解决粘包/断包）
        self.buffer = ""
        
        self.baud_rates = ['9600', '19200', '38400', '57600', '115200']
        self.init_ui()
        self.update_ports()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 顶部串口配置栏
        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.update_ports)
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        
        port_layout.addWidget(QLabel("Port:"))
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(self.refresh_button)
        port_layout.addWidget(self.connect_button)
        port_layout.addWidget(QLabel("Baud:"))
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(self.baud_rates)
        port_layout.addWidget(self.baud_combo)
        
        # 日志控制栏
        log_layout = QHBoxLayout()
        self.log_button = QPushButton("Start Logging")
        self.log_button.clicked.connect(self.toggle_logging)
        log_layout.addWidget(self.log_button)
        
        # 数据显示区
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        
        layout.addLayout(port_layout)
        layout.addLayout(log_layout)
        layout.addWidget(self.data_display)

    def update_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

    def toggle_connection(self):
        if self.serial_worker is None:
            port = self.port_combo.currentText()
            baud = int(self.baud_combo.currentText())
            
            self.serial_worker = SerialWorker(port, baud)
            self.serial_worker.data_received.connect(self.process_incoming_data)
            self.serial_worker.error_occurred.connect(self.handle_error)
            self.serial_worker.start()
            
            self.connect_button.setText("Disconnect")
            self.port_combo.setEnabled(False)
        else:
            self.serial_worker.stop()
            self.serial_worker = None
            self.connect_button.setText("Connect")
            self.port_combo.setEnabled(True)

    def process_incoming_data(self, raw_data):
        """处理粘包/断包"""
        self.buffer += raw_data
        lines = self.buffer.split('\n')
        self.buffer = lines[-1]
        
        for line in lines[:-1]:
            line = line.strip()
            if not line:
                continue
            
            self.data_display.append(line)
            self.parse_and_alert(line)
            
            if self.is_logging and self.csv_writer:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                self.csv_writer.writerow([timestamp, line])

    def parse_and_alert(self, data_str):
        """解析数据与阈值报警"""
        if "TEMP:" in data_str:
            try:
                temp_str = data_str.split("TEMP:")[1].strip()
                temp = float(temp_str)
                
                if temp > 30.0:
                    self.data_display.append("⚠️ 报警：温度过高！")
            except Exception:
                pass

    def handle_error(self, error_msg):
        """看门狗机制"""
        self.data_display.append(f"❌ {error_msg}")
        self.toggle_connection()

    def toggle_logging(self):
        if not self.is_logging:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"uart_log_{timestamp}.csv"
            self.csv_file = open(filename, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(['Timestamp', 'Data'])
            self.is_logging = True
            self.log_button.setText("Stop Logging")
        else:
            if self.csv_file:
                self.csv_file.close()
                self.csv_file = None
            self.is_logging = False
            self.log_button.setText("Start Logging")


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = UARTMonitor()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("程序崩溃，按回车键退出...")