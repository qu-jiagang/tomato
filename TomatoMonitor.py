import sys
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
from Monitors import NetworkMonitor
from TrayIcon import TrayIcon


class FloatingWindow(QMainWindow):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.show_info = ["network"]
        self.monitor = {"network": NetworkMonitor()}
        self.old_pos = QPoint()         # 用于拖动窗口记录鼠标位置

        self.init_tray_icon()           # 初始化托盘图标
        self.init_ui()                  # 初始化窗口
        self.init_timer()               # 初始化定时器

    def init_ui(self):
        """设置窗口外观和布局"""
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.update_ui()
        self.tray_icon.menu.actions()[0].setChecked(True)

    def update_ui(self):
        """更新窗口的显示内容"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()  # 删除控件
            elif item.layout():
                self.clear_layout(item.layout())  # 递归清除嵌套布局

        for info in self.show_info:
            if info == "network":
                self.upload_speed_label = self.create_label("resources/icons/upload.png", "0.0 KB/s")
                self.download_speed_label = self.create_label("resources/icons/download.png", "0.0 KB/s")
            elif info == "memory":
                self.memory_usage_label = self.create_label("resources/icons/ram.png", "0.0 %", icon_size=(32, 24))
            elif info == "cpu":
                self.cpu_usage_label = self.create_label("resources/icons/cpu.png", "0.0 %", icon_size=(60, 24))
            elif info == "gpu":
                self.gpu_usage_label = self.create_label("resources/icons/gpu.png", "0.0 %", icon_size=(60, 24))
            elif info == "disk":
                self.disk_read_label = self.create_label("resources/icons/disk_read.png", "0.0 kb/s", icon_size=(60, 24))
                self.disk_write_label = self.create_label("resources/icons/disk_write.png", "0.0 kb/s", icon_size=(60, 24))
        self.adjustSize()

    def clear_layout(self, layout):
        """递归清除布局中的所有子控件和子布局"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()  # 删除控件
            elif item.layout():
                self.clear_layout(item.layout())  # 递归清除嵌套布局
        layout.deleteLater()  # 删除布局本身

    def create_label(self, icon_path, default_text, icon_size=(24, 24)):
        """创建用于显示网速的图标和文本标签"""
        layout = QHBoxLayout()

        # 图标
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(*icon_size))

        # 速度文本
        text_label = QLabel(default_text)
        text_label.setFont(QFont("Arial", 12))
        text_label.setStyleSheet("""
            color: white;
            background-color: rgba(0, 0, 0, 160);
            border-radius: 5px;
            padding: 0px 5px;
        """)

        layout.addWidget(icon_label, alignment=Qt.AlignVCenter, stretch=0)
        layout.addWidget(text_label, alignment=Qt.AlignVCenter, stretch=1)

        # 添加到主布局
        self.layout.addLayout(layout)
        return text_label

    def init_timer(self):
        """初始化定时器，用于定时更新网速"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # 每秒更新一次
   
    def init_tray_icon(self):
        """初始化托盘图标"""
        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()

    def update_data(self):
        for info in self.show_info:
            if info == "network":
                upload_speed, download_speed = self.monitor[info].get_data()
                self.upload_speed_label.setText(self.monitor[info].format_data(upload_speed))
                self.download_speed_label.setText(self.monitor[info].format_data(download_speed))
            elif info == "memory":
                memory_usage, memory_total = self.monitor[info].get_data()
                self.memory_usage_label.setText(
                    f"{self.monitor[info].format_data(memory_usage)} / {self.monitor[info].format_data(memory_total)}"
                )
            elif info == "cpu":
                cpu_usage = self.monitor[info].get_data()
                self.cpu_usage_label.setText(self.monitor[info].format_data(cpu_usage))
            elif info == "gpu":
                gpu_data = self.monitor[info].get_data()
                self.gpu_usage_label.setText(self.monitor[info].format_data(gpu_data))
            elif info == "disk":
                disk_data = self.monitor[info].get_data()
                read_speed, write_speed = disk_data
                self.disk_read_label.setText(self.monitor[info].format_data(read_speed))
                self.disk_write_label.setText(self.monitor[info].format_data(write_speed))

    def mousePressEvent(self, event):
        """记录鼠标按下的位置"""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
        elif event.button() == Qt.RightButton:
            self.tray_icon.contextMenu().exec_(event.globalPos())

    def mouseMoveEvent(self, event):
        """实现窗口拖动"""
        if event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseDoubleClickEvent(self, event):
        """双击关闭窗口"""
        if event.button() == Qt.LeftButton:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用程序图标（任务栏图标和托盘图标）
    app.setWindowIcon(QIcon("resources/icons/icon.png"))

    # 创建主窗口
    window = FloatingWindow()
    window.show()

    sys.exit(app.exec_())