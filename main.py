import sys
import psutil
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QSystemTrayIcon, QMenu, QAction, QVBoxLayout, QHBoxLayout, QWidget
import pynvml


class NetworkMonitor:
    """负责网络速度的监控和计算"""
    def __init__(self):
        self.last_upload = 0
        self.last_download = 0
        self.update_last_data()

    def update_last_data(self):
        """更新网络的初始值"""
        data = psutil.net_io_counters()
        self.last_upload = data.bytes_sent
        self.last_download = data.bytes_recv

    def get_data(self):
        """计算当前的上传和下载速度"""
        current_data = psutil.net_io_counters()
        upload_speed = current_data.bytes_sent - self.last_upload
        download_speed = current_data.bytes_recv - self.last_download

        # 更新上一次的数据
        self.last_upload = current_data.bytes_sent
        self.last_download = current_data.bytes_recv

        return upload_speed, download_speed

    @staticmethod
    def format_data(speed):
        """格式化速度为人类可读形式"""
        if speed < 1024 ** 2:
            return f"{speed / 1024:.1f} KB/s"
        else:
            return f"{speed / 1024 ** 2:.1f} MB/s"


class CPUUsageMonitor:
    """负责CPU利用率的监控和计算"""
    def __init__(self):
        self.last_cpu_time = psutil.cpu_times()

    def get_data(self):
        """计算当前的CPU利用率"""
        current_cpu_time = psutil.cpu_times()
        total_time = sum(current_cpu_time) - sum(self.last_cpu_time)
        idle_time = current_cpu_time.idle - self.last_cpu_time.idle

        # 更新上一次的数据
        self.last_cpu_time = current_cpu_time

        return (total_time - idle_time) / total_time * 100

    @staticmethod
    def format_data(usage):
        """格式化CPU利用率为百分数"""
        return f"{usage:.1f}%"


class GPUUsageMonitor:
    """负责GPU利用率的监控和计算"""
    def __init__(self):
        # 初始化 pynvml 库
        try:
            pynvml.nvmlInit()
            self.device_count = pynvml.nvmlDeviceGetCount()  # 获取 GPU 的数量
        except pynvml.NVMLError as e:
            print(f"Failed to initialize NVML: {e.value}")
            self.device_count = 0

    def get_data(self):
        """获取所有 GPU 的利用率数据"""
        gpu_data = []
        for i in range(self.device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)  # 获取 GPU 句柄
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)  # 获取利用率
            gpu_data.append({
                "gpu_id": i,
                "gpu_utilization": utilization.gpu,  # GPU 核心利用率（整数，单位是百分比）
                "memory_utilization": utilization.memory,  # 显存利用率（整数，单位是百分比）
            })
        return gpu_data

    @staticmethod
    def format_data(gpu_data):
        """格式化 GPU 利用率数据为字符串"""
        formatted_data = []
        for gpu in gpu_data:
            formatted_data.append(
                f"GPU {gpu['gpu_id']}: Usage {gpu['gpu_utilization']}%, Memory {gpu['memory_utilization']}%"
            )
        if not formatted_data:
            return "No Nvidia GPU found"
        return "\n".join(formatted_data)


class TrayIcon(QSystemTrayIcon):
    """负责托盘图标功能"""
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window

        # 设置托盘图标
        self.setIcon(QIcon("figures/icon.png"))

        # 构建托盘菜单
        self.menu = QMenu()
        self.create_actions()
        self.setContextMenu(self.menu)

        # 连接托盘图标单击事件
        self.activated.connect(self.on_tray_icon_clicked)

    def create_actions(self):
        """创建托盘菜单项"""
        network_action = QAction("网络", self)
        network_action.triggered.connect(lambda: setattr(self.parent_window, 'show_info', 'network'))
        network_action.triggered.connect(lambda: setattr(self.parent_window, 'monitor', NetworkMonitor()))
        network_action.triggered.connect(self.parent_window.update_ui)
        self.menu.addAction(network_action)

        cpu_action = QAction("CPU", self)
        cpu_action.triggered.connect(lambda: setattr(self.parent_window, 'show_info', 'cpu'))
        cpu_action.triggered.connect(lambda: setattr(self.parent_window, 'monitor', CPUUsageMonitor()))
        cpu_action.triggered.connect(self.parent_window.update_ui)
        self.menu.addAction(cpu_action)

        gpu_action = QAction("GPU", self)
        gpu_action.triggered.connect(lambda: setattr(self.parent_window, 'show_info', 'gpu'))
        gpu_action.triggered.connect(lambda: setattr(self.parent_window, 'monitor', GPUUsageMonitor()))
        gpu_action.triggered.connect(self.parent_window.update_ui)
        self.menu.addAction(gpu_action)

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.quit)
        self.menu.addAction(quit_action)

    def on_tray_icon_clicked(self, reason):
        """处理托盘图标的点击事件"""
        if reason == QSystemTrayIcon.Trigger:  # 左键单击
            if self.parent_window.isVisible():
                self.parent_window.hide()
            else:
                self.parent_window.show()


class FloatingWindow(QMainWindow):
    """主窗口，显示网络速度"""
    def __init__(self):
        super().__init__()
        self.show_info = "network"
        self.monitor = NetworkMonitor() # 默认显示网络速度
        self.old_pos = QPoint()         # 用于拖动窗口记录鼠标位置

        self.init_ui()                  # 初始化窗口
        self.init_tray_icon()           # 初始化托盘图标
        self.init_timer()               # 初始化定时器

    def init_ui(self):
        """设置窗口外观和布局"""
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.update_ui()

    def update_ui(self):
        """更新窗口的显示内容"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()  # 删除控件
            elif item.layout():
                self.clear_layout(item.layout())  # 递归清除嵌套布局

        if self.show_info == "network":
            self.upload_speed_label = self.create_label("figures/upload.png", "0.0 KB/s")
            self.download_speed_label = self.create_label("figures/download.png", "0.0 KB/s")
        elif self.show_info == "cpu":
            self.cpu_usage_label = self.create_label("figures/cpu.png", "0.0 %", icon_size=(60, 24))
        elif self.show_info == "gpu":
            self.gpu_usage_label = self.create_label("figures/gpu.png", "0.0 %", icon_size=(60, 24))
            gpu_data = self.monitor.get_data()
            self.gpu_usage_label.setText(self.monitor.format_data(gpu_data))

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
        if self.show_info == "network":
            upload_speed, download_speed = self.monitor.get_data()
            self.upload_speed_label.setText(self.monitor.format_data(upload_speed))
            self.download_speed_label.setText(self.monitor.format_data(download_speed))
        elif self.show_info == "cpu":
            cpu_usage = self.monitor.get_data()
            self.cpu_usage_label.setText(self.monitor.format_data(cpu_usage))
        elif self.show_info == "gpu":
            gpu_data = self.monitor.get_data()
            self.gpu_usage_label.setText(self.monitor.format_data(gpu_data))

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
    app.setWindowIcon(QIcon("figures/icon.png"))

    # 创建主窗口
    window = FloatingWindow()
    window.show()

    sys.exit(app.exec_())